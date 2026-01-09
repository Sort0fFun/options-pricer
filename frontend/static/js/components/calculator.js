/**
 * Option Calculator component.
 */

const Calculator = {
    /**
     * Initialize calculator
     */
    async init() {
        console.log('Initializing calculator...');

        // Load contracts
        await this.loadContracts();

        // Load saved inputs from localStorage
        this.loadInputs();

        // Set up event listeners
        this.setupEventListeners();

        // Initial calculation
        await this.calculate();

        // Load market data
        await this.loadMarketData();
    },

    /**
     * Load contracts from API
     */
    async loadContracts() {
        try {
            const response = await API.pricing.getContracts();
            const contractSelect = document.getElementById('contract');

            if (response.data && response.data.contracts) {
                contractSelect.innerHTML = response.data.contracts.map(contract =>
                    `<option value="${contract.symbol}">${contract.name} (${contract.symbol})</option>`
                ).join('');
            }
        } catch (error) {
            console.error('Error loading contracts:', error);
        }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Input change handlers
        const inputs = ['futures_price', 'strike_price', 'days_to_expiry', 'risk_free_rate'];
        inputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', App.debounce(() => this.calculate(), 500));
                element.addEventListener('change', () => this.saveInputs());
            }
        });

        // Volatility slider
        const volatilitySlider = document.getElementById('volatility');
        const volatilityDisplay = document.getElementById('volatility-display');
        if (volatilitySlider) {
            volatilitySlider.addEventListener('input', (e) => {
                volatilityDisplay.textContent = e.target.value;
                this.calculate();
            });
            volatilitySlider.addEventListener('change', () => this.saveInputs());
        }

        // Option type radio buttons
        const optionTypeRadios = document.querySelectorAll('input[name="option_type"]');
        optionTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.calculate();
                this.saveInputs();
            });
        });

        // Include fees checkbox
        const includeFeesCheckbox = document.getElementById('include_fees');
        const feeBreakdown = document.getElementById('fee-breakdown');
        if (includeFeesCheckbox) {
            includeFeesCheckbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    feeBreakdown.classList.remove('hidden');
                } else {
                    feeBreakdown.classList.add('hidden');
                }
                this.calculate();
                this.saveInputs();
            });
        }

        // Contract selection
        const contractSelect = document.getElementById('contract');
        if (contractSelect) {
            contractSelect.addEventListener('change', () => this.saveInputs());
        }
    },

    /**
     * Get current input values
     */
    getInputs() {
        return {
            futures_price: Formatter.parseFloat(document.getElementById('futures_price').value, 100),
            strike_price: Formatter.parseFloat(document.getElementById('strike_price').value, 100),
            days_to_expiry: Formatter.parseInt(document.getElementById('days_to_expiry').value, 30),
            volatility: Formatter.parseFloat(document.getElementById('volatility').value, 30) / 100,
            risk_free_rate: Formatter.parseFloat(document.getElementById('risk_free_rate').value, 12) / 100,
            option_type: document.querySelector('input[name="option_type"]:checked')?.value || 'call',
            contract_symbol: document.getElementById('contract')?.value || 'SCOM',
            include_fees: document.getElementById('include_fees')?.checked || false
        };
    },

    /**
     * Calculate option prices
     */
    async calculate() {
        try {
            const inputs = this.getInputs();

            // Call pricing API
            const response = await API.pricing.calculate(inputs);

            if (response.success && response.data) {
                this.updateDisplay(response.data, inputs);
                await this.generateHeatmaps(inputs);
            }
        } catch (error) {
            console.error('Calculation error:', error);
            App.showError('pricing-summary', error.message || 'Failed to calculate prices');
        }
    },

    /**
     * Update display with calculated values
     */
    updateDisplay(data, inputs) {
        // Update metrics
        document.getElementById('metric-price').textContent = Formatter.number(inputs.futures_price);
        document.getElementById('metric-strike').textContent = Formatter.number(inputs.strike_price);
        document.getElementById('metric-time').textContent = data.pricing_summary.time_to_maturity.toFixed(4);
        document.getElementById('metric-volatility').textContent = (inputs.volatility * 100).toFixed(0);
        document.getElementById('metric-rate').textContent = (inputs.risk_free_rate * 100).toFixed(1);

        // Update call/put values
        const callValue = inputs.include_fees ? data.call_price_with_fees : data.call_price;
        const putValue = inputs.include_fees ? data.put_price_with_fees : data.put_price;

        document.getElementById('call-value').textContent = Formatter.number(callValue);
        document.getElementById('put-value').textContent = Formatter.number(putValue);
    },

    /**
     * Generate and display heatmaps
     */
    async generateHeatmaps(inputs) {
        try {
            const heatmapParams = {
                futures_price: inputs.futures_price,
                strike_price: inputs.strike_price,
                days_to_expiry: inputs.days_to_expiry,
                volatility: inputs.volatility,
                risk_free_rate: inputs.risk_free_rate,
                price_range_pct: 20,
                vol_range_pct: 50,
                grid_size: 12
            };

            const response = await API.pricing.heatmap(heatmapParams);

            if (response.success && response.data) {
                Charts.renderHeatmap('call-heatmap', response.data, 'call');
                Charts.renderHeatmap('put-heatmap', response.data, 'put');
            }
        } catch (error) {
            console.error('Heatmap generation error:', error);
        }
    },

    /**
     * Load market data
     */
    async loadMarketData() {
        try {
            const response = await API.market.getFutures();

            if (response.success && response.data) {
                this.renderMarketData(response.data);
            }
        } catch (error) {
            console.error('Error loading market data:', error);
            const container = document.getElementById('market-data-container');
            container.innerHTML = '<p class="text-center text-gray-500">Failed to load market data</p>';
        }
    },

    /**
     * Render market data table
     */
    renderMarketData(data) {
        const container = document.getElementById('market-data-container');

        if (!data.data || data.data.length === 0) {
            container.innerHTML = '<p class="text-center text-gray-500">No market data available</p>';
            return;
        }

        const headers = Object.keys(data.data[0]);

        const tableHTML = `
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            ${headers.map(h => `<th>${h}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.data.map(row => `
                            <tr>
                                ${headers.map(h => `<td>${row[h] !== null && row[h] !== undefined ? row[h] : '-'}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-4">
                Showing ${data.total} contract(s)
            </p>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Save inputs to localStorage
     */
    saveInputs() {
        const inputs = this.getInputs();
        Storage.set(Storage.KEYS.CALCULATOR_INPUTS, inputs);
    },

    /**
     * Load inputs from localStorage
     */
    loadInputs() {
        const saved = Storage.get(Storage.KEYS.CALCULATOR_INPUTS);
        if (saved) {
            if (saved.futures_price) document.getElementById('futures_price').value = saved.futures_price;
            if (saved.strike_price) document.getElementById('strike_price').value = saved.strike_price;
            if (saved.days_to_expiry) document.getElementById('days_to_expiry').value = saved.days_to_expiry;
            if (saved.volatility) {
                const volPct = Math.round(saved.volatility * 100);
                document.getElementById('volatility').value = volPct;
                document.getElementById('volatility-display').textContent = volPct;
            }
            if (saved.risk_free_rate) document.getElementById('risk_free_rate').value = saved.risk_free_rate * 100;
            if (saved.option_type) {
                const radio = document.querySelector(`input[name="option_type"][value="${saved.option_type}"]`);
                if (radio) radio.checked = true;
            }
            if (saved.include_fees) {
                document.getElementById('include_fees').checked = true;
                document.getElementById('fee-breakdown').classList.remove('hidden');
            }
        }
    }
};

// Initialize calculator when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Calculator.init());
} else {
    Calculator.init();
}

// Export for use in other modules
window.Calculator = Calculator;
