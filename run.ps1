# PowerShell startup script for NSE Options Pricer Flask app

Write-Host "========================================"
Write-Host "NSE Options Pricer - Flask Edition"
Write-Host "========================================"

# Check if venv exists
if (!(Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create one with: python -m venv venv"
    exit 1
}

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
    Write-Host "Loaded environment variables from .env" -ForegroundColor Green
}

# Set Flask environment variables
$env:FLASK_ENV = "development"
$env:FLASK_PORT = "5001"

Write-Host ""
Write-Host "Starting Flask app on port 5001..."
Write-Host "Once started, visit: http://localhost:5001"
Write-Host ""
Write-Host "Press CTRL+C to stop the server"
Write-Host "----------------------------------------"
Write-Host ""

# Use venv Python
& "venv\Scripts\python.exe" flask_app.py
