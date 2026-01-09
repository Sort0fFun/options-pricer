# NSE Options Pricer - Flask Edition

Complete Flask + HTML/Tailwind CSS migration from Streamlit.

## 🎉 Migration Complete!

The NSE Options Pricer has been successfully converted from Streamlit to a modern Flask-based web application with:
- **Backend**: Flask with Flask-RESTX (automatic Swagger API documentation)
- **Frontend**: Vanilla JavaScript + Tailwind CSS (no build process required)
- **Charts**: Plotly.js for interactive visualizations
- **All existing Python logic preserved**: Black-76 pricing, chatbot, PnL analysis

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create or update your `.env` file:

```bash
# Required for chatbot
OPENAI_API_KEY=your_openai_api_key_here

# Optional configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here
```

### 3. Run the Application

```bash
python flask_app.py
```

The application will be available at: **http://localhost:5000**

API Documentation (Swagger UI) at: **http://localhost:5000/api/doc**

---

## 📁 Project Structure

```
options-pricer/
├── flask_app.py                    # Main application entry point
├── config.py                       # Configuration classes
├── requirements.txt                # Python dependencies
│
├── backend/                        # Flask backend
│   ├── __init__.py                # App factory
│   ├── routes.py                  # Page routes
│   │
│   ├── api/                       # REST API endpoints
│   │   ├── __init__.py           # Flask-RESTX setup
│   │   ├── pricing.py            # Pricing API
│   │   ├── market.py             # Market data API
│   │   ├── chatbot.py            # Chatbot API
│   │   └── pnl.py                # PnL analysis API
│   │
│   ├── services/                  # Business logic
│   │   ├── pricing_service.py    # Black-76 pricing wrapper
│   │   ├── market_service.py     # Market data service
│   │   ├── chatbot_service.py    # Flavia AI wrapper
│   │   └── pnl_service.py        # PnL analysis wrapper
│   │
│   └── models/                    # Pydantic validation models
│       ├── pricing_models.py
│       ├── chatbot_models.py
│       └── pnl_models.py
│
├── frontend/                      # Frontend assets
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base template
│   │   ├── index.html            # Option calculator
│   │   ├── pnl.html              # PnL predictor (NEW!)
│   │   ├── chatbot.html          # Flavia AI
│   │   └── settings.html         # Settings
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css        # Custom styles
│       │
│       └── js/
│           ├── api.js            # API client
│           ├── app.js            # Main controller
│           │
│           ├── components/       # Page components
│           │   ├── calculator.js
│           │   ├── charts.js
│           │   ├── chatbot.js
│           │   └── pnl.js
│           │
│           └── utils/            # Utilities
│               ├── storage.js
│               ├── theme.js
│               └── format.js
│
└── src/core/                     # Preserved core modules
    └── pricing/
        ├── black76.py            # Black-76 model (unchanged)
        └── contracts.py          # NSE contracts (unchanged)
```

---

## 🌟 Features

### 1. **Option Calculator** (`/`)
- **Black-76 pricing model** for call and put options
- Real-time calculations with input synchronization
- Interactive **Plotly heatmaps** (Call & Put price surfaces)
- NSE market fees calculation and breakdown
- NSE Futures Market Overview table
- **localStorage persistence** for inputs

### 2. **PnL Predictor** (`/pnl`) - ✨ NEW FEATURE!
Four comprehensive tabs:

#### Tab 1: Strategy Builder
- 9 pre-built strategies:
  - Long Call, Long Put
  - Bull Call Spread, Bear Put Spread
  - Long Straddle, Long Strangle
  - Iron Condor, Butterfly Spread, Covered Call
- Dynamic parameter forms
- P&L diagram with breakeven markers
- Metrics: Max profit, max loss, breakeven points

#### Tab 2: Custom Position
- Build multi-leg custom strategies
- Add/remove individual legs
- Full P&L analysis with net cost calculation
- localStorage persistence for custom legs

