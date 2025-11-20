#!/usr/bin/env python3
"""
Launcher script for the NSE Options Pricing Tool
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'scipy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def run_app():
    """Run the Streamlit application"""
    print("🇰🇪 NSE Options Pricing Tool")
    print("=" * 50)
    
    if not check_requirements():
        return
    
    print("🚀 Starting Streamlit application...")
    print("📱 The app will open in your browser automatically")
    print("🌐 URL: http://localhost:8501")
    print("=" * 50)
    
    try:
        # Run streamlit
        result = subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    run_app()