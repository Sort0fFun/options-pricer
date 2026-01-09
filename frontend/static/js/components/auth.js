/**
 * Authentication client for managing user sessions.
 */

const Auth = {
    // Storage keys
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'auth_access_token',
        REFRESH_TOKEN: 'auth_refresh_token',
        USER: 'auth_user'
    },

    /**
     * Register a new user
     */
    async register(email, password, name) {
        try {
            const response = await API.post('/auth/register', {
                email,
                password,
                name
            });

            if (response.success) {
                this.saveSession(response.data.tokens, response.data.user);
            }

            return response;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Registration failed'
            };
        }
    },

    /**
     * Login user
     */
    async login(email, password) {
        try {
            const response = await API.post('/auth/login', {
                email,
                password
            });

            if (response.success) {
                this.saveSession(response.data.tokens, response.data.user);
            }

            return response;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Login failed'
            };
        }
    },

    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem(this.STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(this.STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(this.STORAGE_KEYS.USER);
        this.updateNavUI();
    },

    /**
     * Get current user's profile
     */
    async getProfile() {
        try {
            const response = await API.authGet('/auth/profile');
            
            if (response.success) {
                // Update stored user data
                localStorage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(response.data));
            }

            return response;
        } catch (error) {
            // If unauthorized, clear session
            if (error.message.includes('401') || error.message.includes('expired')) {
                this.logout();
            }
            return {
                success: false,
                message: error.message || 'Failed to get profile'
            };
        }
    },

    /**
     * Update user profile
     */
    async updateProfile(updates) {
        try {
            const response = await API.authPut('/auth/profile', updates);
            
            if (response.success) {
                // Update stored user data
                localStorage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(response.data));
                this.updateNavUI();
            }

            return response;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Failed to update profile'
            };
        }
    },

    /**
     * Update user preferences
     */
    async updatePreferences(preferences) {
        try {
            const response = await API.authPut('/auth/preferences', preferences);
            return response;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Failed to update preferences'
            };
        }
    },

    /**
     * Delete user account
     */
    async deleteAccount() {
        try {
            const response = await API.authDelete('/auth/profile');
            return response;
        } catch (error) {
            return {
                success: false,
                message: error.message || 'Failed to delete account'
            };
        }
    },

    /**
     * Refresh access token
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${API.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            const data = await response.json();

            if (data.success) {
                localStorage.setItem(this.STORAGE_KEYS.ACCESS_TOKEN, data.data.access_token);
                return true;
            }

            return false;
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    },

    /**
     * Check if user is logged in
     */
    isLoggedIn() {
        return !!this.getAccessToken();
    },

    /**
     * Get access token
     */
    getAccessToken() {
        return localStorage.getItem(this.STORAGE_KEYS.ACCESS_TOKEN);
    },

    /**
     * Get refresh token
     */
    getRefreshToken() {
        return localStorage.getItem(this.STORAGE_KEYS.REFRESH_TOKEN);
    },

    /**
     * Get stored user data
     */
    getUser() {
        const userData = localStorage.getItem(this.STORAGE_KEYS.USER);
        return userData ? JSON.parse(userData) : null;
    },

    /**
     * Save session data
     */
    saveSession(tokens, user) {
        localStorage.setItem(this.STORAGE_KEYS.ACCESS_TOKEN, tokens.access_token);
        localStorage.setItem(this.STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh_token);
        localStorage.setItem(this.STORAGE_KEYS.USER, JSON.stringify(user));
        this.updateNavUI();
    },

    /**
     * Update navigation UI based on auth state
     */
    updateNavUI() {
        const guestLinks = document.getElementById('auth-links-guest');
        const userLinks = document.getElementById('auth-links-user');
        const mobileGuestLinks = document.getElementById('mobile-auth-guest');
        const mobileUserLinks = document.getElementById('mobile-auth-user');
        const navInitials = document.getElementById('nav-initials');
        const navUsername = document.getElementById('nav-username');

        if (this.isLoggedIn()) {
            const user = this.getUser();
            
            // Show user links, hide guest links
            if (guestLinks) guestLinks.classList.add('hidden');
            if (userLinks) userLinks.classList.remove('hidden');
            if (mobileGuestLinks) mobileGuestLinks.classList.add('hidden');
            if (mobileUserLinks) mobileUserLinks.classList.remove('hidden');
            
            // Update user info
            if (user) {
                const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
                if (navInitials) navInitials.textContent = initials;
                if (navUsername) navUsername.textContent = user.name.split(' ')[0];
            }
        } else {
            // Show guest links, hide user links
            if (guestLinks) guestLinks.classList.remove('hidden');
            if (userLinks) userLinks.classList.add('hidden');
            if (mobileGuestLinks) mobileGuestLinks.classList.remove('hidden');
            if (mobileUserLinks) mobileUserLinks.classList.add('hidden');
        }
    },

    /**
     * Initialize auth state on page load
     */
    init() {
        this.updateNavUI();

        // Setup logout buttons
        const navLogoutBtn = document.getElementById('nav-logout-btn');
        const mobileLogoutBtn = document.getElementById('mobile-logout-btn');

        if (navLogoutBtn) {
            navLogoutBtn.addEventListener('click', () => {
                this.logout();
                window.location.href = '/login';
            });
        }

        if (mobileLogoutBtn) {
            mobileLogoutBtn.addEventListener('click', () => {
                this.logout();
                window.location.href = '/login';
            });
        }

        // Verify token is still valid if logged in
        if (this.isLoggedIn()) {
            this.verifySession();
        }
    },

    /**
     * Verify current session is valid
     */
    async verifySession() {
        try {
            const response = await API.authGet('/auth/verify');
            if (!response.success) {
                // Try to refresh token
                const refreshed = await this.refreshToken();
                if (!refreshed) {
                    this.logout();
                }
            }
        } catch (error) {
            // Try to refresh token
            const refreshed = await this.refreshToken();
            if (!refreshed) {
                this.logout();
            }
        }
    }
};

// Initialize auth when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
});
