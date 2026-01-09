/**
 * Theme management utility for dark/light mode.
 */

const ThemeManager = {
    /**
     * Initialize theme on page load
     */
    init() {
        const savedTheme = Storage.get(Storage.KEYS.THEME, 'light');
        this.setTheme(savedTheme);
        this.setupToggle();
    },

    /**
     * Set theme
     */
    setTheme(theme) {
        const html = document.documentElement;
        const iconDark = document.getElementById('theme-icon-dark');
        const iconLight = document.getElementById('theme-icon-light');

        if (theme === 'dark') {
            html.classList.add('dark');
            if (iconDark) iconDark.classList.remove('hidden');
            if (iconLight) iconLight.classList.add('hidden');
        } else {
            html.classList.remove('dark');
            if (iconDark) iconDark.classList.add('hidden');
            if (iconLight) iconLight.classList.remove('hidden');
        }

        Storage.set(Storage.KEYS.THEME, theme);
    },

    /**
     * Toggle theme
     */
    toggle() {
        const currentTheme = Storage.get(Storage.KEYS.THEME, 'light');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return Storage.get(Storage.KEYS.THEME, 'light');
    },

    /**
     * Setup theme toggle button
     */
    setupToggle() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }
};

// Initialize theme when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}

// Export for use in other modules
window.ThemeManager = ThemeManager;
