// Configuration - loads from localStorage or uses defaults
const DEFAULT_API_URL = 'https://8n22qcrph9.execute-api.us-east-1.amazonaws.com';

const CONFIG = {
    apiUrl: localStorage.getItem('apiUrl') || DEFAULT_API_URL,
    pipelineName: localStorage.getItem('pipelineName') || '',
    hoursBack: parseInt(localStorage.getItem('hoursBack')) || 24
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    setupEventListeners();
    updateMessageTimes();
});

function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    settingsButton.addEventListener('click', () => {
        sidebar.classList.add('open');
    });

    closeSidebar.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });

    saveConfig.addEventListener('click', saveConfiguration);

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
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    chatInput.value = '';
    sendButton.disabled = true;

    // Show loading
    const loadingId = addMessage('Analyzing...', 'bot', true);

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
            // Handle network errors
            console.error('Fetch error:', error);
            throw new Error(`Network error: ${error.message}. Check if API URL is correct and CORS is configured.`);
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('API error:', response.status, errorText);
            throw new Error(`API error (${response.status}): ${errorText || response.statusText}`);
        }

        const data = await response.json();
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add bot response
        addMessage(data.response, 'bot');
        
        // Update conversation ID if provided
        if (data.conversation_id) {
            console.log('Conversation ID:', data.conversation_id);
        }

    } catch (error) {
        console.error('Error:', error);
        removeMessage(loadingId);
        
        let errorMessage = `Error: ${error.message}`;
        
        // Provide helpful suggestions based on error type
        if (error.message.includes('Network error') || error.message.includes('Failed to fetch')) {
            errorMessage += '\n\nPossible solutions:\n';
            errorMessage += '• Check if API URL is correct in settings (⚙️)\n';
            errorMessage += '• Verify API endpoint: https://8n22qcrph9.execute-api.us-east-1.amazonaws.com\n';
            errorMessage += '• Check browser console for CORS errors\n';
            errorMessage += '• Ensure API Gateway CORS is configured';
        } else if (error.message.includes('API error')) {
            errorMessage += '\n\nCheck:\n';
            errorMessage += '• Lambda function logs\n';
            errorMessage += '• API Gateway configuration\n';
            errorMessage += '• Request format is correct';
        }
        
        addMessage(errorMessage, 'bot');
    } finally {
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function addMessage(text, sender, isLoading = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    if (isLoading) {
        messageDiv.id = `loading-${Date.now()}`;
    }

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
            <div class="message-text">
                ${isLoading ? '<span class="loading"></span>' : formatMessage(text)}
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv.id;
}

function removeMessage(id) {
    const message = document.getElementById(id);
    if (message) {
        message.remove();
    }
}

function formatMessage(text) {
    // Format the structured response
    let formatted = text;
    
    // Format numbered sections
    formatted = formatted.replace(/^(\d+\))\s+(.+)$/gm, '<strong>$1 $2</strong>');
    
    // Format bullet points
    formatted = formatted.replace(/^-\s+(.+)$/gm, '• $1');
    
    // Preserve line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

function updateMessageTimes() {
    const times = document.querySelectorAll('.message-time');
    times.forEach(timeEl => {
        // Times are already set when messages are added
    });
}

function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    messageDiv.textContent = text;
    
    const sidebarContent = document.querySelector('.sidebar-content');
    sidebarContent.insertBefore(messageDiv, sidebarContent.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}
