# Quick Start Guide - NSE Options Pricer (Flask Edition)

## ✅ Fixed Issues

The application had Streamlit dependencies in legacy files. These have been resolved:

1. **Chatbot Service**: Rewritten to use OpenAI directly (no Streamlit dependency)
2. **PnL Service**: Standalone implementation (no pnl_analysis.py imports)

---

## 🚀 Start the Application

### Option 1: Using the startup script (Recommended)

```bash
# From the project root
./run.sh
```

The app will start on **port 5001** (since 5000 is often used by AirPlay on macOS).

### Option 2: Manual start

```bash
# Set environment variables
export FLASK_PORT=5001

# Run the app
python flask_app.py
```

### Option 3: Custom port

```bash
FLASK_PORT=8000 python flask_app.py
```

---

## 🌐 Access the Application

Once started, visit:

- **Main App**: http://localhost:5001
- **API Documentation**: http://localhost:5001/api/doc

---

## 📋 Quick Navigation

| Page | URL | Description |
|------|-----|-------------|
| Option Calculator | http://localhost:5001/ | Black-76 pricing with heatmaps |
| PnL Predictor | http://localhost:5001/pnl | Strategy analysis (4 tabs) |
| Flavia AI Chatbot | http://localhost:5001/chatbot | AI assistant |
| Settings | http://localhost:5001/settings | Theme & data management |
| API Docs | http://localhost:5001/api/doc | Swagger UI |

---

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Required for chatbot
OPENAI_API_KEY=your_openai_api_key_here

# Optional
FLASK_PORT=5001
FLASK_ENV=development
SECRET_KEY=your-secret-key
NSE_DATA_FILE=/Users/mac/Downloads/Ahona_Amanda_Derivatives_Price_Lists_2025.csv
```

### Without OpenAI API Key

The app will work fine without an API key, but the chatbot won't function. All other features (calculator, PnL, market data) work independently.

---

## 🧪 Test the Features

### 1. Option Calculator
1. Go to http://localhost:5001
2. Adjust:
   - Futures Price: 100
   - Strike Price: 105
   - Volatility: 30%
3. See real-time calculations and heatmaps

### 2. PnL Predictor (NEW!)
1. Go to http://localhost:5001/pnl
2. Try each tab:
   - **Strategy Builder**: Select "Long Call" → Calculate
   - **Custom Position**: Add a call leg → Add a put leg → Calculate
   - **Compare**: Select 2+ strategies → Compare
   - **Scenario**: Select strategy → Analyze

### 3. Chatbot
1. Go to http://localhost:5001/chatbot
2. Click a suggested question or type your own
3. Get AI responses about options trading

### 4. API Testing
1. Go to http://localhost:5001/api/doc
2. Expand `/api/pricing/calculate`
3. Click "Try it out"
4. Fill in parameters and execute

---

## 🔧 Troubleshooting

### Error: "Address already in use"
**Solution**: Port 5000 is used by AirPlay. Use the startup script or set `FLASK_PORT=5001`

```bash
FLASK_PORT=5001 python flask_app.py
```

### Error: "OPENAI_API_KEY not found"
**Solution**: Either:
1. Add to `.env` file: `OPENAI_API_KEY=sk-...`
2. Export in terminal: `export OPENAI_API_KEY=sk-...`
3. Use app without chatbot (all other features work)

### Error: "Module not found"
**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

### Streamlit warnings on startup
**Solution**: These can be ignored. They occur because some legacy files import Streamlit, but the Flask app doesn't use them.

```
WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext!
```

Just ignore these warnings - the Flask app works perfectly without Streamlit.

---

## 📊 API Endpoints Quick Reference

### Pricing
```bash
# Calculate option price
curl -X POST http://localhost:5001/api/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{"futures_price": 100, "strike_price": 105, "days_to_expiry": 30, "volatility": 0.20, "risk_free_rate": 0.12}'

# Get contracts
curl http://localhost:5001/api/pricing/contracts
```

### Market
```bash
# Market status
curl http://localhost:5001/api/market/status

# Futures data
curl http://localhost:5001/api/market/futures
```

### Chat
```bash
# Send message
curl -X POST http://localhost:5001/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "How does volatility affect options?"}'

# Get suggestions
curl http://localhost:5001/api/chat/suggestions
```

### PnL
```bash
# Get strategies
curl http://localhost:5001/api/pnl/strategies

# Build strategy
curl -X POST http://localhost:5001/api/pnl/strategy-builder \
  -H "Content-Type: application/json" \
  -d '{"strategy_name": "long_call", "parameters": {"spot_price": 100, "strike": 105, "premium": 5}}'
```

---

## 🎨 Features Showcase

### Dark Mode
- Click moon/sun icon in top-right nav bar
- Or go to Settings → Toggle theme
- Persisted to localStorage

### Real-time Calculations
- All inputs update calculations instantly
- Debounced for performance (500ms delay)
- Results cached in browser

### Interactive Charts
- Hover for tooltips
- Zoom and pan
- Download as PNG
- Responsive sizing

### Data Persistence
- Calculator inputs saved to localStorage
- Chat history preserved
- Custom PnL legs stored
- Theme preference remembered

---

## 🚢 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 flask_app:app
```

### Environment Variables for Production

```bash
FLASK_ENV=production
SECRET_KEY=<generate-random-secret-key>
OPENAI_API_KEY=<your-key>
```

---

## ✨ What's New vs Streamlit

| Feature | Streamlit | Flask |
|---------|-----------|-------|
| PnL Predictor | ❌ | ✅ 4 tabs |
| API | ❌ | ✅ REST + Swagger |
| Mobile | Limited | ✅ Responsive |
| Dark Mode | Basic | ✅ Full support |
| State | Server | localStorage |
| Performance | Slower | ⚡ Faster |

---

**Enjoy your new Flask-based NSE Options Pricer!** 🎉

For detailed documentation, see [README_FLASK.md](README_FLASK.md)
