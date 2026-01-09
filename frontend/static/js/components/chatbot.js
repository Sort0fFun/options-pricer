/**
 * Chatbot component - Flavia AI interface.
 */

const Chatbot = {
    history: [],

    /**
     * Initialize chatbot
     */
    async init() {
        console.log('Initializing Flavia AI...');

        // Load chat history from localStorage
        this.loadHistory();

        // Load suggestions
        await this.loadSuggestions();

        // Setup event listeners
        this.setupEventListeners();

        // Render existing messages
        this.renderMessages();
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const clearBtn = document.getElementById('clear-btn');
        const exportBtn = document.getElementById('export-btn');

        // Send button
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Enter key to send
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
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
     * Send message to Flavia AI
     */
    async sendMessage(message = null) {
        const input = document.getElementById('chat-input');
        const userMessage = message || input.value.trim();

        if (!userMessage) return;

        // Clear input
        if (input) input.value = '';

        // Add user message to history
        this.addMessage('user', userMessage);

        // Show loading
        const loadingId = this.addMessage('assistant', '...', true);

        try {
            // Send to API
            const response = await API.chat.sendMessage(userMessage);

            // Remove loading message
            this.removeMessage(loadingId);

            if (response.success && response.data) {
                this.addMessage('assistant', response.data.response);
            } else {
                this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            // Remove loading message
            this.removeMessage(loadingId);
            this.addMessage('assistant', `Error: ${error.message || 'Failed to get response'}`);
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

        if (messages.length === 0 && !tempMessages) {
            container.innerHTML = `
                <div class="text-center text-gray-500 dark:text-gray-400 py-8">
                    <p>Welcome! I'm Flavia AI, your options trading assistant.</p>
                    <p class="text-sm mt-2">Ask me a question or click a suggestion to get started.</p>
                </div>
            `;
            return;
        }

        // If temp messages, just append them
        if (tempMessages) {
            tempMessages.forEach(msg => {
                const messageHTML = this.createMessageHTML(msg);
                container.insertAdjacentHTML('beforeend', messageHTML);
            });
        } else {
            // Render all messages
            const messagesHTML = messages.map(msg => this.createMessageHTML(msg)).join('');
            container.innerHTML = messagesHTML;
        }

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    },

    /**
     * Create message HTML
     */
    createMessageHTML(message) {
        const isUser = message.role === 'user';
        const bubbleClass = isUser ? 'chat-bubble-user' : 'chat-bubble-assistant';
        const messageClass = isUser ? 'chat-message-user' : '';

        return `
            <div class="chat-message ${messageClass}" data-message-id="${message.id}">
                <div class="chat-bubble ${bubbleClass}">
                    ${message.isLoading ? '<div class="spinner w-4 h-4"></div>' : `
                        <div class="text-sm">${this.formatMessage(message.content)}</div>
                        <div class="chat-bubble-timestamp">${Formatter.time(message.timestamp)}</div>
                    `}
                </div>
            </div>
        `;
    },

    /**
     * Format message content (handle line breaks, links, etc.)
     */
    formatMessage(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
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
