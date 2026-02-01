// Enhanced Operations Agent Frontend
// Configuration - loads from localStorage or uses defaults
const DEFAULT_API_URL = 'https://8n22qcrph9.execute-api.us-east-1.amazonaws.com';

const CONFIG = {
    apiUrl: localStorage.getItem('apiUrl') || DEFAULT_API_URL,
    pipelineName: localStorage.getItem('pipelineName') || '',
    hoursBack: parseInt(localStorage.getItem('hoursBack')) || 24,
    darkMode: localStorage.getItem('darkMode') === 'true'
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const settingsButton = document.getElementById('settingsButton');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('closeSidebar');
const saveConfig = document.getElementById('saveConfig');
const quickActionButtons = document.querySelectorAll('.quick-action-btn');
const darkModeToggle = document.getElementById('darkModeToggle');

// State
let isTyping = false;
let conversationHistory = JSON.parse(localStorage.getItem('conversationHistory') || '[]');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    setupEventListeners();
    applyDarkMode();
    loadConversationHistory();
    chatInput.focus();
});

function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    chatInput.addEventListener('input', () => {
        sendButton.disabled = !chatInput.value.trim();
    });

    settingsButton.addEventListener('click', () => {
        sidebar.classList.add('open');
    });

    closeSidebar.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });

    saveConfig.addEventListener('click', saveConfiguration);
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', toggleDarkMode);
    }

    quickActionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handleQuickAction(action);
        });
    });
}

function loadConfig() {
    document.getElementById('apiUrl').value = CONFIG.apiUrl;
    document.getElementById('pipelineName').value = CONFIG.pipelineName;
    document.getElementById('hoursBack').value = CONFIG.hoursBack;
    if (darkModeToggle) {
        darkModeToggle.checked = CONFIG.darkMode;
    }
}

function saveConfiguration() {
    CONFIG.apiUrl = document.getElementById('apiUrl').value.trim();
    CONFIG.pipelineName = document.getElementById('pipelineName').value.trim();
    CONFIG.hoursBack = parseInt(document.getElementById('hoursBack').value) || 24;

    localStorage.setItem('apiUrl', CONFIG.apiUrl);
    localStorage.setItem('pipelineName', CONFIG.pipelineName);
    localStorage.setItem('hoursBack', CONFIG.hoursBack);

    showMessage('Configuration saved!', 'success');
    sidebar.classList.remove('open');
}

function toggleDarkMode() {
    CONFIG.darkMode = darkModeToggle.checked;
    localStorage.setItem('darkMode', CONFIG.darkMode);
    applyDarkMode();
}

function applyDarkMode() {
    document.body.classList.toggle('dark-mode', CONFIG.darkMode);
}

function handleQuickAction(action) {
    let message = '';
    
    switch(action) {
        case 'analyze':
            if (CONFIG.pipelineName) {
                message = `Analyze pipeline ${CONFIG.pipelineName}`;
            } else {
                message = 'Analyze pipeline';
            }
            break;
        case 'logs':
            if (CONFIG.pipelineName) {
                message = `Check logs for ${CONFIG.pipelineName}`;
            } else {
                message = 'Check logs';
            }
            break;
        case 'errors':
            message = 'Show recent errors';
            break;
    }
    
    chatInput.value = message;
    sendMessage();
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isTyping) return;

    // Add user message to chat
    addMessage(message, 'user');
    chatInput.value = '';
    sendButton.disabled = true;
    isTyping = true;

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        // Parse message to extract pipeline name if not in config
        let pipelineName = CONFIG.pipelineName;
        const messageLower = message.toLowerCase();
        
        if (messageLower.includes('pipeline')) {
            const words = message.split(/\s+/);
            const pipelineIndex = words.findIndex(w => w.toLowerCase() === 'pipeline');
            if (pipelineIndex >= 0 && pipelineIndex + 1 < words.length) {
                pipelineName = words[pipelineIndex + 1].replace(/[.,!?]/g, '');
            }
        }

        // Prepare request
        const requestBody = {
            message: message,
            pipeline_name: pipelineName || '',
            hours_back: CONFIG.hoursBack
        };

        const apiUrl = `${CONFIG.apiUrl}/chat`;
        console.log('Calling API:', apiUrl);
        console.log('Request body:', requestBody);

        // Call API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody),
            mode: 'cors'
        }).catch(error => {
            console.error('Fetch error:', error);
            throw new Error(`Network error: ${error.message}. Check if API URL is correct and CORS is configured.`);
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API error:', response.status, errorText);
            throw new Error(`API error (${response.status}): ${errorText || response.statusText}`);
        }

        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        addMessage(data.response, 'bot');
        
        // Save to history
        saveToHistory(message, data.response, data.conversation_id);

    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        
        let errorMessage = `Error: ${error.message}`;
        
        if (error.message.includes('Network error') || error.message.includes('Failed to fetch')) {
            errorMessage += '\n\nPossible solutions:\n';
            errorMessage += '• Check if API URL is correct in settings (⚙️)\n';
            errorMessage += '• Verify API endpoint is accessible\n';
            errorMessage += '• Check browser console for CORS errors';
        }
        
        addMessage(errorMessage, 'bot');
    } finally {
        sendButton.disabled = false;
        isTyping = false;
        chatInput.focus();
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${sender === 'user' ? 'You' : 'Agent'}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${formatMessage(text)}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // Animate in
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.id = `typing-${Date.now()}`;
    
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">Agent</span>
                <span class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <div class="message-text">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    
    return typingDiv.id;
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

function formatMessage(text) {
    // Format markdown-like syntax
    let formatted = text;
    
    // Format numbered sections (1) Summary, 2) Evidence, etc.
    formatted = formatted.replace(/^(\d+\))\s+(.+)$/gm, '<strong class="section-header">$1 $2</strong>');
    
    // Format bullet points
    formatted = formatted.replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>');
    
    // Wrap lists
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Format code blocks
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Format bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Format links
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Preserve line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

function scrollToBottom() {
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function saveToHistory(userMessage, agentResponse, conversationId) {
    conversationHistory.push({
        timestamp: new Date().toISOString(),
        userMessage,
        agentResponse,
        conversationId
    });
    
    // Keep only last 50 messages
    if (conversationHistory.length > 50) {
        conversationHistory = conversationHistory.slice(-50);
    }
    
    localStorage.setItem('conversationHistory', JSON.stringify(conversationHistory));
}

function loadConversationHistory() {
    // Optionally load recent history
    // For now, we start fresh each session
}

function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message notification`;
    messageDiv.textContent = text;
    
    const sidebarContent = document.querySelector('.sidebar-content');
    if (sidebarContent) {
        sidebarContent.insertBefore(messageDiv, sidebarContent.firstChild);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}