#### Tab 3: Compare Strategies
- Side-by-side comparison of up to 4 strategies
- Multi-line overlay chart
- Quick strategy comparison

#### Tab 4: Scenario Analysis
- Volatility impact analysis
- Time decay scenarios
- Visual P&L comparison

### 3. **Flavia AI Chatbot** (`/chatbot`)
- OpenAI GPT-4o-mini integration
- 10 suggested questions
- Conversation history with localStorage
- Export conversations to JSON
- Dark mode support

### 4. **Settings** (`/settings`)
- Light/Dark theme toggle
- Data management (clear calculator, chat, or all data)
- Application information

---

## 🔌 API Endpoints

### Pricing API (`/api/pricing`)

**POST /api/pricing/calculate**
```json
{
  "futures_price": 100.0,
  "strike_price": 105.0,
  "days_to_expiry": 30,
  "volatility": 0.20,
  "risk_free_rate": 0.12,
  "option_type": "call",
  "include_fees": false
}
```

**POST /api/pricing/heatmap**
Generate heatmap data for visualization.

**GET /api/pricing/contracts**
Get NSE futures contracts list.

### Market API (`/api/market`)

**GET /api/market/status**
Real-time NSE market status (OPEN/CLOSED with countdown).

**GET /api/market/futures?contracts=SCOM,EQTY**
Filtered NSE futures data from CSV.

### Chatbot API (`/api/chat`)

**POST /api/chat/message**
```json
{
  "message": "How does volatility affect options?",
  "context": {}
}
```

**GET /api/chat/suggestions**
Get 10 suggested questions.

**POST /api/chat/clear**
Clear server-side conversation.

### PnL API (`/api/pnl`)

**POST /api/pnl/analyze**
Analyze custom multi-leg strategy.

**POST /api/pnl/strategy-builder**
Build and analyze pre-defined strategy.

**GET /api/pnl/strategies**
List available strategies.

---

## 🎨 Styling & Theming

### NSE Color Palette
```javascript
{
  nse: {
    primary: '#1A4D2E',
    secondary: '#2E8B57',
    light: '#4ADE80',
    dark: '#0D261F',
    accent: '#E8F5E9'
  }
}
```

### Dark Mode
- Toggle in navigation bar or settings
- Persisted to localStorage
- Tailwind CSS `dark:` classes throughout

---

## 🗄️ Data Storage

### localStorage Keys
- `nse_theme` - Theme preference (light/dark)
- `nse_chat_history` - Flavia AI conversation history
- `nse_calculator_inputs` - Calculator input values
- `nse_pnl_legs` - Custom PnL strategy legs
- `nse_settings` - Application settings

---

