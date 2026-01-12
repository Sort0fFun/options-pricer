/**
 * Option Calculator component.
 */

const Calculator = {
    mlVolatility: null,  // Store ML prediction

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

        // Setup UI helpers
        this.initHeatmapParamsUI();
        this.initMarketFiltersUI();

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
        const volatilityPct = document.getElementById('volatility-pct');
        if (volatilitySlider) {
            volatilitySlider.addEventListener('input', (e) => {
                if (volatilityDisplay) volatilityDisplay.textContent = e.target.value;
                if (volatilityPct) volatilityPct.textContent = e.target.value;
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

        // Heatmap params toggle
        const toggleBtn = document.getElementById('toggle-heatmap-params');
        const paramsEl = document.getElementById('heatmap-params');
        const arrowEl = document.getElementById('heatmap-params-arrow');
        if (toggleBtn && paramsEl) {
            toggleBtn.addEventListener('click', () => {
                const hidden = paramsEl.classList.toggle('collapsible-hidden');
                if (arrowEl) arrowEl.textContent = hidden ? '▸' : '▾';
            });
        }

        // Heatmap param controls
        ['min-price-dec','min-price-inc','max-price-dec','max-price-inc'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('click', () => {
                    const minPriceEl = document.getElementById('min-futures-price');
                    const maxPriceEl = document.getElementById('max-futures-price');
                    if (!minPriceEl || !maxPriceEl) return;
                    const step = 1.0;
                    const minVal = parseFloat(minPriceEl.value) || 0;
                    const maxVal = parseFloat(maxPriceEl.value) || 0;
                    if (id === 'min-price-dec') minPriceEl.value = (minVal - step).toFixed(2);
                    if (id === 'min-price-inc') minPriceEl.value = (minVal + step).toFixed(2);
                    if (id === 'max-price-dec') maxPriceEl.value = (maxVal - step).toFixed(2);
                    if (id === 'max-price-inc') maxPriceEl.value = (maxVal + step).toFixed(2);
                    this.calculate();
                });
            }
        });

        // Risk-free rate +/- buttons
        const rateDecBtn = document.getElementById('rate-dec');
        const rateIncBtn = document.getElementById('rate-inc');
        const rateInput = document.getElementById('risk_free_rate');
        if (rateDecBtn && rateInput) {
            rateDecBtn.addEventListener('click', () => {
                rateInput.value = Math.max(0, parseFloat(rateInput.value) - 0.5).toFixed(2);
                this.calculate();
            });
        }
        if (rateIncBtn && rateInput) {
            rateIncBtn.addEventListener('click', () => {
                rateInput.value = Math.min(100, parseFloat(rateInput.value) + 0.5).toFixed(2);
                this.calculate();
            });
        }

        // ML Volatility prediction
        const fetchMLBtn = document.getElementById('fetch-ml-vol');
        if (fetchMLBtn) {
            fetchMLBtn.addEventListener('click', () => this.fetchMLVolatility());
        }

        // Use ML Volatility button
        const useMLBtn = document.getElementById('use-ml-vol');
        if (useMLBtn) {
            useMLBtn.addEventListener('click', () => this.useMLVolatility());
        }

        const minVol = document.getElementById('min-vol');
        const maxVol = document.getElementById('max-vol');
        if (minVol) {
            minVol.addEventListener('input', (e) => {
                document.getElementById('min-vol-display').textContent = parseFloat(e.target.value).toFixed(2);
                this.calculate();
            });
        }
        if (maxVol) {
            maxVol.addEventListener('input', (e) => {
                document.getElementById('max-vol-display').textContent = parseFloat(e.target.value).toFixed(2);
                this.calculate();
            });
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
        // Update metrics (formatted with 4 decimal places like the screenshot)
        document.getElementById('metric-price').textContent = inputs.futures_price.toFixed(4);
        document.getElementById('metric-strike').textContent = inputs.strike_price.toFixed(4);
        document.getElementById('metric-time').textContent = data.pricing_summary.time_to_maturity.toFixed(4);
        document.getElementById('metric-volatility').textContent = inputs.volatility.toFixed(4);
        document.getElementById('metric-rate').textContent = inputs.risk_free_rate.toFixed(4);

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
            const heatmapParams = this.getHeatmapParams(inputs);

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
     * Build heatmap params from UI controls
     */
    getHeatmapParams(inputs) {
        const minPriceEl = document.getElementById('min-futures-price');
        const maxPriceEl = document.getElementById('max-futures-price');
        const minVolEl = document.getElementById('min-vol');
        const maxVolEl = document.getElementById('max-vol');

        let priceRangePct = 20; // default
        let volRangePct = 50;   // default

        if (minPriceEl && maxPriceEl) {
            const minPrice = parseFloat(minPriceEl.value) || inputs.futures_price * 0.8;
            const maxPrice = parseFloat(maxPriceEl.value) || inputs.futures_price * 1.2;
            const halfRange = Math.max(
                inputs.futures_price - minPrice,
                maxPrice - inputs.futures_price
            );
            priceRangePct = Math.max(5, Math.round((halfRange / inputs.futures_price) * 100));
        }

        if (minVolEl && maxVolEl) {
            const minV = parseFloat(minVolEl.value) || inputs.volatility * 0.5;
            const maxV = parseFloat(maxVolEl.value) || inputs.volatility * 1.5;
            const halfRangeV = Math.max(
                inputs.volatility - minV,
                maxV - inputs.volatility
            );
            volRangePct = Math.max(10, Math.round((halfRangeV / inputs.volatility) * 100));
        }

        return {
            futures_price: inputs.futures_price,
            strike_price: inputs.strike_price,
            days_to_expiry: inputs.days_to_expiry,
            volatility: inputs.volatility,
            risk_free_rate: inputs.risk_free_rate,
            price_range_pct: priceRangePct,
            vol_range_pct: volRangePct,
            grid_size: 12
        };
    },

    /**
     * Initialize market filter chips UI
     */
    initMarketFiltersUI() {
        // All available options
        this.allContracts = ['N25I','25MN','10MN','SCOM','EQTY','KCB','SBIC','ABSA','COOP','NCBA'];
        this.allTypes = ['Index','Single Stock'];
        
        // Currently selected filters
        this.marketFilters = {
            contracts: ['N25I','25MN','10MN','SCOM','EQTY'],
            types: ['Index','Single Stock']
        };

        const contractChips = document.getElementById('contract-chips');
        const typeChips = document.getElementById('type-chips');
        const clearBtn = document.getElementById('clear-contracts');

        const self = this;

        const renderChips = (container, items, key) => {
            if (!container) return;
            container.innerHTML = items.map(item => `
                <span class="chip chip-active" data-key="${key}" data-value="${item}">
                    ${item}
                    <button aria-label="remove">×</button>
                </span>
            `).join('');
            container.querySelectorAll('.chip button').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const chip = e.target.closest('.chip');
                    const value = chip.dataset.value;
                    const k = chip.dataset.key;
                    self.marketFilters[k] = self.marketFilters[k].filter(v => v !== value);
                    renderChips(container, self.marketFilters[k], k);
                    self.updateDropdown(k);
                    self.loadMarketData();
                });
            });
        };

        renderChips(contractChips, this.marketFilters.contracts, 'contracts');
        renderChips(typeChips, this.marketFilters.types, 'types');

        // Setup dropdown for contracts
        const addContractBtn = document.getElementById('add-contract-btn');
        const contractDropdown = document.getElementById('contract-dropdown');
        if (addContractBtn && contractDropdown) {
            addContractBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                contractDropdown.classList.toggle('hidden');
                // Close type dropdown
                document.getElementById('type-dropdown')?.classList.add('hidden');
            });
            this.updateDropdown('contracts');
        }

        // Setup dropdown for types
        const addTypeBtn = document.getElementById('add-type-btn');
        const typeDropdown = document.getElementById('type-dropdown');
        if (addTypeBtn && typeDropdown) {
            addTypeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                typeDropdown.classList.toggle('hidden');
                // Close contract dropdown
                document.getElementById('contract-dropdown')?.classList.add('hidden');
            });
            this.updateDropdown('types');
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            contractDropdown?.classList.add('hidden');
            typeDropdown?.classList.add('hidden');
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.marketFilters.contracts = [];
                renderChips(contractChips, this.marketFilters.contracts, 'contracts');
                this.updateDropdown('contracts');
                this.loadMarketData();
            });
        }

        // Store renderChips for reuse
        this.renderChips = renderChips;
    },

    /**
     * Update dropdown options based on what's already selected
     */
    updateDropdown(key) {
        const allItems = key === 'contracts' ? this.allContracts : this.allTypes;
        const selected = this.marketFilters[key];
        const available = allItems.filter(item => !selected.includes(item));
        
        const dropdownId = key === 'contracts' ? 'contract-dropdown' : 'type-dropdown';
        const dropdown = document.getElementById(dropdownId);
        const chipsContainer = document.getElementById(key === 'contracts' ? 'contract-chips' : 'type-chips');
        
        if (!dropdown) return;

        if (available.length === 0) {
            dropdown.innerHTML = '<div class="px-3 py-2 text-sm text-gray-400">All items selected</div>';
        } else {
            dropdown.innerHTML = available.map(item => `
                <button type="button" data-value="${item}">${item}</button>
            `).join('');
            
            dropdown.querySelectorAll('button').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const value = btn.dataset.value;
                    this.marketFilters[key].push(value);
                    this.renderChips(chipsContainer, this.marketFilters[key], key);
                    this.updateDropdown(key);
                    dropdown.classList.add('hidden');
                    this.loadMarketData();
                });
            });
        }
    },

    /**
     * Initialize heatmap params defaults and display
     */
    initHeatmapParamsUI() {
        const minVol = document.getElementById('min-vol');
        const maxVol = document.getElementById('max-vol');
        if (minVol) document.getElementById('min-vol-display').textContent = parseFloat(minVol.value).toFixed(2);
        if (maxVol) document.getElementById('max-vol-display').textContent = parseFloat(maxVol.value).toFixed(2);
    },

    /**
     * Load market data
     */
    async loadMarketData() {
        try {
            const filters = {};
            if (this.marketFilters?.contracts?.length) {
                filters.contracts = this.marketFilters.contracts.join(',');
            }
            if (this.marketFilters?.types?.length) {
                filters.types = this.marketFilters.types.join(',');
            }
            const response = await API.market.getFutures(filters);

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
        `;

        container.innerHTML = tableHTML;

        const marketCount = document.getElementById('market-count');
        if (marketCount) {
            marketCount.textContent = `Showing ${data.total} futures contracts`;
        }
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
    },

    /**
     * Fetch ML volatility prediction
     */
    async fetchMLVolatility() {
        const symbol = document.getElementById('contract')?.value || 'ESZ4';
        const fetchBtn = document.getElementById('fetch-ml-vol');
        const spinner = document.getElementById('fetch-ml-spinner');
        const btnText = document.getElementById('fetch-ml-text');

        // Show loading state
        if (fetchBtn) fetchBtn.disabled = true;
        if (spinner) spinner.classList.remove('hidden');
        if (btnText) btnText.textContent = 'Loading...';

        try {
            const response = await API.volatility.predict({
                symbol: symbol,
                horizon: 1,
                confidence_level: 0.95
            });

            if (response.success && response.data) {
                this.mlVolatility = response.data;
                this.displayMLPrediction(response.data);
            } else {
                console.error('ML prediction failed:', response.message);
                alert(response.message || 'Failed to fetch ML prediction');
            }
        } catch (error) {
            console.error('ML prediction error:', error);
            alert('Failed to fetch ML prediction. Please ensure you have historical data for this symbol.');
        } finally {
            // Reset button state
            if (fetchBtn) fetchBtn.disabled = false;
            if (spinner) spinner.classList.add('hidden');
            if (btnText) btnText.textContent = 'Get Prediction';
        }
    },

    /**
     * Display ML prediction results
     */
    displayMLPrediction(data) {
        const resultSection = document.getElementById('ml-prediction-result');
        const placeholder = document.getElementById('ml-prediction-placeholder');
        
        if (placeholder) placeholder.classList.add('hidden');
        if (resultSection) resultSection.classList.remove('hidden');

        // Update values
        const mlVolValue = document.getElementById('ml-vol-value');
        const mlVolPercent = document.getElementById('ml-vol-percent');
        const mlConfidence = document.getElementById('ml-confidence');
        const mlVsCurrent = document.getElementById('ml-vs-current');

        const predictedVol = data.predicted_volatility;
        const currentVol = parseFloat(document.getElementById('volatility').value) / 100;

        if (mlVolValue) mlVolValue.textContent = predictedVol.toFixed(4);
        if (mlVolPercent) mlVolPercent.textContent = `${(predictedVol * 100).toFixed(2)}%`;
        
        if (mlConfidence && data.confidence_interval) {
            const lower = (data.confidence_interval.lower * 100).toFixed(2);
            const upper = (data.confidence_interval.upper * 100).toFixed(2);
            mlConfidence.textContent = `${lower}% - ${upper}%`;
        }

        if (mlVsCurrent) {
            const diff = ((predictedVol - currentVol) / currentVol * 100).toFixed(1);
            const color = diff > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
            mlVsCurrent.className = `text-lg font-bold ${color}`;
            mlVsCurrent.textContent = `${diff > 0 ? '+' : ''}${diff}%`;
        }
    },

    /**
     * Use ML volatility in calculator
     */
    useMLVolatility() {
        if (!this.mlVolatility) return;

        const predictedVol = this.mlVolatility.predicted_volatility;
        const volPct = Math.round(predictedVol * 100);

        // Update volatility slider
        const volatilitySlider = document.getElementById('volatility');
        const volatilityDisplay = document.getElementById('volatility-display');
        const volatilityPct = document.getElementById('volatility-pct');

        if (volatilitySlider) volatilitySlider.value = volPct;
        if (volatilityDisplay) volatilityDisplay.textContent = volPct;
        if (volatilityPct) volatilityPct.textContent = volPct;

        // Recalculate prices
        this.calculate();
        this.saveInputs();

        // Show success message
        const useMLBtn = document.getElementById('use-ml-vol');
        if (useMLBtn) {
            const originalText = useMLBtn.textContent;
            useMLBtn.textContent = '✓ Applied!';
            useMLBtn.classList.add('bg-green-600');
            setTimeout(() => {
                useMLBtn.textContent = originalText;
                useMLBtn.classList.remove('bg-green-600');
            }, 2000);
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
