#!/bin/bash

# NSE Options Pricing Tool - Launch Script
echo "🇰🇪 NSE Options Pricing Tool"
echo "=================================="
echo ""

# Check Python 3
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 is available"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null && python --version | grep -q "Python 3"; then
    echo "✅ Python 3 is available"
    PYTHON_CMD="python"
else
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the project directory:"
    echo "   cd /Users/emilio/projects/options_pricer"
    echo "   ./LAUNCH_APP.sh"
    exit 1
fi

echo "✅ Project directory confirmed"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install streamlit pandas numpy scipy plotly matplotlib --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may already be installed"
fi

# Launch the application
echo ""
echo "🚀 Starting NSE Options Pricing Tool..."
echo "📱 The application will open in your browser"
echo "🌐 URL: http://localhost:8501"
echo ""
echo "=================================="
echo "🎯 LAUNCH SUCCESSFUL!"
echo "🌟 Enjoy exploring Kenya's derivatives market!"
echo "=================================="
echo ""

# Start Streamlit
$PYTHON_CMD -m streamlit run app.py

echo ""
echo "👋 Application stopped. Thank you for using the NSE Options Pricing Tool!"