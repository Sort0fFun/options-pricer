/**
 * Formatting utility functions.
 */

const Formatter = {
    /**
     * Format number as currency (KES)
     */
    currency(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return 'KES 0.00';
        }
        return `KES ${parseFloat(value).toFixed(decimals)}`;
    },

    /**
     * Format number as percentage
     */
    percentage(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '0.00%';
        }
        return `${(parseFloat(value) * 100).toFixed(decimals)}%`;
    },

    /**
     * Format number with thousands separator
     */
    number(value, decimals = 2) {
        if (value === null || value === undefined || isNaN(value)) {
            return '0.00';
        }
        return parseFloat(value).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    /**
     * Format date/time
     */
    datetime(date, includeTime = true) {
        if (!date) return '';
        const d = new Date(date);
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }
        return d.toLocaleString('en-US', options);
    },

    /**
     * Format time only
     */
    time(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Truncate text
     */
    truncate(text, maxLength = 50) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Parse float safely
     */
    parseFloat(value, defaultValue = 0) {
        const parsed = parseFloat(value);
        return isNaN(parsed) ? defaultValue : parsed;
    },

    /**
     * Parse int safely
     */
    parseInt(value, defaultValue = 0) {
        const parsed = parseInt(value, 10);
        return isNaN(parsed) ? defaultValue : parsed;
    }
};

// Export for use in other modules
window.Formatter = Formatter;
