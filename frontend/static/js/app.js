/**
 * Main application controller.
 */

const App = {
    /**
     * Initialize the application
     */
    async init() {
        console.log('NSE Options Pricer - Initializing...');

        // Update market status
        await this.updateMarketStatus();

        // Set up market status refresh (every minute)
        setInterval(() => this.updateMarketStatus(), 60000);

        console.log('NSE Options Pricer - Ready');
    },

    /**
     * Update market status display
     */
    async updateMarketStatus() {
        try {
            const response = await API.market.getStatus();
            const statusElement = document.getElementById('market-status-text');
            const statusContainer = document.getElementById('market-status').querySelector('span');

            if (statusElement && response.data) {
                const { status, message } = response.data;
                statusElement.textContent = `${status}: ${message}`;

                // Update status badge styling
                if (statusContainer) {
                    statusContainer.classList.remove('market-status-open', 'market-status-closed');
                    if (status === 'OPEN') {
                        statusContainer.classList.add('market-status-open');
                    } else {
                        statusContainer.classList.add('market-status-closed');
                    }
                }
            }
        } catch (error) {
            console.error('Failed to update market status:', error);
            const statusElement = document.getElementById('market-status-text');
            if (statusElement) {
                statusElement.textContent = 'Status unavailable';
            }
        }
    },

    /**
     * Show loading spinner
     */
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="flex justify-center items-center py-8"><div class="spinner"></div></div>';
        }
    },

    /**
     * Show error message
     */
    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded relative" role="alert">
                    <strong class="font-bold">Error: </strong>
                    <span class="block sm:inline">${message}</span>
                </div>
            `;
        }
    },

    /**
     * Show success message
     */
    showSuccess(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="bg-green-100 dark:bg-green-900/20 border border-green-400 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded relative" role="alert">
                    <span class="block sm:inline">${message}</span>
                </div>
            `;
        }
    },

    /**
     * Debounce function for input handlers
     */
    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

// Export for use in other modules
window.App = App;
