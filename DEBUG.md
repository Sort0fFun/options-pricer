# Debugging Guide - NSE Options Pricer

## 🔍 Quick Diagnosis

### Step 1: Test the Flask App

Run the test script to verify everything works:

```bash
cd /Users/mac/projects/options-pricer
venv/bin/python test_app.py
```

**Expected output:**
```
============================================================
Testing Flask App Startup
============================================================

1. Importing Flask app...
✓ Import successful!

2. Creating app instance...
✓ App created successfully!

3. Checking registered routes...
   (list of routes...)

4. Testing API endpoints...
   Testing GET /api/pricing/contracts...
   Status: 200
   ✓ Contracts endpoint works!

============================================================
All tests passed! You can now run: ./run.sh
============================================================
```

If you see errors here, they'll point to the exact problem.

---

### Step 2: Start the Flask App

```bash
./run.sh
```

**Expected output:**
```
========================================
NSE Options Pricer - Flask Edition
========================================

Starting Flask app on port 5001...
Once started, visit: http://localhost:5001

Press CTRL+C to stop the server
----------------------------------------

 * Serving Flask app 'backend'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

---

### Step 3: Test in Browser

Open your browser and go to:

1. **Main Page**: http://localhost:5001/
2. **API Docs**: http://localhost:5001/api/doc

---

## 🐛 Common Issues & Fixes

### Issue 1: "Heatmaps not showing"

**Symptoms**:
- Page loads but heatmaps are blank
- JavaScript console shows errors

**Fix**: Open browser developer console (F12) and check for errors:

```javascript
// Common errors:
// 1. "Failed to fetch" - API endpoint not working
// 2. "Plotly is not defined" - CDN blocked
// 3. "Cannot read property of undefined" - Data format issue
```

**Solutions**:
1. Check API is responding:
   ```bash
   curl http://localhost:5001/api/pricing/contracts
   ```
   Should return JSON with contract list.

2. Check Plotly CDN loads:
   - Open DevTools → Network tab
   - Look for `plotly-2.27.0.min.js`
   - If blocked, check internet connection

3. Clear browser cache:
   ```
   CTRL+Shift+R (Windows/Linux)
   CMD+Shift+R (Mac)
   ```

---

### Issue 2: "API returns 404"

**Symptoms**:
```bash
curl http://localhost:5001/api/pricing/contracts
# Returns: 404 Not Found
```

**Fix**:
Check the Flask routes are registered:

```bash
venv/bin/python test_app.py
```

Look for `/api/pricing/contracts` in the route list.

If missing, there's a Flask-RESTX configuration issue (already fixed in latest code).

---

### Issue 3: "Port 5000 in use"

**Symptoms**:
```
Address already in use
Port 5000 is in use by another program
```

**Fix**:
Use port 5001 (already set in run.sh):

```bash
./run.sh  # Uses port 5001 automatically
```

Or use custom port:
```bash
FLASK_PORT=8000 venv/bin/python flask_app.py
```

---

### Issue 4: "Module not found" errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'flask_restx'
```

**Fix**:
Install dependencies:

```bash
venv/bin/pip install -r requirements.txt
```

---

### Issue 5: "OpenAI API key not found"

**Symptoms**:
Chatbot page shows error about API key.

**Fix**:
This is OPTIONAL. The chatbot won't work without it, but all other features will:

1. Create `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

2. Or run without chatbot (calculator and PnL still work fine)

---

## 🔬 Deep Debugging

### Check Specific API Endpoint

```bash
# Test pricing calculation
curl -X POST http://localhost:5001/api/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "futures_price": 100,
    "strike_price": 105,
    "days_to_expiry": 30,
    "volatility": 0.20,
    "risk_free_rate": 0.12,
    "option_type": "call"
  }'
```

**Expected**: JSON with call_price, put_price, etc.

### Check JavaScript Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors in red

Common errors and fixes:

| Error | Fix |
|-------|-----|
| `Calculator is not defined` | Check calculator.js loaded |
| `API.pricing.calculate is not a function` | Check api.js loaded |
| `Failed to fetch` | Flask app not running |
| `Unexpected token < in JSON` | API returning HTML (404 error) |

### Check Network Requests

1. Open DevTools → Network tab
2. Reload page
3. Filter by "XHR" or "Fetch"
4. Look for red requests (failed)
5. Click on them to see error details

---

## 📊 Verify Data Flow

### Frontend → Backend Flow

1. **User adjusts slider** →
2. **JavaScript event** (`calculator.js:66`) →
3. **Debounced API call** (`calculator.js:110`) →
4. **Flask route** (`/api/pricing/calculate`) →
5. **Service layer** (`pricing_service.py`) →
6. **Black76Pricer** (core logic) →
7. **JSON response** →
8. **JavaScript updates DOM**

If heatmaps don't show, one of these steps failed.

**Test each step:**

```javascript
// In browser console
console.log(Calculator);  // Should show object
console.log(API);         // Should show object
API.pricing.getContracts().then(console.log);  // Should show contracts
```

---

## ✅ Health Check Checklist

Run these commands to verify everything:

```bash
# 1. Flask app working?
curl http://localhost:5001/ | grep "Option Calculator"

# 2. API working?
curl http://localhost:5001/api/pricing/contracts | grep "SCOM"

# 3. Swagger docs working?
curl http://localhost:5001/api/doc | grep "Swagger"

# 4. Market status working?
curl http://localhost:5001/api/market/status

# 5. PnL strategies working?
curl http://localhost:5001/api/pnl/strategies
```

All should return data without errors.

---

## 🚨 Last Resort

If nothing works:

1. **Stop all Flask processes**:
   ```bash
   pkill -f flask_app.py
   ```

2. **Clear Python cache**:
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   ```

3. **Reinstall dependencies**:
   ```bash
   venv/bin/pip install --force-reinstall -r requirements.txt
   ```

4. **Test again**:
   ```bash
   venv/bin/python test_app.py
   ./run.sh
   ```

---

## 📞 Getting More Help

If you're still stuck, check these files for clues:

1. **Flask startup logs**: Look at terminal output
2. **Browser console**: F12 → Console tab
3. **Network tab**: F12 → Network → Look for failed requests
4. **Test script output**: `venv/bin/python test_app.py`

The error messages will point you to the exact problem!
