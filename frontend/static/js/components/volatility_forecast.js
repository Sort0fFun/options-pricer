/**
 * Volatility Forecasting component.
 */

const VolatilityForecast = {
    currentSymbol: null,
    modelInfo: null,
    selectedFile: null,

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
     * Load model information
     */
    async loadModelInfo() {
        try {
            const response = await API.volatility.getModelInfo();
            if (response.success && response.data) {
                this.modelInfo = response.data;
                this.updateModelInfo();
            }
        } catch (error) {
            console.error('Error loading model info:', error);
            App.showError('alert-area', 'Failed to load model information');
        }
    },

    /**
     * Load available symbols
     */
    async loadSymbols() {
        const symbolSelect = document.getElementById('symbol');
        try {
            const response = await API.volatility.getSymbols();
            if (response.success && response.data && response.data.symbols) {
                symbolSelect.innerHTML = response.data.symbols.map(symbol =>
                    `<option value="${symbol}">${symbol}</option>`
                ).join('');
                
                // Select first symbol by default
                if (response.data.symbols.length > 0) {
                    this.currentSymbol = response.data.symbols[0];
                }
            } else {
                // Fallback to common NSE futures symbols
                const defaultSymbols = ['ESZ4', 'NQZ4', 'RTY', 'YM'];
                symbolSelect.innerHTML = defaultSymbols.map(symbol =>
                    `<option value="${symbol}">${symbol}</option>`
                ).join('');
                this.currentSymbol = defaultSymbols[0];
            }
        } catch (error) {
            console.error('Error loading symbols:', error);
            // Use fallback symbols
            const defaultSymbols = ['ESZ4', 'NQZ4', 'RTY', 'YM'];
            symbolSelect.innerHTML = defaultSymbols.map(symbol =>
                `<option value="${symbol}">${symbol}</option>`
            ).join('');
            this.currentSymbol = defaultSymbols[0];
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
     * Update model information display
     */
    updateModelInfo() {
        if (!this.modelInfo) return;

        const modelName = document.getElementById('model-name');
        const modelFeatures = document.getElementById('model-features');
        const modelTrained = document.getElementById('model-trained');
        const featureImportance = document.getElementById('feature-importance');

        if (modelName) modelName.textContent = this.modelInfo.model_type || 'Unknown';
        if (modelFeatures) modelFeatures.textContent = this.modelInfo.num_features || '-';
        if (modelTrained) modelTrained.textContent = this.modelInfo.trained_date || '-';

        // Display top features
        if (featureImportance && this.modelInfo.top_features) {
            featureImportance.innerHTML = this.modelInfo.top_features.slice(0, 10).map((feature, idx) =>
                `<div class="flex justify-between text-gray-700 dark:text-gray-300">
                    <span>${idx + 1}. ${feature.name}</span>
                    <span class="font-medium">${(feature.importance * 100).toFixed(2)}%</span>
                </div>`
            ).join('');
        }
    },

    /**
     * Get prediction
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
            const response = await API.volatility.predict({
                symbol: symbol,
                horizon: horizon,
                confidence_level: confidence
            });

            if (response.success && response.data) {
                this.displayPrediction(response.data);
                
                // Also fetch forecast time series
                await this.fetchForecast(symbol, horizon);
            } else {
                App.showError('alert-area', response.message || 'Prediction failed');
            }
        } catch (error) {
            console.error('Prediction error:', error);
            App.showError('alert-area', `Prediction failed: ${error.message}`);
        } finally {
            this.setLoading('predict', false);
        }
    },

    /**
     * Fetch forecast time series
     */
    async fetchForecast(symbol, horizon) {
        try {
            const response = await API.volatility.getForecast(symbol, horizon);
            if (response.success && response.data) {
                Charts.renderVolatilityForecast('forecast-chart', response.data);
            }
        } catch (error) {
            console.error('Forecast error:', error);
        }
    },

    /**
     * Display prediction results
     */
    displayPrediction(data) {
        const predictionSection = document.getElementById('prediction-section');
        predictionSection?.classList.remove('hidden');

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
            const lower = (data.confidence_interval[0] * 100).toFixed(4);
            const upper = (data.confidence_interval[1] * 100).toFixed(4);
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
