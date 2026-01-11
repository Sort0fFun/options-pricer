/**
 * API client for making requests to the Flask backend.
 */

const API = {
    baseURL: '/api',

    /**
     * Generic fetch wrapper
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const { headers: optionHeaders, ...restOptions } = options;
        const config = {
            ...restOptions,
            headers: {
                'Content-Type': 'application/json',
                ...optionHeaders
            }
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    },

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Authenticated request wrapper
     */
    async authRequest(endpoint, options = {}) {
        const token = localStorage.getItem('auth_access_token');
        if (!token) {
            throw new Error('Not authenticated');
        }

        const authHeaders = {
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };

        return this.request(endpoint, { ...options, headers: authHeaders });
    },

    /**
     * Authenticated GET request
     */
    async authGet(endpoint) {
        return this.authRequest(endpoint, { method: 'GET' });
    },

    /**
     * Authenticated POST request
     */
    async authPost(endpoint, data) {
        return this.authRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * Authenticated PUT request
     */
    async authPut(endpoint, data) {
        return this.authRequest(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * Authenticated DELETE request
     */
    async authDelete(endpoint) {
        return this.authRequest(endpoint, { method: 'DELETE' });
    },

    // Pricing API
    pricing: {
        async calculate(params) {
            return API.post('/pricing/calculate', params);
        },

        async heatmap(params) {
            return API.post('/pricing/heatmap', params);
        },

        async getContracts() {
            return API.get('/pricing/contracts');
        }
    },

    // Market API
    market: {
        async getStatus() {
            return API.get('/market/status');
        },

        async getFutures(filters = {}) {
            const params = new URLSearchParams(filters);
            const query = params.toString() ? `?${params.toString()}` : '';
            return API.get(`/market/futures${query}`);
        }
    },

    // Chat API
    chat: {
        async sendMessage(message, context = {}) {
            return API.authPost('/chat/message', { message, context });
        },

        async getSuggestions() {
            return API.get('/chat/suggestions');
        },

        async getTokenStatus() {
            return API.authGet('/chat/token-status');
        },

        async clear() {
            return API.authPost('/chat/clear', {});
        }
    },

    // PnL API
    pnl: {
        async analyze(strategy, marketParams) {
            return API.post('/pnl/analyze', { strategy, market_params: marketParams });
        },

        async buildStrategy(strategyName, parameters) {
            return API.post('/pnl/strategy-builder', {
                strategy_name: strategyName,
                parameters
            });
        },

        async getStrategies() {
            return API.get('/pnl/strategies');
        }
    },

    // Auth API
    auth: {
        async register(email, password, name) {
            return API.post('/auth/register', { email, password, name });
        },

        async login(email, password) {
            return API.post('/auth/login', { email, password });
        },

        async refresh() {
            const refreshToken = localStorage.getItem('auth_refresh_token');
            if (!refreshToken) {
                throw new Error('No refresh token');
            }
            return API.request('/auth/refresh', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`
                }
            });
        },

        async getProfile() {
            return API.authGet('/auth/profile');
        },

        async updateProfile(updates) {
            return API.authPut('/auth/profile', updates);
        },

        async updatePreferences(preferences) {
            return API.authPut('/auth/preferences', preferences);
        },

        async deleteAccount() {
            return API.authDelete('/auth/profile');
        },

        async verify() {
            return API.authGet('/auth/verify');
        }
    }
};

// Export for use in other modules
window.API = API;
