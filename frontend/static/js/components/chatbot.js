/**
 * Chatbot component - Flavia AI interface with token integration.
 */

const Chatbot = {
    history: [],
    tokenBalance: 0,
    isAuthenticated: false,

    /**
     * Initialize chatbot
     */
    async init() {
        console.log('Initializing Flavia AI...');

        // Check authentication
        const token = localStorage.getItem('auth_access_token');
        this.isAuthenticated = !!token;

        if (!this.isAuthenticated) {
            this.showLoginRequired();
            return;
        }

        // Load token status first (this also grants daily free tokens)
        await this.loadTokenStatus();

        // Load chat history from localStorage
        this.loadHistory();

        // Load suggestions
        await this.loadSuggestions();

        // Setup event listeners
        this.setupEventListeners();

        // Render existing messages
        this.renderMessages();

        // Setup auto-resize for textarea
        this.setupTextareaAutoResize();
    },

    /**
     * Show login required message
     */
    showLoginRequired() {
        const container = document.getElementById('chat-messages');
        if (container) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full py-12">
                    <div class="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                        <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Login Required</h3>
                    <p class="text-gray-600 dark:text-gray-400 text-center max-w-sm mb-6">
                        Please login to chat with Flavia AI and access your free daily tokens.
                    </p>
                    <a href="/login?redirect=/chatbot" class="px-6 py-3 bg-nse-primary text-white rounded-lg font-semibold hover:bg-nse-secondary transition-colors">
                        Login Now
                    </a>
                </div>
            `;
        }

        // Disable input
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        if (input) input.disabled = true;
        if (sendBtn) sendBtn.disabled = true;
    },

    /**
     * Load token status from server
     */
    async loadTokenStatus() {
        try {
            const response = await API.chat.getTokenStatus();
            
            if (response.success) {
                this.tokenBalance = response.tokens || 0;
                this.updateTokenUI(response);
                
                // Show notification if daily tokens were granted
                if (response.daily_tokens_granted > 0) {
                    this.showNotification(`🎉 You received ${response.daily_tokens_granted} free daily tokens!`, 'success');
                }
            }
        } catch (error) {
            console.error('Error loading token status:', error);
            // Try to continue with local balance
            this.tokenBalance = 0;
        }

        this.updateSendButtonState();
    },

    /**
     * Update token display in UI
     */
    updateTokenUI(data) {
        const balanceEl = document.getElementById('token-balance');
        const statusEl = document.getElementById('daily-tokens-status');
        const warningEl = document.getElementById('no-tokens-warning');

        if (balanceEl) {
            balanceEl.textContent = this.tokenBalance;
            // Add color based on balance
            balanceEl.classList.remove('text-red-400', 'text-yellow-400');
            if (this.tokenBalance === 0) {
                balanceEl.classList.add('text-red-400');
            } else if (this.tokenBalance <= 2) {
                balanceEl.classList.add('text-yellow-400');
            }
        }

        if (statusEl) {
            if (data.daily_tokens_available) {
                statusEl.innerHTML = `<span class="text-green-400">✓ Daily tokens available</span>`;
            } else {
                statusEl.innerHTML = `<span class="text-white/60">Daily tokens claimed</span>`;
            }
        }

        // Show/hide no tokens warning
        if (warningEl) {
            if (this.tokenBalance === 0) {
                warningEl.classList.remove('hidden');
            } else {
                warningEl.classList.add('hidden');
            }
        }
    },

    /**
     * Update send button state based on token balance
     */
    updateSendButtonState() {
        const sendBtn = document.getElementById('send-btn');
        const input = document.getElementById('chat-input');

        if (sendBtn) {
            sendBtn.disabled = this.tokenBalance < 1;
            if (this.tokenBalance < 1) {
                sendBtn.title = 'No tokens remaining. Please purchase more tokens.';
            } else {
                sendBtn.title = 'Send message (1 token)';
            }
        }

        if (input) {
            input.disabled = this.tokenBalance < 1;
            if (this.tokenBalance < 1) {
                input.placeholder = 'You need tokens to send messages. Click "Get Tokens" to continue.';
            } else {
                input.placeholder = 'Ask Flavia anything about options trading...';
            }
        }
    },

    /**
     * Setup textarea auto-resize
     */
    setupTextareaAutoResize() {
        const textarea = document.getElementById('chat-input');
        const charCount = document.getElementById('char-count');

        if (textarea) {
            textarea.addEventListener('input', () => {
                // Auto-resize
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
                
                // Update character count
                if (charCount) {
                    charCount.textContent = `${textarea.value.length}/2000`;
                }
            });
        }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        console.log('Binding chatbot events...');
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const clearBtn = document.getElementById('clear-btn');
        const exportBtn = document.getElementById('export-btn');

        // Send button
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Enter key to send (Shift+Enter for new line)
        if (input) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Clear button
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearConversation());
        }

        // Export button
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportConversation());
        }
    },

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        
        notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.remove('translate-x-full');
        });
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    },

    /**
     * Send message to Flavia AI
     */
    async sendMessage(message = null) {
        const input = document.getElementById('chat-input');
        const userMessage = message || (input ? input.value.trim() : '');

        if (!userMessage) return;

        // Check token balance
        if (this.tokenBalance < 1) {
            this.showNotification('No tokens remaining. Please purchase more tokens.', 'error');
            return;
        }

        // Clear input
        if (input) {
            input.value = '';
            input.style.height = 'auto';
            const charCount = document.getElementById('char-count');
            if (charCount) charCount.textContent = '0/2000';
        }

        // Hide welcome message
        const welcomeEl = document.getElementById('welcome-message');
        if (welcomeEl) welcomeEl.classList.add('hidden');

        // Add user message to history
        this.addMessage('user', userMessage);

        // Show loading
        const loadingId = this.addMessage('assistant', '', true);

        // Optimistically decrease token count
        this.tokenBalance--;
        this.updateTokenUI({ daily_tokens_available: false });
        this.updateSendButtonState();

        try {
            // Send to API
            const response = await API.chat.sendMessage(userMessage);

            // Remove loading message
            this.removeMessage(loadingId);

            if (response.success && response.data) {
                this.addMessage('assistant', response.data.response);
                
                // Update token balance from server response
                if (typeof response.tokens_remaining !== 'undefined') {
                    this.tokenBalance = response.tokens_remaining;
                    this.updateTokenUI({ daily_tokens_available: false });
                    this.updateSendButtonState();
                }
            } else {
                // Restore token if request failed
                this.tokenBalance++;
                this.updateTokenUI({ daily_tokens_available: false });
                this.updateSendButtonState();
                
                const errorMsg = response.error === 'insufficient_tokens' 
                    ? 'You have no tokens remaining. Please purchase more tokens to continue.'
                    : (response.message || 'Sorry, I encountered an error. Please try again.');
                this.addMessage('assistant', errorMsg);
            }
        } catch (error) {
            // Remove loading message
            this.removeMessage(loadingId);
            
            // Restore token on error
            this.tokenBalance++;
            this.updateTokenUI({ daily_tokens_available: false });
            this.updateSendButtonState();
            
            this.addMessage('assistant', `Error: ${error.message || 'Failed to get response. Please try again.'}`);
        }
    },

    /**
     * Add message to history
     */
    addMessage(role, content, isLoading = false) {
        const message = {
            id: Date.now() + Math.random(),
            role,
            content,
            timestamp: new Date().toISOString(),
            isLoading
        };

        if (!isLoading) {
            this.history.push(message);
            this.saveHistory();
        }

        this.renderMessages(isLoading ? [message] : null);

        return message.id;
    },

    /**
     * Remove message by ID (for loading messages)
     */
    removeMessage(messageId) {
        const container = document.getElementById('chat-messages');
        const messageEl = container.querySelector(`[data-message-id="${messageId}"]`);
        if (messageEl) {
            messageEl.remove();
        }
    },

    /**
     * Render messages
     */
    renderMessages(tempMessages = null) {
        const container = document.getElementById('chat-messages');
        if (!container) return;

        const messages = tempMessages || this.history;

        // Don't overwrite welcome message if no history
        if (messages.length === 0 && !tempMessages) {
            return; // Keep the HTML welcome message
        }

        // If temp messages, just append them
        if (tempMessages) {
            // Hide welcome message when starting conversation
            const welcomeEl = document.getElementById('welcome-message');
            if (welcomeEl) welcomeEl.classList.add('hidden');
            
            tempMessages.forEach(msg => {
                const messageHTML = this.createMessageHTML(msg);
                container.insertAdjacentHTML('beforeend', messageHTML);
            });
        } else {
            // Hide welcome message if we have history
            const welcomeEl = document.getElementById('welcome-message');
            if (welcomeEl && this.history.length > 0) {
                welcomeEl.classList.add('hidden');
            }
            
            // Render all messages after welcome
            const messagesHTML = messages.map(msg => this.createMessageHTML(msg)).join('');
            
            // Find welcome message and add after it, or replace content
            if (welcomeEl) {
                // Remove existing message elements (not welcome)
                container.querySelectorAll('.chat-message').forEach(el => el.remove());
                container.insertAdjacentHTML('beforeend', messagesHTML);
            } else {
                container.innerHTML = messagesHTML;
            }
        }

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    },

    /**
     * Create message HTML
     */
    createMessageHTML(message) {
        const isUser = message.role === 'user';
        
        if (isUser) {
            return `
                <div class="chat-message flex justify-end" data-message-id="${message.id}">
                    <div class="max-w-[80%] bg-gradient-to-r from-nse-primary to-nse-secondary text-white rounded-2xl rounded-tr-md px-4 py-3 shadow-md">
                        <div class="text-sm whitespace-pre-wrap">${this.escapeHtml(message.content)}</div>
                        <div class="text-xs text-white/70 mt-1 text-right">${this.formatTime(message.timestamp)}</div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="chat-message flex justify-start" data-message-id="${message.id}">
                    <div class="flex items-start gap-3 max-w-[80%]">
                        <div class="w-8 h-8 bg-gradient-to-br from-nse-primary to-nse-secondary rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                            <span class="text-white font-bold text-sm">F</span>
                        </div>
                        <div class="bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-2xl rounded-tl-md px-4 py-3 shadow-md border border-gray-100 dark:border-gray-600">
                            ${message.isLoading ? `
                                <div class="flex items-center gap-2">
                                    <div class="flex gap-1">
                                        <span class="w-2 h-2 bg-nse-primary rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                                        <span class="w-2 h-2 bg-nse-primary rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                                        <span class="w-2 h-2 bg-nse-primary rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                                    </div>
                                    <span class="text-sm text-gray-500">Thinking...</span>
                                </div>
                            ` : `
                                <div class="text-sm whitespace-pre-wrap prose prose-sm dark:prose-invert max-w-none">${this.formatMessage(message.content)}</div>
                                <div class="text-xs text-gray-400 mt-2">${this.formatTime(message.timestamp)}</div>
                            `}
                        </div>
                    </div>
                </div>
            `;
        }
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Format time
     */
    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },

    /**
     * Format message content (handle markdown-like formatting)
     */
    formatMessage(content) {
        if (!content) return '';
        
        // Escape HTML first
        let formatted = this.escapeHtml(content);
        
        // Headers: ### Header -> <h4>, ## Header -> <h3>, # Header -> <h2>
        formatted = formatted.replace(/^### (.+)$/gm, '<h4 class="font-bold text-base mt-4 mb-2 text-gray-900 dark:text-white">$1</h4>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h3 class="font-bold text-lg mt-4 mb-2 text-gray-900 dark:text-white">$1</h3>');
        formatted = formatted.replace(/^# (.+)$/gm, '<h2 class="font-bold text-xl mt-4 mb-2 text-gray-900 dark:text-white">$1</h2>');
        
        // Bold: **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
        // Italic: *text*
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Code blocks: ```code```
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg my-2 overflow-x-auto text-sm"><code>$1</code></pre>');
        // Inline code: `code`
        formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-600 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>');
        
        // Numbered lists: 1. item, 2. item (convert consecutive items to <ol>)
        formatted = formatted.replace(/^(\d+)\. (.+)$/gm, '<li class="ml-5 list-decimal">$2</li>');
        // Wrap consecutive <li> items in <ol>
        formatted = formatted.replace(/((?:<li class="ml-5 list-decimal">.*?<\/li>\n?)+)/g, '<ol class="my-2 space-y-1">$1</ol>');
        
        // Bullet lists: - item
        formatted = formatted.replace(/^- (.+)$/gm, '<li class="ml-5 list-disc">$1</li>');
        // Wrap consecutive bullet <li> items in <ul>
        formatted = formatted.replace(/((?:<li class="ml-5 list-disc">.*?<\/li>\n?)+)/g, '<ul class="my-2 space-y-1">$1</ul>');
        
        // Line breaks (but not inside lists or headers)
        formatted = formatted.replace(/\n/g, '<br>');
        // Clean up extra <br> after block elements
        formatted = formatted.replace(/<\/(h[234]|ol|ul|pre)><br>/g, '</$1>');
        formatted = formatted.replace(/<br><(h[234]|ol|ul|pre)/g, '<$1');
        
        return formatted;
    },

    /**
     * Load suggestions
     */
    async loadSuggestions() {
        try {
            const response = await API.chat.getSuggestions();

            if (response.success && response.data) {
                this.renderSuggestions(response.data.suggestions);
            }
        } catch (error) {
            console.error('Error loading suggestions:', error);
            const container = document.getElementById('suggestions-container');
            if (container) {
                container.innerHTML = '<p class="text-sm text-gray-500">Failed to load suggestions</p>';
            }
        }
    },

    /**
     * Render suggestions
     */
    renderSuggestions(suggestions) {
        const container = document.getElementById('suggestions-container');
        if (!container) return;

        const suggestionsHTML = suggestions.map((question, index) => `
            <button
                class="w-full text-left px-4 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-nse-accent dark:hover:bg-nse-dark rounded-lg text-sm text-gray-900 dark:text-white transition-colors"
                onclick="Chatbot.sendMessage('${question.replace(/'/g, "\\'")}')"
            >
                ${question}
            </button>
        `).join('');

        container.innerHTML = suggestionsHTML;
    },

    /**
     * Clear conversation
     */
    async clearConversation() {
        if (!confirm('Are you sure you want to clear the conversation?')) {
            return;
        }

        this.history = [];
        this.saveHistory();
        this.renderMessages();

        try {
            await API.chat.clear();
        } catch (error) {
            console.error('Error clearing server conversation:', error);
        }
    },

    /**
     * Export conversation to JSON
     */
    exportConversation() {
        if (this.history.length === 0) {
            alert('No conversation to export');
            return;
        }

        const data = {
            exported_at: new Date().toISOString(),
            messages: this.history
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `flavia-conversation-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    /**
     * Save history to localStorage
     */
    saveHistory() {
        Storage.set(Storage.KEYS.CHAT_HISTORY, this.history);
    },

    /**
     * Load history from localStorage
     */
    loadHistory() {
        const saved = Storage.get(Storage.KEYS.CHAT_HISTORY, []);
        this.history = saved;
    }
};

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Chatbot.init());
} else {
    Chatbot.init();
}

// Export for use in other modules
window.Chatbot = Chatbot;
