/**
 * Main application controller.
 */

const App = {
    /**
     * Initialize the application
     */
    async init() {
        console.log('NSE Options Pricer - Initializing...');

        // Setup mobile menu toggle
        this.setupMobileMenu();

        // Update market status
        await this.updateMarketStatus();

        // Set up market status refresh (every minute)
        setInterval(() => this.updateMarketStatus(), 60000);

        console.log('NSE Options Pricer - Ready');
    },

    /**
     * Setup mobile menu toggle
     */
    setupMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');

        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    },

    /**
     * Update market status display
     */
    async updateMarketStatus() {
        try {
            const response = await API.market.getStatus();
            const statusElement = document.getElementById('market-status-text');
            const statusBadge = document.getElementById('market-status-badge');

            if (statusElement && response.data) {
                const { status, message } = response.data;
                statusElement.textContent = `${status}: ${message}`;

                // Update badge styling based on market status
                if (statusBadge) {
                    statusBadge.classList.remove(
                        'bg-green-500/20', 'text-green-200',
                        'bg-red-500/20', 'text-red-200',
                        'bg-yellow-500/20', 'text-yellow-200'
                    );
                    
                    if (status === 'OPEN') {
                        statusBadge.classList.add('bg-green-500/20', 'text-green-200');
                    } else {
                        statusBadge.classList.add('bg-red-500/20', 'text-red-200');
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
