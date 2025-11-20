# 🚀 How to Run the NSE Options Pricing Tool

## Quick Start

### Option 1: Direct Launch
```bash
# Navigate to the project directory
cd /Users/emilio/projects/options_pricer

# Run the Streamlit application
streamlit run app.py
```

### Option 2: Using Python Module
```bash
# Navigate to the project directory
cd /Users/emilio/projects/options_pricer

# Run with Python module
python3 -m streamlit run app.py
```

### Option 3: Using the Launcher Script
```bash
# Navigate to the project directory
cd /Users/emilio/projects/options_pricer

# Run the launcher
python3 run_app.py
```

## 🌐 Accessing the Application

Once you run any of the above commands:

1. **Streamlit will start** and show output like:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Open your browser** and go to: `http://localhost:8501`

3. **The app will load** with the beautiful NSE-branded interface

## 🎯 What You'll See

### Home Page
- **Hero Section**: Beautiful gradient header with NSE branding
- **Feature Cards**: Overview of capabilities (6 contracts, 3 ML models, 8 Greeks)
- **Quick Start Buttons**: Direct access to main features
- **Market Overview**: Simulated NSE market data

### Option Pricing Page
- **Interactive Controls**: Select contracts, set parameters
- **Real-time Calculations**: Instant pricing as you change inputs
- **ML Volatility Option**: Toggle between manual and predicted volatility
- **Comprehensive Results**: Option price, intrinsic value, time value

### Greeks Analysis Page
- **Complete Greeks Suite**: Delta, Gamma, Vega, Theta, Rho, Lambda
- **Interactive Charts**: Visualize Greeks vs underlying price
- **Educational Explanations**: Built-in help for each Greek
- **Real-time Updates**: Greeks recalculate as inputs change

## 🎨 Visual Features

The application includes:
- **Modern Glass-morphism Design**
- **NSE Orange & Blue Branding**
- **Smooth Animations & Transitions**
- **Responsive Layout** (works on mobile too)
- **Professional Typography** (Inter font)
- **Interactive Hover Effects**

## 🔧 Troubleshooting

### If Streamlit is not installed:
```bash
pip install streamlit pandas numpy scipy plotly matplotlib
```

### If you see import errors:
```bash
# Install all dependencies
pip install -r requirements.txt
```

### If the app doesn't load:
1. Check that you're in the right directory
2. Ensure Python 3 is being used
3. Try a different port:
   ```bash
   streamlit run app.py --server.port 8502
   ```

## 📱 Usage Tips

1. **Start with Home Page**: Get familiar with the layout
2. **Try Option Pricing**: Use default values first, then experiment
3. **Explore Greeks**: See how risk metrics change with inputs
4. **Use Help Text**: Hover over (?) icons for explanations
5. **Try Different Contracts**: Each NSE contract has unique characteristics

## 🎓 Educational Features

- **Contextual Help**: Explanations throughout the interface
- **Real Examples**: Using actual NSE contract parameters
- **Interactive Learning**: Change inputs and see immediate results
- **Local Context**: KES currency, NSE trading hours, Kenyan holidays

## 🚀 Ready to Launch!

The NSE Options Pricing Tool is fully functional and ready to use. Simply run the command above and start exploring Kenya's derivatives market with professional-grade tools!

---

**🇰🇪 Happy Trading and Learning! 📈**