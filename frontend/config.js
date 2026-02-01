// Default configuration
// This file can be updated before deployment or configured via the UI

const DEFAULT_CONFIG = {
    // API Gateway endpoint (update after Terraform deploy)
    apiUrl: 'https://8n22qcrph9.execute-api.us-east-1.amazonaws.com',
    
    // Default pipeline name (can be overridden in UI)
    defaultPipelineName: '',
    
    // Default time range in hours
    defaultHoursBack: 24,
    
    // UI settings
    theme: {
        primaryColor: '#2563eb',
        enableDarkMode: false
    },
    
    // Feature flags
    features: {
        enableQuickActions: true,
        enableSettings: true,
        enableHistory: false
    }
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DEFAULT_CONFIG;
}
