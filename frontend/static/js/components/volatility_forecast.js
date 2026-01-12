/**
 * Volatility Forecasting component.
 */

const VolatilityForecast = {
    currentSymbol: null,
    modelInfo: null,
    selectedFile: null,
    lastPrediction: null,

    /**
     * Initialize volatility forecast component
     */
    async init() {
        console.log('Initializing volatility forecast...');

        // Load model info
        await this.loadModelInfo();

        // Load available symbols
        await this.loadSymbols();

        // Setup event listeners
        this.setupEventListeners();

        // Load saved preferences
        this.loadPreferences();
    },

    /**
     * Load model information (NSE version)
     */
    async loadModelInfo() {
        // For NSE, we use static model info
        this.modelInfo = {
            model_type: 'GARCH + ARIMA',
            num_features: 'NSE Derivatives',
            trained_date: 'Real-time'
        };
        this.updateModelInfo();
    },

    /**
     * Load available symbols from NSE API
     */
    async loadSymbols() {
        const symbolSelect = document.getElementById('symbol');
        try {
            // Load NSE symbols from our API
            const response = await fetch('/api/nse/symbols');
            const symbols = await response.json();
            
            if (Array.isArray(symbols) && symbols.length > 0) {
                symbolSelect.innerHTML = symbols.map(sym =>
                    `<option value="${sym.value}">${sym.label}</option>`
                ).join('');
                
                // Select first symbol by default
                this.currentSymbol = symbols[0].value;
            } else {
                // Fallback to default NSE symbols
                const defaultSymbols = [
                    { value: 'SCOM', label: 'SCOM - Safaricom PLC' },
                    { value: 'EQTY', label: 'EQTY - Equity Group Holdings' },
                    { value: 'KCBG', label: 'KCBG - KCB Group PLC' },
                    { value: 'EABL', label: 'EABL - East African Breweries' },
                    { value: 'ABSA', label: 'ABSA - ABSA Bank Kenya' }
                ];
                symbolSelect.innerHTML = defaultSymbols.map(sym =>
                    `<option value="${sym.value}">${sym.label}</option>`
                ).join('');
                this.currentSymbol = defaultSymbols[0].value;
            }
        } catch (error) {
            console.error('Error loading NSE symbols:', error);
            // Use fallback NSE symbols
            const defaultSymbols = [
                { value: 'SCOM', label: 'SCOM - Safaricom PLC' },
                { value: 'EQTY', label: 'EQTY - Equity Group Holdings' },
                { value: 'KCBG', label: 'KCBG - KCB Group PLC' },
                { value: 'EABL', label: 'EABL - East African Breweries' },
                { value: 'ABSA', label: 'ABSA - ABSA Bank Kenya' }
            ];
            symbolSelect.innerHTML = defaultSymbols.map(sym =>
                `<option value="${sym.value}">${sym.label}</option>`
            ).join('');
            this.currentSymbol = defaultSymbols[0].value;
        }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Symbol change
        const symbolSelect = document.getElementById('symbol');
        if (symbolSelect) {
            symbolSelect.addEventListener('change', (e) => {
                this.currentSymbol = e.target.value;
                this.savePreferences();
            });
        }

        // Confidence slider
        const confidenceSlider = document.getElementById('confidence');
        const confidenceDisplay = document.getElementById('confidence-display');
        if (confidenceSlider && confidenceDisplay) {
            confidenceSlider.addEventListener('input', (e) => {
                confidenceDisplay.textContent = e.target.value;
            });
            confidenceSlider.addEventListener('change', () => this.savePreferences());
        }

        // Horizon input
        const horizonInput = document.getElementById('horizon');
        if (horizonInput) {
            horizonInput.addEventListener('change', () => this.savePreferences());
        }

        // Predict button
        const predictBtn = document.getElementById('predict-btn');
        if (predictBtn) {
            predictBtn.addEventListener('click', () => this.predict());
        }

        // Backtest button
        const backtestBtn = document.getElementById('backtest-btn');
        if (backtestBtn) {
            backtestBtn.addEventListener('click', () => this.backtest());
        }

        // File upload handlers
        this.setupFileUpload();

        // Use in calculator button
        const useInCalcBtn = document.getElementById('use-in-calculator-btn');
        if (useInCalcBtn) {
            useInCalcBtn.addEventListener('click', () => this.openCalculator());
        }
    },

    /**
     * Setup file upload drag-and-drop and click handlers
     */
    setupFileUpload() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const clearBtn = document.getElementById('clear-file');
        const uploadBtn = document.getElementById('upload-predict-btn');

        if (!dropZone || !fileInput) return;

        // Click to upload
        dropZone.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('border-purple-500', 'bg-purple-50', 'dark:bg-purple-900/20');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-purple-500', 'bg-purple-50', 'dark:bg-purple-900/20');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-purple-500', 'bg-purple-50', 'dark:bg-purple-900/20');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // Clear file
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFile());
        }

        // Upload and predict button
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.uploadAndPredict());
        }
    },

    /**
     * Handle file selection
     */
    handleFileSelect(file) {
        // Validate file type
        const validTypes = ['.csv', '.json'];
        const fileName = file.name.toLowerCase();
        const isValid = validTypes.some(type => fileName.endsWith(type));

        if (!isValid) {
            App.showError('alert-area', 'Invalid file type. Please upload a CSV or JSON file.');
            return;
        }

        // Check file size (max 10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            App.showError('alert-area', 'File too large. Maximum size is 10MB.');
            return;
        }

        // Store file reference
        this.selectedFile = file;

        // Update UI
        const fileInfo = document.getElementById('file-info');
        const fileNameEl = document.getElementById('file-name');
        const fileSizeEl = document.getElementById('file-size');
        const uploadBtn = document.getElementById('upload-predict-btn');

        if (fileInfo) fileInfo.classList.remove('hidden');
        if (fileNameEl) fileNameEl.textContent = file.name;
        if (fileSizeEl) {
            const sizeKB = (file.size / 1024).toFixed(2);
            fileSizeEl.textContent = `Size: ${sizeKB} KB`;
        }
        if (uploadBtn) uploadBtn.disabled = false;

        // Clear any previous errors
        document.getElementById('alert-area').innerHTML = '';
    },

    /**
     * Clear selected file
     */
    clearFile() {
        this.selectedFile = null;

        const fileInput = document.getElementById('file-input');
        const fileInfo = document.getElementById('file-info');
        const uploadBtn = document.getElementById('upload-predict-btn');

        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.classList.add('hidden');
        if (uploadBtn) uploadBtn.disabled = true;
    },

    /**
     * Upload file and get prediction
     */
    async uploadAndPredict() {
        if (!this.selectedFile) {
            App.showError('alert-area', 'Please select a file first');
            return;
        }

        const horizon = parseInt(document.getElementById('horizon').value);
        const dataName = this.selectedFile.name.replace(/\.(csv|json)$/i, '');

        // Show loading state
        this.setLoading('upload', true);
        document.getElementById('welcome-state')?.classList.add('hidden');
        document.getElementById('backtest-section')?.classList.add('hidden');

        try {
            const response = await API.volatility.uploadAndPredict(
                this.selectedFile,
                horizon,
                dataName
            );

            if (response.success && response.data) {
                // Show upload data info
                this.displayUploadDataInfo(response.data.data_info);
                
                // Display prediction
                this.displayPrediction(response.data);

                // Clear file after successful prediction
                this.clearFile();
            } else {
                App.showError('alert-area', response.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            App.showError('alert-area', `Upload failed: ${error.message}`);
        } finally {
            this.setLoading('upload', false);
        }
    },

    /**
     * Display uploaded data info
     */
    displayUploadDataInfo(dataInfo) {
        const container = document.getElementById('upload-data-info');
        if (!container || !dataInfo) return;

        container.classList.remove('hidden');

        const nameEl = document.getElementById('upload-data-name');
        const rowsEl = document.getElementById('upload-data-rows');
        const rangeEl = document.getElementById('upload-data-range');

        if (nameEl) nameEl.textContent = dataInfo.name || 'Custom Data';
        if (rowsEl) rowsEl.textContent = dataInfo.rows?.toLocaleString() || '0';
        if (rangeEl && dataInfo.date_range) {
            const start = new Date(dataInfo.date_range.start).toLocaleDateString();
            const end = new Date(dataInfo.date_range.end).toLocaleDateString();
            rangeEl.textContent = `${start} to ${end}`;
        }
    },

    /**
     * Hide upload data info (when switching to symbol-based prediction)
     */
    hideUploadDataInfo() {
        const container = document.getElementById('upload-data-info');
        if (container) container.classList.add('hidden');
    },

    /**
     * Navigate to calculator with predicted volatility pre-filled
     */
    openCalculator() {
        if (!this.currentSymbol || !this.lastPrediction) {
            App.showError('alert-area', 'No prediction available to use');
            return;
        }

        // Store prediction data for calculator to pick up
        const calcData = {
            volatility: this.lastPrediction.predicted_volatility,
            symbol: this.currentSymbol,
            source: 'ml_forecast',
            confidence: this.lastPrediction.model_confidence,
            timestamp: this.lastPrediction.prediction_timestamp
        };

        localStorage.setItem('nse_calculator_prefill', JSON.stringify(calcData));

        // Navigate to calculator
        window.location.href = '/';
    },

    /**
     * Update model information display for NSE
     */
    updateModelInfo() {
        const modelName = document.getElementById('model-name');
        const modelFeatures = document.getElementById('model-features');
        const modelTrained = document.getElementById('model-trained');
        const featureImportance = document.getElementById('feature-importance');

        // Set NSE-specific model info
        if (modelName) modelName.textContent = 'GARCH + ARIMA';
        if (modelFeatures) modelFeatures.textContent = 'NSE Derivatives';
        if (modelTrained) modelTrained.textContent = 'Real-time';

        // Display NSE model features
        if (featureImportance) {
            const features = [
                { name: 'GARCH(1,1) Volatility', importance: 0.35 },
                { name: 'ARIMA Price Forecast', importance: 0.25 },
                { name: 'Log Returns', importance: 0.15 },
                { name: 'Historical Vol (Annual)', importance: 0.12 },
                { name: 'Open Interest', importance: 0.08 },
                { name: 'Days to Expiry', importance: 0.05 }
            ];
            featureImportance.innerHTML = features.map((feature, idx) =>
                `<div class="flex justify-between text-gray-700 dark:text-gray-300">
                    <span>${idx + 1}. ${feature.name}</span>
                    <span class="font-medium">${(feature.importance * 100).toFixed(1)}%</span>
                </div>`
            ).join('');
        }
    },

    /**
     * Get prediction using NSE combined forecast
     */
    async predict() {
        const symbol = document.getElementById('symbol').value;
        const horizon = parseInt(document.getElementById('horizon').value);
        const confidence = parseFloat(document.getElementById('confidence').value) / 100;

        if (!symbol) {
            App.showError('alert-area', 'Please select a symbol');
            return;
        }

        // Show loading state
        this.setLoading('predict', true);
        document.getElementById('welcome-state')?.classList.add('hidden');
        document.getElementById('backtest-section')?.classList.add('hidden');
        
        // Hide upload data info when using symbol-based prediction
        this.hideUploadDataInfo();

        try {
            // Use NSE combined forecast API
            const response = await fetch('/api/nse/forecast/combined', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: symbol,
                    horizon: horizon,
                    garch_type: 'GARCH'
                })
            });
            
            const data = await response.json();

            if (data && !data.error) {
                this.displayNSEPrediction(data);
            } else {
                App.showError('alert-area', data.error || 'Prediction failed');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            App.showError('alert-area', `Prediction failed: ${error.message}`);
        } finally {
            this.setLoading('predict', false);
        }
    },

    /**
     * Display NSE prediction results
     */
    displayNSEPrediction(data) {
        const predictionSection = document.getElementById('prediction-section');
        predictionSection?.classList.remove('hidden');

        // Store last prediction
        this.lastPrediction = data;

        const vol = data.volatility_forecast || {};
        const price = data.price_forecast || {};

        // Update "Use in Calculator" button info
        const volValue = document.getElementById('use-calc-vol-value');
        const symbolEl = document.getElementById('use-calc-symbol');
        if (volValue && vol.historical_volatility_annual) {
            volValue.textContent = `${vol.historical_volatility_annual.toFixed(2)}%`;
        }
        if (symbolEl) symbolEl.textContent = data.name || data.symbol;

        // Update metrics
        const predictedVol = document.getElementById('predicted-vol');
        const predictedVolPct = document.getElementById('predicted-vol-pct');
        const confidenceInterval = document.getElementById('confidence-interval');
        const modelConfidence = document.getElementById('model-confidence');
        const modelVersion = document.getElementById('model-version');
        const predictionTime = document.getElementById('prediction-time');
        const horizonDays = document.getElementById('horizon-days');

        // Display volatility forecast
        if (predictedVol && vol.forecasted_volatility_annual && vol.forecasted_volatility_annual.length > 0) {
            const avgVol = vol.forecasted_volatility_annual.reduce((a, b) => a + b, 0) / vol.forecasted_volatility_annual.length;
            predictedVol.textContent = avgVol.toFixed(2) + '%';
        } else if (predictedVol && vol.historical_volatility_annual) {
            predictedVol.textContent = vol.historical_volatility_annual.toFixed(2) + '%';
        }
        
        if (predictedVolPct && vol.historical_volatility_daily) {
            predictedVolPct.textContent = `Daily: ${vol.historical_volatility_daily.toFixed(4)}%`;
        }
        
        // Confidence interval from price forecast
        if (confidenceInterval && price.confidence_interval_lower && price.confidence_interval_upper) {
            const lower = price.confidence_interval_lower[0]?.toFixed(2) || 'N/A';
            const upper = price.confidence_interval_upper[0]?.toFixed(2) || 'N/A';
            confidenceInterval.textContent = `KES ${lower} - ${upper}`;
        }

        if (modelConfidence) {
            modelConfidence.textContent = vol.model_type || 'GARCH';
        }

        if (modelVersion && vol.aic) {
            modelVersion.textContent = `AIC: ${vol.aic.toFixed(2)}`;
        }

        if (predictionTime && data.timestamp) {
            const date = new Date(data.timestamp);
            predictionTime.textContent = date.toLocaleString();
        }

        if (horizonDays && data.forecast_horizon) {
            horizonDays.textContent = `${data.forecast_horizon} periods ahead`;
        }

        // Display volatility forecasts as contributing models
        if (vol.forecasted_volatility_daily && vol.forecasted_volatility_annual) {
            const models = {};
            vol.forecasted_volatility_daily.forEach((v, i) => {
                models[`T+${i+1} Daily`] = v / 100;
            });
            this.displayContributingModels(models);
        }

        // Display price forecast info
        if (price.forecasted_prices) {
            this.displayPriceForecast(price);
        }

        // Clear any previous errors
        document.getElementById('alert-area').innerHTML = '';
    },

    /**
     * Display price forecast in contributing models section
     */
    displayPriceForecast(price) {
        const container = document.getElementById('contributing-models');
        if (!container) return;

        let html = `<div class="mb-4 pb-2 border-b border-gray-300 dark:border-gray-600">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Price Forecast (ARIMA)</h4>
            <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">Current: KES ${price.current_price?.toFixed(2) || 'N/A'}</div>
        </div>`;
        
        if (price.forecasted_prices) {
            price.forecasted_prices.forEach((p, i) => {
                const lower = price.confidence_interval_lower?.[i]?.toFixed(2) || 'N/A';
                const upper = price.confidence_interval_upper?.[i]?.toFixed(2) || 'N/A';
                html += `
                    <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700 last:border-0">
                        <span class="text-sm text-gray-700 dark:text-gray-300">T+${i+1}</span>
                        <span class="text-sm font-semibold text-green-600 dark:text-green-400">KES ${p.toFixed(2)}</span>
                        <span class="text-xs text-gray-500">[${lower} - ${upper}]</span>
                    </div>
                `;
            });
        }

        container.innerHTML = html;
    },

    /**
     * Fetch forecast time series
     */
    async fetchForecast(symbol, horizon) {
        try {
            // Show chart section and loading state
            const chartSection = document.getElementById('forecast-chart-section');
            const chartLoading = document.getElementById('forecast-chart-loading');
            const chartContainer = document.getElementById('forecast-chart');
            const chartError = document.getElementById('forecast-chart-error');

            if (chartSection) chartSection.classList.remove('hidden');
            if (chartLoading) chartLoading.classList.remove('hidden');
            if (chartContainer) chartContainer.classList.add('hidden');
            if (chartError) chartError.classList.add('hidden');

            const response = await API.volatility.getForecast(symbol, horizon);

            if (response.success && response.data) {
                // Format data for chart
                const chartData = this.formatForecastData(response.data);

                // Hide loading, show chart
                if (chartLoading) chartLoading.classList.add('hidden');
                if (chartContainer) chartContainer.classList.remove('hidden');

                // Render chart
                Charts.renderVolatilityForecast('forecast-chart', chartData);
            } else {
                throw new Error('Invalid forecast data');
            }
        } catch (error) {
            console.error('Forecast error:', error);

            // Show error state
            const chartLoading = document.getElementById('forecast-chart-loading');
            const chartContainer = document.getElementById('forecast-chart');
            const chartError = document.getElementById('forecast-chart-error');

            if (chartLoading) chartLoading.classList.add('hidden');
            if (chartContainer) chartContainer.classList.add('hidden');
            if (chartError) chartError.classList.remove('hidden');
        }
    },

    /**
     * Format forecast data for chart rendering
     */
    formatForecastData(data) {
        // Extract data from API response
        const historical = data.historical_volatility || {};
        const current = data.current_prediction || {};

        // Ensure confidence interval is properly ordered
        let upper = null;
        let lower = null;
        if (current.confidence_interval && Array.isArray(current.confidence_interval)) {
            const sorted = [...current.confidence_interval].sort((a, b) => a - b);
            lower = sorted[0];
            upper = sorted[1];
        }

        return {
            // Historical volatility data
            historical_dates: historical.timestamps || [],
            historical_volatility: historical.values || [],

            // Predicted volatility (single point or array)
            forecast_dates: [current.prediction_timestamp],
            predicted_volatility: [current.predicted_volatility],

            // Confidence intervals
            upper_bound: upper !== null ? [upper] : [],
            lower_bound: lower !== null ? [lower] : []
        };
    },

    /**
     * Display prediction results
     */
    displayPrediction(data) {
        const predictionSection = document.getElementById('prediction-section');
        predictionSection?.classList.remove('hidden');

        // Store last prediction for calculator integration
        this.lastPrediction = data;

        // Update "Use in Calculator" button info
        const volValue = document.getElementById('use-calc-vol-value');
        const symbolEl = document.getElementById('use-calc-symbol');
        if (volValue) volValue.textContent = `${(data.predicted_volatility * 100).toFixed(2)}%`;
        if (symbolEl) symbolEl.textContent = this.currentSymbol || data.symbol;

        // Update metrics
        const predictedVol = document.getElementById('predicted-vol');
        const predictedVolPct = document.getElementById('predicted-vol-pct');
        const confidenceInterval = document.getElementById('confidence-interval');
        const modelConfidence = document.getElementById('model-confidence');
        const modelVersion = document.getElementById('model-version');
        const predictionTime = document.getElementById('prediction-time');
        const horizonDays = document.getElementById('horizon-days');

        if (predictedVol) predictedVol.textContent = data.predicted_volatility.toFixed(6);
        if (predictedVolPct) predictedVolPct.textContent = `${(data.predicted_volatility * 100).toFixed(4)}%`;
        
        if (confidenceInterval && data.confidence_interval && Array.isArray(data.confidence_interval)) {
            // Ensure lower is always less than upper
            const values = [data.confidence_interval[0], data.confidence_interval[1]].sort((a, b) => a - b);
            const lower = (values[0] * 100).toFixed(4);
            const upper = (values[1] * 100).toFixed(4);
            confidenceInterval.textContent = `${lower}% - ${upper}%`;
        }

        if (modelConfidence && data.model_confidence) {
            modelConfidence.textContent = `${(data.model_confidence * 100).toFixed(2)}%`;
        }

        if (modelVersion && data.model_version) {
            modelVersion.textContent = `v${data.model_version}`;
        }

        if (predictionTime && data.prediction_timestamp) {
            const date = new Date(data.prediction_timestamp);
            predictionTime.textContent = date.toLocaleString();
        }

        if (horizonDays && data.horizon_days) {
            horizonDays.textContent = `${data.horizon_days} bars ahead`;
        }

        // Display contributing models
        if (data.contributing_models) {
            this.displayContributingModels(data.contributing_models);
        }

        // Clear any previous errors
        document.getElementById('alert-area').innerHTML = '';
    },

    /**
     * Display contributing models breakdown
     */
    displayContributingModels(models) {
        const container = document.getElementById('contributing-models');
        if (!container) return;

        const html = Object.entries(models).map(([name, value]) => `
            <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700 last:border-0">
                <span class="text-sm text-gray-700 dark:text-gray-300">${name}</span>
                <span class="text-sm font-semibold text-blue-600 dark:text-blue-400">${(value * 100).toFixed(4)}%</span>
            </div>
        `).join('');

        container.innerHTML = html;
    },

    /**
     * Run backtest
     */
    async backtest() {
        const symbol = document.getElementById('symbol').value;
        const horizon = parseInt(document.getElementById('horizon').value);

        if (!symbol) {
            App.showError('alert-area', 'Please select a symbol');
            return;
        }

        // Show loading state
        this.setLoading('backtest', true);
        document.getElementById('welcome-state')?.classList.add('hidden');
        document.getElementById('prediction-section')?.classList.add('hidden');

        try {
            const response = await API.volatility.backtest({
                symbol: symbol,
                horizon: horizon,
                test_days: 30  // Last 30 days
            });

            if (response.success && response.data) {
                this.displayBacktest(response.data);
            } else {
                App.showError('alert-area', response.message || 'Backtest failed');
            }
        } catch (error) {
            console.error('Backtest error:', error);
            App.showError('alert-area', `Backtest failed: ${error.message}`);
        } finally {
            this.setLoading('backtest', false);
        }
    },

    /**
     * Display backtest results
     */
    displayBacktest(data) {
        const backtestSection = document.getElementById('backtest-section');
        backtestSection?.classList.remove('hidden');

        // Hide prediction and chart sections
        document.getElementById('prediction-section')?.classList.add('hidden');
        document.getElementById('forecast-chart-section')?.classList.add('hidden');

        // Update metrics
        const accuracy = document.getElementById('backtest-accuracy');
        const auc = document.getElementById('backtest-auc');
        const totalPreds = document.getElementById('backtest-total-preds');
        const testPeriod = document.getElementById('backtest-period');
        const winRate = document.getElementById('backtest-winrate');
        const sharpe = document.getElementById('backtest-sharpe');
        const totalReturn = document.getElementById('backtest-return');
        const maxDD = document.getElementById('backtest-maxdd');

        if (accuracy && data.metrics) {
            accuracy.textContent = `${(data.metrics.accuracy * 100).toFixed(2)}%`;
        }
        if (auc && data.metrics) {
            auc.textContent = data.metrics.test_auc.toFixed(4);
        }
        if (totalPreds && data.metrics) {
            totalPreds.textContent = data.metrics.total_predictions.toLocaleString();
        }
        if (testPeriod && data.test_period) {
            const start = new Date(data.test_period.start).toLocaleDateString();
            const end = new Date(data.test_period.end).toLocaleDateString();
            testPeriod.textContent = `${start} - ${end}`;
        }

        // Display detailed backtest metrics if available
        if (data.model_info && data.model_info.metrics && data.model_info.metrics.backtest_metrics) {
            const bt = data.model_info.metrics.backtest_metrics;
            if (winRate) winRate.textContent = `${(bt.win_rate * 100).toFixed(2)}%`;
            if (sharpe) sharpe.textContent = bt.sharpe.toFixed(2);
            if (totalReturn) totalReturn.textContent = `$${bt.total_return.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            if (maxDD) maxDD.textContent = `$${bt.max_dd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        // Display model info
        if (data.model_info) {
            this.displayBacktestModelInfo(data.model_info);
        }

        // Clear any previous errors
        document.getElementById('alert-area').innerHTML = '';
    },

    /**
     * Display backtest model information
     */
    displayBacktestModelInfo(modelInfo) {
        const container = document.getElementById('backtest-model-info');
        if (!container) return;

        const config = modelInfo.config || {};
        const html = `
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">Best Model</div>
                    <div class="text-sm font-semibold text-gray-900 dark:text-white">${modelInfo.best_model || 'N/A'}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">Features</div>
                    <div class="text-sm font-semibold text-gray-900 dark:text-white">${modelInfo.n_features || 'N/A'}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">Bar Frequency</div>
                    <div class="text-sm font-semibold text-gray-900 dark:text-white">${config.bar_freq || 'N/A'}</div>
                </div>
                <div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">Horizon</div>
                    <div class="text-sm font-semibold text-gray-900 dark:text-white">${config.horizon || 'N/A'} bars</div>
                </div>
            </div>
        `;
        container.innerHTML = html;
    },

    /**
     * Set loading state for buttons
     */
    setLoading(type, isLoading) {
        // Handle special case for upload button which has different ID pattern
        const btnId = type === 'upload' ? 'upload-predict-btn' : `${type}-btn`;
        const btn = document.getElementById(btnId);
        const btnText = document.getElementById(`${type}-btn-text`);
        const spinner = document.getElementById(`${type}-spinner`);

        if (btn) btn.disabled = isLoading;
        if (spinner) {
            if (isLoading) {
                spinner.classList.remove('hidden');
            } else {
                spinner.classList.add('hidden');
            }
        }
    },

    /**
     * Save preferences to localStorage
     */
    savePreferences() {
        const preferences = {
            symbol: document.getElementById('symbol').value,
            horizon: document.getElementById('horizon').value,
            confidence: document.getElementById('confidence').value
        };
        localStorage.setItem('nse_volatility_preferences', JSON.stringify(preferences));
    },

    /**
     * Load preferences from localStorage
     */
    loadPreferences() {
        const saved = localStorage.getItem('nse_volatility_preferences');
        if (saved) {
            try {
                const preferences = JSON.parse(saved);
                
                const symbolSelect = document.getElementById('symbol');
                const horizonInput = document.getElementById('horizon');
                const confidenceSlider = document.getElementById('confidence');
                const confidenceDisplay = document.getElementById('confidence-display');

                if (preferences.symbol && symbolSelect) symbolSelect.value = preferences.symbol;
                if (preferences.horizon && horizonInput) horizonInput.value = preferences.horizon;
                if (preferences.confidence && confidenceSlider) {
                    confidenceSlider.value = preferences.confidence;
                    if (confidenceDisplay) confidenceDisplay.textContent = preferences.confidence;
                }
            } catch (error) {
                console.error('Error loading preferences:', error);
            }
        }
    }
};

// Export to window
window.VolatilityForecast = VolatilityForecast;

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => VolatilityForecast.init());
} else {
    VolatilityForecast.init();
}
