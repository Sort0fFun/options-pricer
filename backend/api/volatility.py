"""
Volatility Forecasting API Endpoints

Provides REST API endpoints for volatility prediction, forecasting, and backtesting.
"""

import io
import logging
from flask import Blueprint, request, jsonify, Response
from backend.services.volatility_service import VolatilityForecasterService
import pandas as pd

logger = logging.getLogger(__name__)

volatility_bp = Blueprint('volatility', __name__)

# Upload validation constants
UPLOAD_CONFIG = {
    'max_file_size_mb': 10,
    'min_rows': 100,
    'max_rows': 100000,
    'required_columns': ['timestamp', 'open', 'high', 'low', 'close'],
    'optional_columns': ['volume'],
    'allowed_extensions': ['.csv', '.json']
}


@volatility_bp.route('/predict', methods=['POST'])
def predict_volatility():
    """
    Predict volatility for a given symbol.

    POST /api/volatility/predict
    Request Body:
    {
        "symbol": "NQZ5",
        "futures_price": 100.0,  // optional
        "horizon_days": 12        // optional, default=12
    }

    Response:
    {
        "success": true,
        "data": {
            "predicted_volatility": 0.3245,
            "confidence_interval": [0.2950, 0.3540],
            "model_confidence": 0.87,
            "contributing_models": {...},
            "prediction_timestamp": "2026-01-12T11:30:00Z",
            ...
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        symbol = data.get('symbol')
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400

        futures_price = data.get('futures_price')
        horizon_days = data.get('horizon_days', 12)

        # Validate inputs
        if not isinstance(horizon_days, int) or horizon_days < 1 or horizon_days > 365:
            return jsonify({
                'success': False,
                'error': 'horizon_days must be between 1 and 365'
            }), 400

        # Get prediction
        prediction = service.predict_volatility(
            symbol=symbol,
            futures_price=futures_price,
            horizon_days=horizon_days
        )

        return jsonify({
            'success': True,
            'data': prediction.to_dict()
        })

    except FileNotFoundError as e:
        logger.error(f"Data not found: {e}")
        return jsonify({
            'success': False,
            'error': f'No data available for symbol {data.get("symbol")}'
        }), 404

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error in predict_volatility: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error during prediction'
        }), 500


@volatility_bp.route('/forecast/<symbol>', methods=['GET'])
def get_forecast(symbol):
    """
    Get volatility forecast time series for a symbol.

    GET /api/volatility/forecast/NQZ5?horizon=30&confidence_threshold=0.6

    Response:
    {
        "success": true,
        "data": {
            "symbol": "NQZ5",
            "current_prediction": {...},
            "historical_volatility": {
                "timestamps": [...],
                "values": [...]
            },
            "stats": {...}
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Parse query parameters
        horizon_days = request.args.get('horizon', default=30, type=int)
        confidence_threshold = request.args.get('confidence_threshold', default=0.6, type=float)

        # Validate inputs
        if horizon_days < 1 or horizon_days > 90:
            return jsonify({
                'success': False,
                'error': 'horizon must be between 1 and 90 days'
            }), 400

        if confidence_threshold < 0 or confidence_threshold > 1:
            return jsonify({
                'success': False,
                'error': 'confidence_threshold must be between 0 and 1'
            }), 400

        # Get forecast
        forecast_data = service.get_forecast_series(
            symbol=symbol,
            horizon_days=horizon_days,
            confidence_threshold=confidence_threshold
        )

        return jsonify({
            'success': True,
            'data': forecast_data
        })

    except FileNotFoundError as e:
        logger.error(f"Data not found: {e}")
        return jsonify({
            'success': False,
            'error': f'No data available for symbol {symbol}'
        }), 404

    except Exception as e:
        logger.error(f"Error in get_forecast: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error during forecast generation'
        }), 500


@volatility_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """
    Run backtest on historical data.

    POST /api/volatility/backtest
    Request Body:
    {
        "symbol": "NQZ5",
        "start_date": "2025-10-01",  // optional
        "end_date": "2025-12-31",    // optional
        "confidence_threshold": 0.6  // optional
    }

    Response:
    {
        "success": true,
        "data": {
            "symbol": "NQZ5",
            "test_period": {...},
            "metrics": {
                "accuracy": 0.7038,
                "total_predictions": 4826,
                ...
            },
            "model_info": {...}
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        symbol = data.get('symbol')
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Symbol is required'
            }), 400

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        confidence_threshold = data.get('confidence_threshold', 0.6)

        # Run backtest
        backtest_results = service.run_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            confidence_threshold=confidence_threshold
        )

        return jsonify({
            'success': True,
            'data': backtest_results
        })

    except FileNotFoundError as e:
        logger.error(f"Data not found: {e}")
        return jsonify({
            'success': False,
            'error': f'No data available for symbol {data.get("symbol")}'
        }), 404

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error in run_backtest: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error during backtest'
        }), 500


@volatility_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """
    Get model metadata and information.

    GET /api/volatility/model-info

    Response:
    {
        "success": true,
        "data": {
            "version": "v2_enhanced",
            "best_model": "LightGBM",
            "n_features": 75,
            "config": {...},
            "metrics": {...}
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Get model info
        model_info = service.get_model_info()

        return jsonify({
            'success': True,
            'data': model_info
        })

    except Exception as e:
        logger.error(f"Error in get_model_info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@volatility_bp.route('/symbols', methods=['GET'])
def get_available_symbols():
    """
    Get list of available symbols with data.

    GET /api/volatility/symbols

    Response:
    {
        "success": true,
        "data": {
            "symbols": ["NQZ5", "ESZ5", "SCOM", ...]
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Get available symbols
        symbols = service.get_available_symbols()

        return jsonify({
            'success': True,
            'data': {
                'symbols': symbols,
                'count': len(symbols)
            }
        })

    except Exception as e:
        logger.error(f"Error in get_available_symbols: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# Health check endpoint
@volatility_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check if volatility forecasting service is healthy.

    GET /api/volatility/health

    Response:
    {
        "success": true,
        "status": "healthy",
        "service_available": true
    }
    """
    service = VolatilityForecasterService.get_instance()

    return jsonify({
        'success': True,
        'status': 'healthy' if service else 'degraded',
        'service_available': service is not None
    })


@volatility_bp.route('/upload', methods=['POST'])
def upload_and_predict():
    """
    Upload custom OHLCV data and get volatility prediction.

    POST /api/volatility/upload
    Content-Type: multipart/form-data

    Form fields:
    - file: CSV or JSON file with OHLCV data
    - horizon_days: Optional forecast horizon (default: 12)
    - data_name: Optional name for the dataset

    Required columns: timestamp, open, high, low, close
    Optional columns: volume

    Response:
    {
        "success": true,
        "data": {
            "predicted_volatility": 0.3245,
            "confidence_interval": [0.2950, 0.3540],
            "model_confidence": 0.87,
            "data_info": {
                "rows": 5000,
                "date_range": {...}
            }
        }
    }
    """
    try:
        # Get service instance
        service = VolatilityForecasterService.get_instance()
        if service is None:
            return jsonify({
                'success': False,
                'error': 'Volatility forecasting service not available'
            }), 503

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded. Use form field "file"'
            }), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        # Get optional parameters
        horizon_days = request.form.get('horizon_days', default=12, type=int)
        data_name = request.form.get('data_name', default='uploaded_data')

        # Validate file extension
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in UPLOAD_CONFIG['allowed_extensions']):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {UPLOAD_CONFIG["allowed_extensions"]}'
            }), 400

        # Read file content
        file_content = file.read()
        
        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > UPLOAD_CONFIG['max_file_size_mb']:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {UPLOAD_CONFIG["max_file_size_mb"]}MB'
            }), 400

        # Parse file to DataFrame
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith('.json'):
                df = pd.read_json(io.BytesIO(file_content))
            else:
                return jsonify({
                    'success': False,
                    'error': 'Unsupported file format'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to parse file: {str(e)}'
            }), 400

        # Normalize column names (lowercase)
        df.columns = df.columns.str.lower().str.strip()

        # Check required columns
        missing_cols = [col for col in UPLOAD_CONFIG['required_columns'] if col not in df.columns]
        if missing_cols:
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {missing_cols}',
                'required': UPLOAD_CONFIG['required_columns'],
                'found': list(df.columns)
            }), 400

        # Validate row count
        if len(df) < UPLOAD_CONFIG['min_rows']:
            return jsonify({
                'success': False,
                'error': f'Insufficient data. Minimum {UPLOAD_CONFIG["min_rows"]} rows required, got {len(df)}'
            }), 400

        if len(df) > UPLOAD_CONFIG['max_rows']:
            return jsonify({
                'success': False,
                'error': f'Too much data. Maximum {UPLOAD_CONFIG["max_rows"]} rows allowed, got {len(df)}'
            }), 400

        # Parse timestamp
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to parse timestamp column: {str(e)}'
            }), 400

        # Validate numeric columns
        numeric_cols = ['open', 'high', 'low', 'close']
        if 'volume' in df.columns:
            numeric_cols.append('volume')
        
        for col in numeric_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Failed to parse column {col} as numeric: {str(e)}'
                }), 400

        # Check for NaN values
        nan_counts = df[numeric_cols].isna().sum()
        if nan_counts.any():
            return jsonify({
                'success': False,
                'error': f'Found NaN values in columns: {nan_counts[nan_counts > 0].to_dict()}'
            }), 400

        # Prepare OHLCV DataFrame in expected format
        ohlcv_df = df[['timestamp', 'open', 'high', 'low', 'close']].copy()
        ohlcv_df.columns = ['ts_event', 'open', 'high', 'low', 'close']
        if 'volume' in df.columns:
            ohlcv_df['volume'] = df['volume']
        else:
            ohlcv_df['volume'] = 0
        
        ohlcv_df = ohlcv_df.set_index('ts_event')

        # Get prediction using custom data
        prediction = service.predict_from_dataframe(
            df=ohlcv_df,
            data_name=data_name,
            horizon_days=horizon_days
        )

        # Build response with data info
        response_data = prediction.to_dict()
        response_data['data_info'] = {
            'name': data_name,
            'rows': len(df),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'columns': list(df.columns)
        }

        return jsonify({
            'success': True,
            'data': response_data
        })

    except ValueError as e:
        logger.error(f"Validation error in upload: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Error in upload_and_predict: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error during prediction'
        }), 500


