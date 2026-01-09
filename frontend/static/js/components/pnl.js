/**
 * PnL Predictor component.
 */

const PnL = {
    strategies: [],
    customLegs: [],

    /**
     * Initialize PnL predictor
     */
    async init() {
        console.log('Initializing PnL Predictor...');

        // Setup tabs
        this.setupTabs();

        // Load strategies
        await this.loadStrategies();

        // Load saved custom legs
        this.loadCustomLegs();

        // Setup event listeners
        this.setupEventListeners();
    },

    /**
     * Setup tab switching
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;

                // Update button states
                tabButtons.forEach(btn => {
                    btn.classList.remove('tab-button-active');
                });
                button.classList.add('tab-button-active');

                // Update content visibility
                tabContents.forEach(content => {
                    content.classList.remove('tab-content-active');
                });
                document.getElementById(`tab-${tabName}`).classList.add('tab-content-active');
            });
        });
    },

    /**
     * Load available strategies
     */
    async loadStrategies() {
        try {
            const response = await API.pnl.getStrategies();

            if (response.success && response.data) {
                this.strategies = response.data.strategies;
                this.populateStrategyDropdowns();
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    },

    /**
     * Populate strategy dropdowns
     */
    populateStrategyDropdowns() {
        const selects = [
            'strategy-select',
            'compare-strategy-1',
            'compare-strategy-2',
            'compare-strategy-3',
            'compare-strategy-4',
            'scenario-strategy'
        ];

        const options = this.strategies.map(s =>
            `<option value="${s.name}">${s.label}</option>`
        ).join('');

        selects.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                select.innerHTML = '<option value="">Select a strategy...</option>' + options;
            }
        });
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Strategy builder
        const strategySelect = document.getElementById('strategy-select');
        if (strategySelect) {
            strategySelect.addEventListener('change', (e) => this.updateStrategyParams(e.target.value));
        }

        const calculateStrategyBtn = document.getElementById('calculate-strategy-btn');
        if (calculateStrategyBtn) {
            calculateStrategyBtn.addEventListener('click', () => this.calculateStrategy());
        }

        // Custom position
        const addLegBtn = document.getElementById('add-leg-btn');
        if (addLegBtn) {
            addLegBtn.addEventListener('click', () => this.addCustomLeg());
        }

        const calculateCustomBtn = document.getElementById('calculate-custom-btn');
        if (calculateCustomBtn) {
            calculateCustomBtn.addEventListener('click', () => this.calculateCustomStrategy());
        }

        // Compare
        const compareBtn = document.getElementById('compare-btn');
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.compareStrategies());
        }

        // Scenario
        const scenarioBtn = document.getElementById('scenario-analyze-btn');
        if (scenarioBtn) {
            scenarioBtn.addEventListener('click', () => this.runScenarioAnalysis());
        }
    },

    /**
     * Update strategy parameters form
     */
    updateStrategyParams(strategyName) {
        const container = document.getElementById('strategy-params');
        if (!strategyName) {
            container.innerHTML = '';
            return;
        }

        const currentPrice = Formatter.parseFloat(document.getElementById('pnl_current_price').value, 100);

        // Define parameters for each strategy
        const params = {
            'long_call': [
                { label: 'Strike Price', id: 'strike', value: currentPrice * 1.05 },
                { label: 'Premium', id: 'premium', value: currentPrice * 0.05 }
            ],
            'long_put': [
                { label: 'Strike Price', id: 'strike', value: currentPrice * 0.95 },
                { label: 'Premium', id: 'premium', value: currentPrice * 0.05 }
            ],
            'bull_call_spread': [
                { label: 'Lower Strike', id: 'lower_strike', value: currentPrice * 0.95 },
                { label: 'Upper Strike', id: 'upper_strike', value: currentPrice * 1.05 },
                { label: 'Lower Premium', id: 'lower_premium', value: currentPrice * 0.07 },
                { label: 'Upper Premium', id: 'upper_premium', value: currentPrice * 0.03 }
            ],
            'bear_put_spread': [
                { label: 'Lower Strike', id: 'lower_strike', value: currentPrice * 0.95 },
                { label: 'Upper Strike', id: 'upper_strike', value: currentPrice * 1.05 },
                { label: 'Lower Premium', id: 'lower_premium', value: currentPrice * 0.03 },
                { label: 'Upper Premium', id: 'upper_premium', value: currentPrice * 0.07 }
            ],
            'long_straddle': [
                { label: 'Strike', id: 'strike', value: currentPrice },
                { label: 'Call Premium', id: 'call_premium', value: currentPrice * 0.05 },
                { label: 'Put Premium', id: 'put_premium', value: currentPrice * 0.05 }
            ],
            'long_strangle': [
                { label: 'Call Strike', id: 'call_strike', value: currentPrice * 1.05 },
                { label: 'Put Strike', id: 'put_strike', value: currentPrice * 0.95 },
                { label: 'Call Premium', id: 'call_premium', value: currentPrice * 0.03 },
                { label: 'Put Premium', id: 'put_premium', value: currentPrice * 0.03 }
            ],
            'iron_condor': [
                { label: 'Put Lower Strike', id: 'put_lower_strike', value: currentPrice * 0.90 },
                { label: 'Put Upper Strike', id: 'put_upper_strike', value: currentPrice * 0.95 },
                { label: 'Call Lower Strike', id: 'call_lower_strike', value: currentPrice * 1.05 },
                { label: 'Call Upper Strike', id: 'call_upper_strike', value: currentPrice * 1.10 },
                { label: 'Total Credit', id: 'total_credit', value: currentPrice * 0.04 }
            ],
            'butterfly_spread': [
                { label: 'Lower Strike', id: 'lower_strike', value: currentPrice * 0.95 },
                { label: 'Middle Strike', id: 'middle_strike', value: currentPrice },
                { label: 'Upper Strike', id: 'upper_strike', value: currentPrice * 1.05 },
                { label: 'Net Cost', id: 'net_cost', value: currentPrice * 0.02 }
            ],
            'covered_call': [
                { label: 'Stock Cost', id: 'stock_cost', value: currentPrice },
                { label: 'Call Strike', id: 'call_strike', value: currentPrice * 1.05 },
                { label: 'Call Premium', id: 'call_premium', value: currentPrice * 0.03 }
            ]
        };

        const strategyParams = params[strategyName] || [];

        container.innerHTML = strategyParams.map(param => `
            <div>
                <label class="input-label text-sm">${param.label}</label>
                <input type="number" id="param-${param.id}" class="input-field" value="${param.value.toFixed(2)}" step="0.01">
            </div>
        `).join('');
    },

    /**
     * Get market parameters
     */
    getMarketParams() {
        return {
            current_price: Formatter.parseFloat(document.getElementById('pnl_current_price').value, 100),
            price_range_pct: Formatter.parseFloat(document.getElementById('pnl_price_range').value, 50),
            time_to_expiry: Formatter.parseFloat(document.getElementById('pnl_time_expiry').value, 0.0822)
        };
    },

    /**
     * Get strategy parameters from form
     */
    getStrategyParams() {
        const params = { spot_price: this.getMarketParams().current_price };
        const inputs = document.querySelectorAll('[id^="param-"]');

        inputs.forEach(input => {
            const key = input.id.replace('param-', '');
            params[key] = Formatter.parseFloat(input.value, 0);
        });

        params.price_range_pct = this.getMarketParams().price_range_pct;

        return params;
    },

    /**
     * Calculate selected strategy
     */
    async calculateStrategy() {
        const strategyName = document.getElementById('strategy-select').value;
        if (!strategyName) {
            alert('Please select a strategy');
            return;
        }

        try {
            App.showLoading('strategy-results');
            document.getElementById('strategy-results').classList.remove('hidden');

            const parameters = this.getStrategyParams();

            const response = await API.pnl.buildStrategy(strategyName, parameters);

            if (response.success && response.data) {
                this.displayStrategyResults(response.data);
            }
        } catch (error) {
            console.error('Strategy calculation error:', error);
            App.showError('strategy-results', error.message || 'Failed to calculate strategy');
        }
    },

    /**
     * Display strategy results
     */
    displayStrategyResults(data) {
        // Render chart
        Charts.renderPnLChart('strategy-chart', data.pnl_data);

        // Update metrics
        document.getElementById('strategy-max-profit').textContent = Formatter.number(data.metrics.max_profit);
        document.getElementById('strategy-max-loss').textContent = Formatter.number(data.metrics.max_loss);
        document.getElementById('strategy-breakeven').textContent =
            data.metrics.breakeven_points.length > 0
                ? data.metrics.breakeven_points.map(bp => Formatter.number(bp, 2)).join(', ')
                : 'None';
        document.getElementById('strategy-description').textContent = data.strategy_description || '';

        document.getElementById('strategy-results').classList.remove('hidden');
    },

    /**
     * Add custom leg
     */
    addCustomLeg() {
        const leg = {
            option_type: document.getElementById('custom-option-type').value,
            strike: Formatter.parseFloat(document.getElementById('custom-strike').value, 100),
            premium: Formatter.parseFloat(document.getElementById('custom-premium').value, 5),
            position_type: document.getElementById('custom-position').value,
            quantity: Formatter.parseInt(document.getElementById('custom-quantity').value, 1)
        };

        this.customLegs.push(leg);
        this.saveCustomLegs();
        this.renderCustomLegs();

        // Enable calculate button
        document.getElementById('calculate-custom-btn').disabled = false;
    },

    /**
     * Render custom legs table
     */
    renderCustomLegs() {
        const container = document.getElementById('custom-legs-container');

        if (this.customLegs.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500">No legs added yet</p>';
            return;
        }

        const tableHTML = `
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Strike</th>
                            <th>Premium</th>
                            <th>Position</th>
                            <th>Qty</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.customLegs.map((leg, index) => `
                            <tr>
                                <td>${leg.option_type}</td>
                                <td>${Formatter.number(leg.strike)}</td>
                                <td>${Formatter.number(leg.premium)}</td>
                                <td>${leg.position_type}</td>
                                <td>${leg.quantity}</td>
                                <td>
                                    <button onclick="PnL.removeCustomLeg(${index})" class="text-red-600 hover:text-red-800">
                                        Remove
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHTML;
    },

    /**
     * Remove custom leg
     */
    removeCustomLeg(index) {
        this.customLegs.splice(index, 1);
        this.saveCustomLegs();
        this.renderCustomLegs();

        if (this.customLegs.length === 0) {
            document.getElementById('calculate-custom-btn').disabled = true;
            document.getElementById('custom-results').classList.add('hidden');
        }
    },

    /**
     * Calculate custom strategy
     */
    async calculateCustomStrategy() {
        if (this.customLegs.length === 0) {
            alert('Please add at least one leg');
            return;
        }

        try {
            App.showLoading('custom-results');
            document.getElementById('custom-results').classList.remove('hidden');

            const marketParams = this.getMarketParams();

            const response = await API.pnl.analyze({
                legs: this.customLegs
            }, marketParams);

            if (response.success && response.data) {
                this.displayCustomResults(response.data);
            }
        } catch (error) {
            console.error('Custom strategy calculation error:', error);
            App.showError('custom-results', error.message || 'Failed to calculate custom strategy');
        }
    },

    /**
     * Display custom results
     */
    displayCustomResults(data) {
        Charts.renderPnLChart('custom-chart', data.pnl_data);

        document.getElementById('custom-max-profit').textContent = Formatter.number(data.metrics.max_profit);
        document.getElementById('custom-max-loss').textContent = Formatter.number(data.metrics.max_loss);
        document.getElementById('custom-net-cost').textContent = Formatter.number(data.metrics.net_cost);
        document.getElementById('custom-breakeven').textContent =
            data.metrics.breakeven_points.length > 0
                ? data.metrics.breakeven_points.map(bp => Formatter.number(bp, 2)).join(', ')
                : 'None';

        document.getElementById('custom-results').classList.remove('hidden');
    },

    /**
     * Compare strategies
     */
    async compareStrategies() {
        const strategies = [
            document.getElementById('compare-strategy-1').value,
            document.getElementById('compare-strategy-2').value,
            document.getElementById('compare-strategy-3').value,
            document.getElementById('compare-strategy-4').value
        ].filter(s => s);

        if (strategies.length < 2) {
            alert('Please select at least 2 strategies to compare');
            return;
        }

        try {
            App.showLoading('compare-results');
            document.getElementById('compare-results').classList.remove('hidden');

            const marketParams = this.getMarketParams();
            const results = [];

            for (const strategyName of strategies) {
                const params = { ...marketParams, spot_price: marketParams.current_price };
                const response = await API.pnl.buildStrategy(strategyName, params);

                if (response.success && response.data) {
                    const strategy = this.strategies.find(s => s.name === strategyName);
                    results.push({
                        name: strategy.label,
                        pnl_data: response.data.pnl_data
                    });
                }
            }

            Charts.renderComparisonChart('compare-chart', results);
            document.getElementById('compare-results').classList.remove('hidden');

        } catch (error) {
            console.error('Comparison error:', error);
            App.showError('compare-results', error.message || 'Failed to compare strategies');
        }
    },

    /**
     * Run scenario analysis
     */
    async runScenarioAnalysis() {
        const strategyName = document.getElementById('scenario-strategy').value;
        if (!strategyName) {
            alert('Please select a strategy');
            return;
        }

        App.showLoading('scenario-results');
        document.getElementById('scenario-results').classList.remove('hidden');

        // For now, just show a single P&L chart
        // Future enhancement: Show 2x2 grid with different volatility/time scenarios
        try {
            const marketParams = this.getMarketParams();
            const params = { ...marketParams, spot_price: marketParams.current_price };

            const response = await API.pnl.buildStrategy(strategyName, params);

            if (response.success && response.data) {
                Charts.renderPnLChart('scenario-chart', response.data.pnl_data);
                document.getElementById('scenario-results').classList.remove('hidden');
            }
        } catch (error) {
            console.error('Scenario analysis error:', error);
            App.showError('scenario-results', error.message || 'Failed to run scenario analysis');
        }
    },

    /**
     * Save custom legs to localStorage
     */
    saveCustomLegs() {
        Storage.set(Storage.KEYS.PNL_LEGS, this.customLegs);
    },

    /**
     * Load custom legs from localStorage
     */
    loadCustomLegs() {
        const saved = Storage.get(Storage.KEYS.PNL_LEGS, []);
        this.customLegs = saved;
        this.renderCustomLegs();

        if (this.customLegs.length > 0) {
            document.getElementById('calculate-custom-btn').disabled = false;
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => PnL.init());
} else {
    PnL.init();
}

// Export for use in other modules
window.PnL = PnL;
