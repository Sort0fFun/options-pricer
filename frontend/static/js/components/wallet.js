/**
 * Wallet management and M-Pesa integration
 */

class WalletManager {
    constructor() {
        this.currentPage = 1;
        this.totalPages = 1;
        this.selectedPackage = null;
        this.pendingCheckoutId = null;
        this.statusCheckInterval = null;
        
        this.init();
    }

    init() {
        console.log('WalletManager initializing...');
        
        // Check if user is logged in first
        const token = localStorage.getItem('auth_access_token');
        if (!token) {
            console.log('No auth token found, redirecting to login');
            window.location.href = '/login?redirect=/wallet';
            return;
        }
        
        this.bindEvents();
        this.loadWallet();
        this.loadTokenPackages();
        this.loadTransactions();
    }

    bindEvents() {
        console.log('Binding wallet events...');
        // Deposit modal
        const depositBtn = document.getElementById('deposit-btn');
        if (depositBtn) {
            console.log('Deposit button found, binding click event');
            depositBtn.addEventListener('click', () => {
                console.log('Deposit button clicked');
                this.openDepositModal();
            });
        } else {
            console.error('Deposit button not found!');
        }
        
        document.getElementById('close-deposit-modal')?.addEventListener('click', () => this.closeDepositModal());
        document.getElementById('deposit-form')?.addEventListener('submit', (e) => this.handleDeposit(e));
        document.getElementById('check-status-btn')?.addEventListener('click', () => this.checkDepositStatus());
        
        // Quick amount buttons
        document.querySelectorAll('.quick-amount').forEach(btn => {
            btn.addEventListener('click', () => {
                document.getElementById('deposit-amount').value = btn.dataset.amount;
            });
        });

        // Token purchase modal
        document.getElementById('cancel-token-btn')?.addEventListener('click', () => this.closeTokenModal());
        document.getElementById('confirm-token-btn')?.addEventListener('click', () => this.confirmTokenPurchase());

        // Custom token amount input
        const customTokensInput = document.getElementById('custom-tokens');
        const customPriceDisplay = document.getElementById('custom-price');
        const buyCustomBtn = document.getElementById('buy-custom-tokens');
        
        if (customTokensInput) {
            customTokensInput.addEventListener('input', () => {
                const tokens = parseInt(customTokensInput.value) || 0;
                const price = this.calculateCustomPrice(tokens);
                customPriceDisplay.textContent = tokens >= 10 ? `KES ${price.toLocaleString()}` : 'KES 0';
                buyCustomBtn.disabled = tokens < 10;
            });
        }
        
        if (buyCustomBtn) {
            buyCustomBtn.addEventListener('click', () => {
                const tokens = parseInt(customTokensInput.value) || 0;
                if (tokens >= 10) {
                    const price = this.calculateCustomPrice(tokens);
                    this.selectedPackage = { tokens, price, custom: true };
                    document.getElementById('confirm-tokens').textContent = tokens.toLocaleString();
                    document.getElementById('confirm-price').textContent = `KES ${price.toLocaleString()}`;
                    this.openTokenModal();
                }
            });
        }

        // Transaction filter
        document.getElementById('transaction-filter')?.addEventListener('change', () => {
            this.currentPage = 1;
            this.loadTransactions();
        });

        // Pagination
        document.getElementById('prev-page-btn')?.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadTransactions();
            }
        });
        document.getElementById('next-page-btn')?.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.loadTransactions();
            }
        });

        // Close modals on backdrop click
        document.getElementById('deposit-modal')?.addEventListener('click', (e) => {
            if (e.target.id === 'deposit-modal') this.closeDepositModal();
        });
        document.getElementById('token-modal')?.addEventListener('click', (e) => {
            if (e.target.id === 'token-modal') this.closeTokenModal();
        });
    }

    calculateCustomPrice(tokens) {
        if (tokens < 10) return 0;
        
        let rate;
        if (tokens >= 10000) {
            rate = 0.25;  // 50% discount
        } else if (tokens >= 5000) {
            rate = 0.30;  // 40% discount
        } else if (tokens >= 1000) {
            rate = 0.35;  // 30% discount
        } else if (tokens >= 500) {
            rate = 0.40;  // 20% discount
        } else {
            rate = 0.50;  // base rate
        }
        
        return Math.round(tokens * rate * 100) / 100;
    }

    async loadWallet() {
        const token = localStorage.getItem('auth_access_token');
        console.log('loadWallet - token exists:', !!token);
        
        if (!token) {
            console.log('No token, redirecting to login');
            window.location.href = '/login?redirect=/wallet';
            return;
        }
        
        try {
            const response = await fetch('/api/wallet/balance', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log('loadWallet response status:', response.status);

            if (response.status === 401) {
                console.log('Got 401, clearing tokens and redirecting');
                localStorage.removeItem('auth_access_token');
                localStorage.removeItem('auth_refresh_token');
                localStorage.removeItem('auth_user');
                window.location.href = '/login?redirect=/wallet';
                return;
            }

            if (response.ok) {
                const wallet = await response.json();
                this.updateWalletUI(wallet);
            }
        } catch (error) {
            console.error('Error loading wallet:', error);
        }
    }

    updateWalletUI(wallet) {
        const balanceEl = document.getElementById('wallet-balance');
        const tokensEl = document.getElementById('chat-tokens');
        const usedEl = document.getElementById('tokens-used');
        const updatedEl = document.getElementById('wallet-updated');

        if (balanceEl) balanceEl.textContent = (wallet.balance || 0).toFixed(2);
        if (tokensEl) tokensEl.textContent = wallet.chat_tokens || 0;
        if (usedEl) usedEl.textContent = wallet.tokens_used || 0;
        if (updatedEl) {
            updatedEl.textContent = wallet.last_updated 
                ? new Date(wallet.last_updated).toLocaleString()
                : 'Never';
        }
    }

    async loadTokenPackages() {
        try {
            const response = await fetch('/api/wallet/tokens', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderTokenPackages(data.packages);
            }
        } catch (error) {
            console.error('Error loading token packages:', error);
        }
    }

    renderTokenPackages(packages) {
        const container = document.getElementById('token-packages');
        if (!container) return;

        container.innerHTML = packages.map(pkg => `
            <button class="token-package p-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl hover:border-nse-primary hover:bg-nse-primary/5 transition-all text-left"
                data-tokens="${pkg.tokens}" data-price="${pkg.price}">
                <div class="text-2xl font-bold text-nse-primary mb-1">${pkg.tokens.toLocaleString()}</div>
                <div class="text-gray-500 dark:text-gray-400 text-sm">tokens</div>
                <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                    <span class="font-semibold text-gray-900 dark:text-white">KES ${pkg.price.toLocaleString()}</span>
                </div>
            </button>
        `).join('');

        // Bind package click events
        container.querySelectorAll('.token-package').forEach(btn => {
            btn.addEventListener('click', () => this.selectTokenPackage(btn));
        });
    }

    selectTokenPackage(btn) {
        const tokens = parseInt(btn.dataset.tokens);
        const price = parseFloat(btn.dataset.price);
        
        this.selectedPackage = { tokens, price };
        
        document.getElementById('confirm-tokens').textContent = tokens.toLocaleString();
        document.getElementById('confirm-price').textContent = `KES ${price.toLocaleString()}`;
        
        this.openTokenModal();
    }

    async confirmTokenPurchase() {
        if (!this.selectedPackage) return;

        const confirmBtn = document.getElementById('confirm-token-btn');
        const messageEl = document.getElementById('token-purchase-message');
        
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Processing...';

        try {
            const payload = { 
                tokens: this.selectedPackage.tokens,
                custom: this.selectedPackage.custom || false
            };
            
            const response = await fetch('/api/wallet/tokens', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage(messageEl, data.message, 'success');
                this.updateWalletUI(data.wallet);
                // Clear custom input if it was a custom purchase
                const customInput = document.getElementById('custom-tokens');
                if (customInput) customInput.value = '';
                document.getElementById('custom-price').textContent = 'KES 0';
                document.getElementById('buy-custom-tokens').disabled = true;
                
                setTimeout(() => {
                    this.closeTokenModal();
                    this.loadTransactions();
                }, 1500);
            } else {
                this.showMessage(messageEl, data.message || 'Purchase failed', 'error');
            }
        } catch (error) {
            this.showMessage(messageEl, 'An error occurred', 'error');
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.textContent = 'Confirm';
        }
    }

    async loadTransactions() {
        const filter = document.getElementById('transaction-filter')?.value || '';
        
        try {
            const url = new URL('/api/wallet/transactions', window.location.origin);
            url.searchParams.set('page', this.currentPage);
            if (filter) url.searchParams.set('type', filter);

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.renderTransactions(data.transactions);
                this.updatePagination(data);
            }
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    renderTransactions(transactions) {
        const container = document.getElementById('transactions-list');
        const emptyState = document.getElementById('no-transactions');
        
        if (!container) return;

        if (!transactions || transactions.length === 0) {
            container.innerHTML = '';
            emptyState?.classList.remove('hidden');
            return;
        }

        emptyState?.classList.add('hidden');

        container.innerHTML = transactions.map(tx => {
            const isCredit = tx.amount > 0;
            const statusColors = {
                'completed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
                'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
                'failed': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
            };
            const typeIcons = {
                'deposit': `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>`,
                'payment': `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
                </svg>`,
                'refund': `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
                </svg>`
            };

            return `
                <div class="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center ${isCredit ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'}">
                        ${typeIcons[tx.type] || typeIcons['payment']}
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="font-medium text-gray-900 dark:text-white truncate">${tx.description || tx.type}</p>
                        <p class="text-sm text-gray-500 dark:text-gray-400">
                            ${new Date(tx.created_at).toLocaleDateString()} ${new Date(tx.created_at).toLocaleTimeString()}
                        </p>
                    </div>
                    <div class="text-right">
                        <p class="font-semibold ${isCredit ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
                            ${isCredit ? '+' : ''}KES ${Math.abs(tx.amount).toFixed(2)}
                        </p>
                        <span class="inline-flex px-2 py-0.5 text-xs rounded-full ${statusColors[tx.status]}">
                            ${tx.status}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    }

    updatePagination(data) {
        const pagination = document.getElementById('transactions-pagination');
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');
        const pageInfo = document.getElementById('page-info');

        this.totalPages = Math.ceil(data.total / data.per_page);

        if (data.total > data.per_page) {
            pagination?.classList.remove('hidden');
            pageInfo.textContent = `Page ${data.page} of ${this.totalPages}`;
            prevBtn.disabled = data.page <= 1;
            nextBtn.disabled = data.page >= this.totalPages;
        } else {
            pagination?.classList.add('hidden');
        }
    }

    openDepositModal() {
        document.getElementById('deposit-modal')?.classList.remove('hidden');
        document.getElementById('deposit-form')?.classList.remove('hidden');
        document.getElementById('stk-pending')?.classList.add('hidden');
        document.getElementById('deposit-message')?.classList.add('hidden');
    }

    closeDepositModal() {
        document.getElementById('deposit-modal')?.classList.add('hidden');
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }

    async handleDeposit(e) {
        e.preventDefault();

        const phoneInput = document.getElementById('phone-number');
        const amountInput = document.getElementById('deposit-amount');
        const submitBtn = document.getElementById('submit-deposit-btn');
        const spinner = document.getElementById('deposit-spinner');
        const messageEl = document.getElementById('deposit-message');

        const phone = '254' + phoneInput.value.replace(/\D/g, '');
        const amount = parseFloat(amountInput.value);

        if (phone.length !== 12) {
            this.showMessage(messageEl, 'Please enter a valid phone number', 'error');
            return;
        }

        if (amount < 10) {
            this.showMessage(messageEl, 'Minimum deposit is KES 10', 'error');
            return;
        }

        submitBtn.disabled = true;
        spinner?.classList.remove('hidden');

        try {
            const response = await fetch('/api/wallet/deposit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
                },
                body: JSON.stringify({
                    phone_number: phone,
                    amount: amount
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.pendingCheckoutId = data.checkout_request_id;
                document.getElementById('pending-transaction-id').textContent = data.transaction_id;
                
                // Show pending state
                document.getElementById('deposit-form')?.classList.add('hidden');
                document.getElementById('stk-pending')?.classList.remove('hidden');
                
                // Start checking status
                this.startStatusCheck();
            } else {
                this.showMessage(messageEl, data.message || 'Failed to initiate payment', 'error');
            }
        } catch (error) {
            this.showMessage(messageEl, 'An error occurred. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            spinner?.classList.add('hidden');
        }
    }

    startStatusCheck() {
        let checks = 0;
        const maxChecks = 60; // Check for 2 minutes max

        this.statusCheckInterval = setInterval(async () => {
            checks++;
            if (checks >= maxChecks) {
                clearInterval(this.statusCheckInterval);
                return;
            }
            await this.checkDepositStatus();
        }, 2000);
    }

    async checkDepositStatus() {
        if (!this.pendingCheckoutId) return;

        try {
            const response = await fetch(`/api/wallet/deposit/status/${this.pendingCheckoutId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.transaction.status === 'completed') {
                    clearInterval(this.statusCheckInterval);
                    this.updateWalletUI(data.wallet);
                    this.closeDepositModal();
                    this.loadTransactions();
                    this.showNotification('Deposit successful!', 'success');
                } else if (data.transaction.status === 'failed') {
                    clearInterval(this.statusCheckInterval);
                    this.showNotification('Deposit failed. Please try again.', 'error');
                }
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }

    openTokenModal() {
        document.getElementById('token-modal')?.classList.remove('hidden');
        document.getElementById('token-purchase-message')?.classList.add('hidden');
    }

    closeTokenModal() {
        document.getElementById('token-modal')?.classList.add('hidden');
        this.selectedPackage = null;
    }

    showMessage(element, message, type) {
        if (!element) return;
        
        element.textContent = message;
        element.className = `p-3 rounded-lg text-sm ${
            type === 'success' 
                ? 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400'
        }`;
        element.classList.remove('hidden');
    }

    showNotification(message, type) {
        // Simple notification - could be enhanced with a toast library
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
            type === 'success' 
                ? 'bg-green-500 text-white' 
                : 'bg-red-500 text-white'
        }`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 3000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, creating WalletManager');
    window.walletManager = new WalletManager();
});