@volatility_bp.route('/template', methods=['GET'])
def download_template():
    """
    Download a sample CSV template for data upload.

    GET /api/volatility/template

    Response: CSV file download
    """
    import random
    from datetime import datetime, timedelta

    # Generate 100 rows of realistic OHLCV data
    lines = ['timestamp,open,high,low,close,volume']
    base_price = 5245.25
    base_time = datetime(2025, 1, 2, 9, 30, 0)  # Start from a trading day

    for i in range(100):
        # Add 5 minutes per row
        timestamp = base_time + timedelta(minutes=i * 5)
        timestamp_str = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Generate realistic price movements
        change = random.uniform(-2.5, 2.5)
        open_price = base_price + change
        high_price = open_price + random.uniform(0.5, 3.0)
        low_price = open_price - random.uniform(0.5, 3.0)
        close_price = open_price + random.uniform(-2.0, 2.0)
        volume = random.randint(800, 2000)

        # Update base price for next iteration (random walk)
        base_price = close_price

        lines.append(f'{timestamp_str},{open_price:.2f},{high_price:.2f},{low_price:.2f},{close_price:.2f},{volume}')

    sample_data = '\n'.join(lines) + '\n'

    return Response(
        sample_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=volatility_data_template.csv'}
    )


@volatility_bp.route('/upload-requirements', methods=['GET'])
def get_upload_requirements():
    """
    Get upload requirements and validation rules.

    GET /api/volatility/upload-requirements

    Response:
    {
        "success": true,
        "data": {
            "max_file_size_mb": 10,
            "min_rows": 100,
            ...
        }
    }
    """
    return jsonify({
        'success': True,
        'data': {
            **UPLOAD_CONFIG,
            'supported_formats': ['CSV', 'JSON'],
            'example_timestamp_format': '2025-01-01T09:30:00Z',
            'notes': [
                'Timestamps should be in ISO 8601 format',
                'Data should be sorted by timestamp (ascending)',
                'Volume is optional but recommended for better predictions',
                'Minimum 100 data points required for feature calculation'
            ]
        }
    })
