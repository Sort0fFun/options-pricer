"""
NSE Derivatives API Endpoints

Provides REST API endpoints for NSE symbol data, price information,
and volatility/price forecasting.
"""

import logging
from flask import Blueprint, request, jsonify

from backend.services.nse_data_service import NSEDataService
from backend.services.nse_forecaster import NSEVolatilityForecaster

logger = logging.getLogger(__name__)

nse_bp = Blueprint('nse', __name__)


def get_data_service() -> NSEDataService:
    """Get NSE data service instance."""
    return NSEDataService.get_instance()


def get_forecaster() -> NSEVolatilityForecaster:
    """Get NSE forecaster instance."""
    return NSEVolatilityForecaster.get_instance()


# ============================================================================
# Symbol Endpoints
# ============================================================================

@nse_bp.route('/symbols', methods=['GET'])
def get_symbols():
    """
    Get list of available NSE symbols for dropdown.
    
    GET /api/nse/symbols
    
    Response:
    [
        {"value": "SCOM", "label": "SCOM - Safaricom PLC", "type": "STOCK", "sector": "Telecommunications"},
        ...
    ]
    """
    try:
        service = get_data_service()
        symbols = service.get_dropdown_options()
        return jsonify(symbols)
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/symbols/stocks', methods=['GET'])
def get_stock_symbols():
    """
    Get only stock futures symbols.
    
    GET /api/nse/symbols/stocks
    """
    try:
        from backend.models.nse_symbols import get_stocks_only
        return jsonify(get_stocks_only())
    except Exception as e:
        logger.error(f"Error getting stock symbols: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/symbols/indices', methods=['GET'])
def get_index_symbols():
    """
    Get only index futures symbols.
    
    GET /api/nse/symbols/indices
    """
    try:
        from backend.models.nse_symbols import get_indices_only
        return jsonify(get_indices_only())
    except Exception as e:
        logger.error(f"Error getting index symbols: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/symbols/available', methods=['GET'])
def get_available_symbols():
    """
    Get symbols that have sufficient data for forecasting.
    
    GET /api/nse/symbols/available
    """
    try:
        forecaster = get_forecaster()
        symbols = forecaster.get_available_symbols()
        return jsonify(symbols)
    except Exception as e:
        logger.error(f"Error getting available symbols: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Price Data Endpoints
# ============================================================================

@nse_bp.route('/price/<string:symbol>', methods=['GET'])
def get_symbol_price(symbol):
    """
    Get latest price data for a symbol.
    
    GET /api/nse/price/SCOM
    
    Response:
    {
        "symbol": "SCOM",
        "name": "Safaricom PLC",
        "mtm_price": 25.50,
        "previous_price": 25.30,
        "daily_return": 0.0079,
        "expiry_date": "2025-03-31",
        "days_to_expiry": 77,
        "open_interest": 150
    }
    """
    try:
        service = get_data_service()
        data = service.get_latest_prices(symbol.upper())
        
        if data is None:
            return jsonify({'error': f'Symbol {symbol} not found'}), 404
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/expiries/<string:symbol>', methods=['GET'])
def get_symbol_expiries(symbol):
    """
    Get all available expiry contracts for a symbol.
    
    GET /api/nse/expiries/SCOM
    """
    try:
        service = get_data_service()
        expiries = service.get_all_expiries(symbol.upper())
        
        if not expiries:
            return jsonify({'error': f'No expiries found for {symbol}'}), 404
        
        return jsonify(expiries)
    except Exception as e:
        logger.error(f"Error getting expiries for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/historical/<string:symbol>', methods=['GET'])
def get_historical_data(symbol):
    """
    Get historical data for a symbol.
    
    GET /api/nse/historical/SCOM
    """
    try:
        service = get_data_service()
        df = service.get_symbol_data(symbol.upper())
        
        if df.empty:
            return jsonify({'error': f'Symbol {symbol} not found'}), 404
        
        # Convert dates to string for JSON
        for col in ['Expiry Date', 'Listing Date']:
            if col in df.columns:
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        return jsonify(df.to_dict('records'))
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Volatility Endpoints
# ============================================================================

@nse_bp.route('/volatility/<string:symbol>', methods=['GET'])
def get_historical_volatility(symbol):
    """
    Get historical volatility metrics for a symbol.
    
    GET /api/nse/volatility/SCOM
    GET /api/nse/volatility/SCOM?window=10
    """
    try:
        window = request.args.get('window', type=int)
        
        forecaster = get_forecaster()
        result = forecaster.calculate_historical_volatility(symbol.upper(), window=window)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error calculating volatility for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Forecast Endpoints
# ============================================================================

@nse_bp.route('/forecast/volatility', methods=['POST'])
def forecast_volatility():
    """
    Generate volatility forecast using GARCH model.
    
    POST /api/nse/forecast/volatility
    Request Body:
    {
        "symbol": "SCOM",
        "horizon": 5,
        "model_type": "GARCH"  // GARCH, EGARCH, or TARCH
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        symbol = data.get('symbol', '').upper()
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        horizon = data.get('horizon', 5)
        model_type = data.get('model_type', data.get('garch_type', 'GARCH'))
        
        # Validate horizon
        if not isinstance(horizon, int) or horizon < 1 or horizon > 30:
            return jsonify({'error': 'Horizon must be between 1 and 30'}), 400
        
        forecaster = get_forecaster()
        result = forecaster.forecast_volatility_garch(
            symbol=symbol,
            horizon=horizon,
            model_type=model_type
        )
        
        if 'error' in result and 'forecasted_volatility_daily' not in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error forecasting volatility: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/forecast/price', methods=['POST'])
def forecast_price():
    """
    Generate price forecast using ARIMA model.
    
    POST /api/nse/forecast/price
    Request Body:
    {
        "symbol": "SCOM",
        "horizon": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        symbol = data.get('symbol', '').upper()
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        horizon = data.get('horizon', 5)
        
        # Validate horizon
        if not isinstance(horizon, int) or horizon < 1 or horizon > 30:
            return jsonify({'error': 'Horizon must be between 1 and 30'}), 400
        
        forecaster = get_forecaster()
        result = forecaster.forecast_price_arima(
            symbol=symbol,
            horizon=horizon
        )
        
        if 'error' in result and 'forecasted_prices' not in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error forecasting price: {e}")
        return jsonify({'error': str(e)}), 500


@nse_bp.route('/forecast/combined', methods=['POST'])
def forecast_combined():
    """
    Generate combined volatility and price forecast.
    
    POST /api/nse/forecast/combined
    Request Body:
    {
        "symbol": "SCOM",
        "horizon": 5,
        "garch_type": "GARCH"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        symbol = data.get('symbol', '').upper()
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        horizon = data.get('horizon', 5)
        garch_type = data.get('garch_type', 'GARCH')
        
        # Validate horizon
        if not isinstance(horizon, int) or horizon < 1 or horizon > 30:
            return jsonify({'error': 'Horizon must be between 1 and 30'}), 400
        
        forecaster = get_forecaster()
        result = forecaster.combined_forecast(
            symbol=symbol,
            horizon=horizon,
            garch_type=garch_type
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error generating combined forecast: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Data Management Endpoints
# ============================================================================

@nse_bp.route('/reload', methods=['POST'])
def reload_data():
    """
    Reload NSE data from CSV file.
    
    POST /api/nse/reload
    """
    try:
        service = get_data_service()
        df = service.load_data(force_reload=True)
        
        return jsonify({
            'success': True,
            'message': f'Reloaded {len(df)} records',
            'symbols_available': len(df['Symbol'].dropna().unique()) if not df.empty else 0
        })
    except Exception as e:
        logger.error(f"Error reloading data: {e}")
        return jsonify({'error': str(e)}), 500
