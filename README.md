# 🇰🇪 NSE Options Pricing Tool

A comprehensive web-based options pricing and analysis tool specifically designed for the Nairobi Securities Exchange (NSE) derivatives market. This tool combines traditional Black-76 pricing models with modern machine learning techniques to provide accurate options valuation and risk analysis.

## 🌟 Features

### 💰 Core Options Pricing
- **Black-76 Model Implementation**: Accurate pricing for European-style options on futures
- **Real-time Calculations**: Instant pricing updates as parameters change
- **NSE Contract Support**: SCOM, KCB, EQTY, ABSA, NSE25, Mini NSE25
- **Input Validation**: Comprehensive error checking and user guidance

### 📊 Greeks Analysis
- **Complete Risk Metrics**: Delta, Gamma, Vega, Theta, Rho, Lambda
- **Interactive Visualizations**: Charts showing Greeks vs underlying price
- **Portfolio Greeks**: Aggregate risk analysis for multiple positions
- **Educational Explanations**: Built-in help for understanding each Greek

### 🤖 Machine Learning Integration
- **GARCH Volatility Models**: Traditional volatility clustering prediction
- **LSTM Neural Networks**: Advanced deep learning for volatility forecasting
- **Ensemble Methods**: Combines multiple models for improved accuracy
- **Model Performance Tracking**: Backtesting and validation metrics

### 🔧 Strategy Analysis
- **Multi-leg Strategies**: Build and analyze complex option strategies
- **Payoff Diagrams**: Visual representation of strategy outcomes
- **Risk/Reward Analysis**: Comprehensive strategy evaluation
- **Breakeven Calculations**: Automatic breakeven point identification

### 📈 Market Data Simulation
- **Realistic NSE Data**: Simulated market data with local characteristics
- **Regime Switching**: Bull, bear, volatile, and crisis market scenarios
- **Correlation Modeling**: Multi-asset correlated price movements
- **Educational Scenarios**: Controlled environments for learning

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd options_pricer
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

4. **Open in browser**: The app will automatically open at `http://localhost:8501`

### Basic Usage

1. **Select a Contract**: Choose from NSE futures contracts (SCOM, KCB, etc.)
2. **Input Parameters**: Set futures price, strike price, time to expiry, volatility, and interest rate
3. **Choose Option Type**: Select Call or Put option
4. **View Results**: Get instant pricing and Greeks analysis
5. **Explore Strategies**: Build multi-leg strategies and analyze payoffs

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [`DOC_PRICING_ENGINE.md`](docs/DOC_PRICING_ENGINE.md) - Black-76 pricing model implementation
- [`DOC_GREEKS_ENGINE.md`](docs/DOC_GREEKS_ENGINE.md) - Risk sensitivities calculation
- [`DOC_VOLATILITY_ML.md`](docs/DOC_VOLATILITY_ML.md) - Machine learning volatility prediction
- [`DOC_STREAMLIT_APP.md`](docs/DOC_STREAMLIT_APP.md) - Web application architecture
- [`DOC_DATA_SIMULATION.md`](docs/DOC_DATA_SIMULATION.md) - Market data simulation

## 🏗️ Architecture

### Project Structure
```
options_pricer/
├── src/
│   ├── core/           # Core pricing and Greeks engines
│   ├── ml/             # Machine learning models
│   ├── data/           # Data simulation and utilities
│   ├── web/            # Web application components
│   └── visualization/  # Plotting and charting tools
├── docs/               # Comprehensive documentation
├── tests/              # Unit and integration tests
├── config/             # Configuration files
└── app.py              # Main Streamlit application
```

### Technology Stack
- **Backend**: Python 3.9+, NumPy, SciPy, pandas
- **Machine Learning**: scikit-learn, TensorFlow, statsmodels, arch
- **Web Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib
- **Data Handling**: pandas, NumPy

## 🎯 NSE Market Focus

### Supported Contracts
- **SCOM**: Safaricom PLC (Telecommunications)
- **KCB**: KCB Group PLC (Banking)
- **EQTY**: Equity Group Holdings PLC (Banking)
- **ABSA**: Absa Bank Kenya PLC (Banking)
- **NSE25**: NSE 25 Share Index
- **MNSE25**: Mini NSE 25 Share Index

### Market Conventions
- **Currency**: Kenyan Shilling (KES)
- **Trading Hours**: 9:00 AM - 3:00 PM EAT
- **Expiry Cycle**: Quarterly (March, June, September, December)
- **Settlement**: Cash-settled options
- **Style**: European exercise

### Educational Features
- **Local Context**: Uses Kenyan market data and conventions
- **CBK Rate Integration**: Central Bank of Kenya policy rate defaults
- **Currency Formatting**: Proper KES currency display
- **Holiday Calendar**: Kenyan public holidays consideration

## 🧪 Testing and Validation

### Model Validation
- **Theoretical Verification**: Pricing results validated against known models
- **Numerical Accuracy**: High precision mathematical implementations
- **Edge Case Handling**: Robust error handling for extreme inputs
- **Performance Testing**: Optimized for real-time calculations

### Educational Validation
- **Student Testing**: Validated with finance students and educators
- **User Experience**: Intuitive interface design
- **Learning Progression**: Structured from basic to advanced features

## 🤝 Contributing

This project is designed for educational and research purposes. Contributions are welcome!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **Documentation**: Comprehensive docstrings for all functions
- **Testing**: Unit tests for all new functionality
- **Comments**: Clear explanations for complex calculations

## 📊 Performance Metrics

### Calculation Speed
- **Single Option Pricing**: < 1ms
- **Greeks Calculation**: < 5ms
- **Strategy Analysis**: < 100ms
- **ML Volatility Prediction**: < 1s

### Accuracy Targets
- **Pricing Accuracy**: Within 0.01% of theoretical values
- **Greeks Precision**: 6 decimal places for most metrics
- **Volatility Prediction**: Target 70%+ directional accuracy

## ⚠️ Important Disclaimers

### Educational Purpose
This tool is designed for **educational and research purposes only**. It should not be used as the sole basis for actual trading decisions.

### Market Data
- All market data shown is **simulated** unless otherwise specified
- Real NSE data integration requires proper licenses and API access
- Pricing models are theoretical and may not reflect actual market conditions

### Risk Warning
- Options trading involves significant risk of loss
- Past performance does not guarantee future results
- Consult with qualified financial advisors before making investment decisions

### Regulatory Compliance
- This tool does not provide investment advice
- Users are responsible for compliance with local regulations
- Educational use only - not for commercial trading

## 📞 Support and Contact

### Documentation
- Complete API documentation in `docs/` directory
- Interactive tutorials within the application
- Code examples and use cases

### Issues and Feedback
- Report bugs and issues through GitHub Issues
- Feature requests welcome
- Educational feedback particularly valuable

### Academic Collaboration
- Open to collaboration with educational institutions
- Research partnerships welcome
- Student project contributions encouraged

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 Acknowledgments

### Educational Institutions
- Strathmore Business School (NSE derivatives research)
- University of Nairobi (Finance department feedback)
- Technical University of Kenya (Software development support)

### Market Data Sources
- Nairobi Securities Exchange (Market structure information)
- Central Bank of Kenya (Interest rate data)
- Capital Markets Authority (Regulatory guidance)

### Technical References
- Fischer Black (1976) - Original Black-76 model
- Hull, John C. - Options, Futures, and Other Derivatives
- Wilmott, Paul - Paul Wilmott Introduces Quantitative Finance

---

**Built with ❤️ for the Kenyan financial markets community**

*Empowering the next generation of quantitative finance professionals in East Africa*