## 🚢 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 flask_app:app
```

### Environment Variables for Production

```bash
FLASK_ENV=production
SECRET_KEY=<generate-strong-secret-key>
OPENAI_API_KEY=<your-key>
NSE_DATA_FILE=/path/to/derivatives/data.csv
```

### WSGI Configuration

The app is WSGI-compatible. Use `flask_app:app` as the application object.

---

## 📊 Preserved Core Modules

All existing Python logic has been preserved and wrapped in services:

### Black-76 Pricing
- **File**: `src/core/pricing/black76.py` (394 lines, **unchanged**)
- **Wrapper**: `backend/services/pricing_service.py`
- Functions: `price_call()`, `price_put()`, `calculate_intrinsic_value()`

### NSE Contracts
- **File**: `src/core/pricing/contracts.py` (111 lines, **unchanged**)
- Contains `NSE_FUTURES` dictionary with 13 contracts

### Flavia AI Chatbot
- **File**: `src/web/chatbot.py` (292 lines, **unchanged**)
- **Wrapper**: `backend/services/chatbot_service.py`
- Class: `FlaviaAIBot` with OpenAI integration

### PnL Analysis
- **File**: `pnl_analysis.py` (705 lines, **unchanged**)
- **Wrapper**: `backend/services/pnl_service.py`
- Classes: `PnLAnalyzer`, `StrategyBuilder`

---

## 🔍 API Documentation

Swagger UI with full API documentation is automatically generated and available at:

**http://localhost:5000/api/doc**

Features:
- Interactive API testing
- Request/response schemas
- Endpoint descriptions
- Try it out functionality

---

## 🆚 Streamlit vs Flask Comparison

| Feature | Streamlit | Flask Edition |
|---------|-----------|---------------|
| **Architecture** | Monolithic (1,202 lines) | Modular (40+ files) |
| **UI Framework** | Streamlit widgets | HTML + Tailwind CSS |
| **API** | None | RESTful with Swagger docs |
| **State Management** | st.session_state | localStorage + Flask session |
| **Charts** | Plotly (embedded) | Plotly.js (client-side) |
| **PnL Predictor** | ❌ Not implemented | ✅ Full 4-tab interface |
| **API Documentation** | ❌ None | ✅ Auto-generated Swagger |
| **Mobile Responsive** | Limited | Fully responsive |
| **Build Process** | None | None (CDN-based) |

---

## 🧪 Testing the Application

### 1. Test Option Calculator
1. Navigate to http://localhost:5000
2. Adjust parameters (futures price, strike, volatility, etc.)
3. Observe real-time calculations
4. Check heatmaps render correctly

### 2. Test PnL Predictor
1. Navigate to http://localhost:5000/pnl
2. **Strategy Builder**: Select "Long Call", calculate P&L
3. **Custom Position**: Add 2-3 legs, calculate custom strategy
4. **Compare**: Select 2+ strategies, compare visually
5. **Scenario**: Run scenario analysis

### 3. Test Chatbot
1. Navigate to http://localhost:5000/chatbot
2. Send a message or click a suggestion
3. Verify response from Flavia AI
4. Export conversation to JSON

### 4. Test API Directly
Visit http://localhost:5000/api/doc and try the endpoints in Swagger UI.

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Chatbot not responding
**Solution**: Check OPENAI_API_KEY in `.env` file
```bash
echo $OPENAI_API_KEY  # Should output your key
```

### Issue: Market data not loading
**Solution**: Verify NSE_DATA_FILE path in `config.py` or set in `.env`
```bash
NSE_DATA_FILE=/Users/mac/Downloads/Ahona_Amanda_Derivatives_Price_Lists_2025.csv
```

### Issue: Charts not rendering
**Solution**: Check browser console for JavaScript errors. Ensure Plotly.js CDN is accessible.

### Issue: Dark mode not working
**Solution**: Clear localStorage and refresh:
```javascript
localStorage.clear();
location.reload();
```

---

## ✅ Success Criteria (All Met!)

- ✅ All 4 pages functional (Calculator, PnL, Chatbot, Settings)
- ✅ Real-time pricing calculations with heatmaps
- ✅ Chat interface with localStorage persistence
- ✅ PnL Predictor with 4 tabs fully implemented
- ✅ Dark/Light theme toggle working
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ API documentation auto-generated (Swagger UI)
- ✅ No Streamlit dependencies remaining
- ✅ All existing Python logic preserved and functional

---

## 📝 Next Steps (Optional Enhancements)

1. **Database Integration**: Replace CSV with PostgreSQL for market data
2. **User Authentication**: Add login/registration for multi-user support
3. **Real-time Updates**: Implement WebSocket for live market data
4. **Enhanced Charts**: Add technical indicators to price charts
5. **Mobile App**: Create React Native app using the REST API
6. **Backtesting**: Add historical P&L backtesting features
7. **Alerts**: Email/SMS notifications for price targets

---

## 📄 License

© 2026 NSE Options Pricer. All rights reserved.

---

## 🙏 Acknowledgments

- **Black-76 Model**: Fischer Black (1976)
- **NSE**: Nairobi Securities Exchange
- **OpenAI**: GPT-4o-mini for Flavia AI
- **Plotly**: Interactive charting library
- **Flask & Tailwind CSS**: Modern web framework and styling

---

**Enjoy your new Flask-based NSE Options Pricer! 🚀**
