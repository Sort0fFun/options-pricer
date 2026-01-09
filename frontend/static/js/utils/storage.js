/**
 * LocalStorage utility for managing app state persistence.
 */

const Storage = {
    /**
     * Get item from localStorage
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error(`Error reading from localStorage (${key}):`, error);
            return defaultValue;
        }
    },

    /**
     * Set item in localStorage
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error(`Error writing to localStorage (${key}):`, error);
        }
    },

    /**
     * Remove item from localStorage
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error(`Error removing from localStorage (${key}):`, error);
        }
    },

    /**
     * Clear all localStorage
     */
    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
    },

    // Specific storage keys
    KEYS: {
        THEME: 'nse_theme',
        CHAT_HISTORY: 'nse_chat_history',
        CALCULATOR_INPUTS: 'nse_calculator_inputs',
        PNL_LEGS: 'nse_pnl_legs',
        SETTINGS: 'nse_settings'
    }
};

// Export for use in other modules
window.Storage = Storage;
