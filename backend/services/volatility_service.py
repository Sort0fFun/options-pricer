"""
Volatility Forecasting Service

This service loads the v2_enhanced volatility forecasting model and provides
prediction methods for the Flask application.
"""

import os
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass, asdict

import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from .data_loader import DataLoader
from .feature_engine import FeatureEngine

logger = logging.getLogger(__name__)


@dataclass
class VolatilityPrediction:
    """Container for volatility prediction results."""
    predicted_volatility: float
    confidence_interval: Tuple[float, float]
    model_confidence: float
    contributing_models: Dict[str, float]
    prediction_timestamp: str
    horizon_days: int
    symbol: str
    model_version: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert tuple to list for JSON
        result['confidence_interval'] = list(result['confidence_interval'])
        return result


class VolatilityForecasterService:
    """
    Service for loading and using the volatility forecasting model.
    """

    # Class-level singleton instance
    _instance = None
    _initialized = False

    def __init__(self, model_path: str, data_dir: str, cache_dir: Optional[str] = None):
        """
        Initialize volatility forecaster service.

        Args:
            model_path: Path to the .joblib model file
            data_dir: Directory containing .zst trade data files
            cache_dir: Directory for caching processed data
        """
        self.model_path = model_path
        self.data_dir = data_dir
        self.cache_dir = cache_dir

        # Initialize components
        self.model_data = None
        self.scaler = None
        self.models = None
        self.feature_columns = None
        self.best_model_name = None
        self.calibrated_model = None
        self.config = None
        self.metrics = None

        self.data_loader = None
        self.feature_engine = FeatureEngine()

        # Load model
        self.load_model()

        # Initialize data loader
        self.data_loader = DataLoader(data_dir, cache_dir)

    def load_model(self):
        """Load the volatility forecasting model from disk."""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")

            logger.info(f"Loading model from {self.model_path}")
            self.model_data = joblib.load(self.model_path)

            # Extract model components
            self.scaler = self.model_data.get('scaler')
            self.models = self.model_data.get('models', {})
            self.feature_columns = self.model_data.get('feature_columns', [])
            self.best_model_name = self.model_data.get('best_model')
            self.calibrated_model = self.model_data.get('calibrated_model')
            self.config = self.model_data.get('config', {})
            self.metrics = self.model_data.get('metrics', {})

            logger.info(f"Model loaded successfully")
            logger.info(f"Best model: {self.best_model_name}")
            logger.info(f"Features: {len(self.feature_columns)}")
            logger.info(f"Test AUC: {self.metrics.get('test_auc', 'N/A')}")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def predict_volatility(
        self,
        symbol: str,
        futures_price: Optional[float] = None,
        horizon_days: int = 12,
        confidence_level: float = 0.95
    ) -> VolatilityPrediction:
        """
        Predict volatility for a given symbol.

        Args:
            symbol: Futures symbol (e.g., 'NQZ5')
            futures_price: Optional current futures price (not used in prediction but included in response)
            horizon_days: Forecast horizon in number of periods
            confidence_level: Confidence level for intervals (0.95 or 0.99)

        Returns:
            VolatilityPrediction object
        """
        try:
            logger.info(f"Predicting volatility for {symbol}, horizon={horizon_days}")

            # Load trade data
            trade_data = self.data_loader.load_symbol_data(symbol, use_cache=True)

            # Create OHLCV bars
            bars = self.data_loader.create_ohlcv_bars(
                trade_data,
                freq=self.config.get('bar_freq', '5min'),
                use_cache=True
            )

            # Generate features
            features_df = self.feature_engine.generate_all_features(bars)

            # Remove NaN rows
            features_df = features_df.dropna()

            if len(features_df) < 100:
                raise ValueError(f"Insufficient data for prediction. Got {len(features_df)} samples, need at least 100")

            # Extract features in the correct order
            X = features_df[self.feature_columns].values[-1:, :]  # Take most recent

            # Scale features
            X_scaled = self.scaler.transform(X)

            # Get predictions from available models
            predictions = {}

            # Use calibrated model if available
            if self.calibrated_model is not None:
                try:
                    y_prob = self.calibrated_model.predict_proba(X_scaled)[0, 1]
                    # Convert probability to volatility estimate
                    # Higher probability = expecting volatility to increase
                    base_vol = features_df['rvol_12'].iloc[-1]
                    predicted_vol = base_vol * (1 + (y_prob - 0.5))  # Adjust based on prediction
                    predictions['Calibrated Model'] = predicted_vol
                    logger.info(f"Calibrated model prediction: {predicted_vol:.4f} (prob={y_prob:.4f})")
                except Exception as e:
                    logger.warning(f"Calibrated model prediction failed: {e}")

            # Try individual models as fallback
            for model_name, model in self.models.items():
                if model_name == self.best_model_name or (len(predictions) == 0 and 'XGBoost' in model_name):
                    try:
                        y_prob = model.predict_proba(X_scaled)[0, 1]
                        base_vol = features_df['rvol_12'].iloc[-1]
                        predicted_vol = base_vol * (1 + (y_prob - 0.5))
                        predictions[model_name] = predicted_vol
                        logger.info(f"{model_name} prediction: {predicted_vol:.4f}")
                    except Exception as e:
                        logger.warning(f"{model_name} prediction failed: {e}")

            if not predictions:
                # Fallback to historical volatility
                predicted_vol = features_df['rvol_12'].iloc[-1]
                predictions['Historical'] = predicted_vol
                logger.warning("All models failed, using historical volatility as fallback")
            else:
                # Ensemble prediction (average of all models)
                predicted_vol = np.mean(list(predictions.values()))

            # Calculate confidence interval
            if len(predictions) > 1:
                prediction_std = np.std(list(predictions.values()))
            else:
                prediction_std = predicted_vol * 0.1  # 10% of predicted value

            z_score = 1.96 if confidence_level == 0.95 else 2.58
            confidence_interval = (
                max(0.01, predicted_vol - z_score * prediction_std),
                predicted_vol + z_score * prediction_std
            )

            # Model confidence based on prediction agreement
            model_confidence = 1.0 - (prediction_std / predicted_vol) if predicted_vol > 0 else 0.5
            model_confidence = max(0.1, min(1.0, model_confidence))

            return VolatilityPrediction(
                predicted_volatility=float(predicted_vol),
                confidence_interval=confidence_interval,
                model_confidence=float(model_confidence),
                contributing_models={k: float(v) for k, v in predictions.items()},
                prediction_timestamp=datetime.utcnow().isoformat() + 'Z',
                horizon_days=horizon_days,
                symbol=symbol,
                model_version=self.model_data.get('version', 'v2_enhanced')
            )

        except Exception as e:
            logger.error(f"Error predicting volatility: {e}")
            raise

    def get_forecast_series(
        self,
        symbol: str,
        horizon_days: int = 30,
        confidence_threshold: float = 0.6
    ) -> Dict:
        """
        Get volatility forecast time series.

        Args:
            symbol: Futures symbol
            horizon_days: Number of days to forecast
            confidence_threshold: Confidence threshold for filtering predictions

        Returns:
            Dictionary with forecast data and metrics
        """
        try:
            # Load and process data
            trade_data = self.data_loader.load_symbol_data(symbol, use_cache=True)
            bars = self.data_loader.create_ohlcv_bars(trade_data, use_cache=True)
            features_df = self.feature_engine.generate_all_features(bars)
            features_df = features_df.dropna()

            # Get recent historical volatility
            recent_data = features_df.tail(horizon_days * 12)  # 12 periods per hour

            historical_vol = recent_data['rvol_12'].values
            timestamps = recent_data.index.strftime('%Y-%m-%d %H:%M:%S').tolist()

            # Current prediction
            current_prediction = self.predict_volatility(symbol, horizon_days=horizon_days)

            return {
                'symbol': symbol,
                'current_prediction': current_prediction.to_dict(),
                'historical_volatility': {
                    'timestamps': timestamps,
                    'values': historical_vol.tolist()
                },
                'stats': {
                    'mean': float(np.mean(historical_vol)),
                    'std': float(np.std(historical_vol)),
                    'min': float(np.min(historical_vol)),
                    'max': float(np.max(historical_vol)),
                    'current': float(historical_vol[-1])
                }
            }

        except Exception as e:
            logger.error(f"Error generating forecast series: {e}")
            raise

    def run_backtest(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        confidence_threshold: float = 0.6
    ) -> Dict:
        """
        Run backtest on historical data.

        Args:
            symbol: Futures symbol
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            confidence_threshold: Confidence threshold for trading

        Returns:
            Dictionary with backtest results
        """
        try:
            logger.info(f"Running backtest for {symbol}")

            # Load data
            trade_data = self.data_loader.load_symbol_data(
                symbol,
                start_date=start_date,
                end_date=end_date,
                use_cache=True
            )

            bars = self.data_loader.create_ohlcv_bars(trade_data, use_cache=True)
            features_df = self.feature_engine.generate_all_features(bars)
            features_df = features_df.dropna()

            # Split into test set (last 30%)
            split_idx = int(len(features_df) * 0.7)
            test_df = features_df.iloc[split_idx:]

            # Get predictions for test set
            X_test = test_df[self.feature_columns].values
            X_test_scaled = self.scaler.transform(X_test)

            # Use calibrated model or best model
            model = self.calibrated_model if self.calibrated_model else self.models[self.best_model_name]
            y_prob = model.predict_proba(X_test_scaled)[:, 1]

            # Simulate trading based on predictions
            # (Simplified version - full backtest would need more complex logic)
            correct_predictions = np.sum((y_prob > 0.5) == (test_df['rvol_12'].values > test_df['rvol_12'].shift(12).values))
            total_predictions = len(y_prob)
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0

            return {
                'symbol': symbol,
                'test_period': {
                    'start': test_df.index[0].isoformat(),
                    'end': test_df.index[-1].isoformat(),
                    'n_samples': len(test_df)
                },
                'metrics': {
                    'accuracy': float(accuracy),
                    'total_predictions': int(total_predictions),
                    'test_auc': float(self.metrics.get('test_auc', 0))
                },
                'model_info': self.get_model_info()
            }

        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise

    def get_model_info(self) -> Dict:
        """
        Get model metadata and information.

        Returns:
            Dictionary with model information
        """
        return {
            'version': self.model_data.get('version', 'v2_enhanced'),
            'best_model': self.best_model_name,
            'n_features': len(self.feature_columns),
            'feature_names': self.feature_columns[:20],  # First 20 features
            'config': self.config,
            'metrics': self.metrics,
            'available_models': list(self.models.keys())
        }

    def predict_from_dataframe(
        self,
        df: pd.DataFrame,
        data_name: str = 'custom_data',
        horizon_days: int = 12,
        confidence_level: float = 0.95
    ) -> VolatilityPrediction:
        """
        Predict volatility from a custom OHLCV DataFrame.

        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
                indexed by timestamp
            data_name: Name for the dataset (used in response)
            horizon_days: Forecast horizon in number of periods
            confidence_level: Confidence level for intervals (0.95 or 0.99)

        Returns:
            VolatilityPrediction object
        """
        try:
            logger.info(f"Predicting volatility from custom DataFrame with {len(df)} rows")

            # Validate DataFrame structure
            required_cols = ['open', 'high', 'low', 'close']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            # Add volume column if missing
            if 'volume' not in df.columns:
                df = df.copy()
                df['volume'] = 0

            # Ensure proper types
            df = df.copy()
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Calculate log returns (required by feature engine)
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))
            df['return'] = df['close'].pct_change()

            # Generate features using feature engine
            features_df = self.feature_engine.generate_all_features(df)

            # Remove NaN rows
            features_df = features_df.dropna()

            if len(features_df) < 50:
                raise ValueError(f"Insufficient data after feature generation. Got {len(features_df)} samples, need at least 50")

            # Extract features in the correct order
            available_features = [f for f in self.feature_columns if f in features_df.columns]
            if len(available_features) < len(self.feature_columns) * 0.8:
                logger.warning(f"Only {len(available_features)}/{len(self.feature_columns)} features available")
            
            # Use only available features that are in the model
            X = features_df[available_features].values[-1:, :]  # Take most recent

            # If feature count doesn't match, pad with zeros or use median
            if X.shape[1] < len(self.feature_columns):
                # Create full feature array with zeros for missing features
                X_full = np.zeros((1, len(self.feature_columns)))
                for i, feat in enumerate(self.feature_columns):
                    if feat in available_features:
                        feat_idx = available_features.index(feat)
                        X_full[0, i] = X[0, feat_idx]
                X = X_full

            # Scale features
            X_scaled = self.scaler.transform(X)

            # Get predictions from available models
            predictions = {}

            # Use calibrated model if available
            if self.calibrated_model is not None:
                try:
                    y_prob = self.calibrated_model.predict_proba(X_scaled)[0, 1]
                    # Convert probability to volatility estimate
                    base_vol = features_df['rvol_12'].iloc[-1] if 'rvol_12' in features_df.columns else 0.02
                    predicted_vol = base_vol * (1 + (y_prob - 0.5))
                    predictions['Calibrated Model'] = predicted_vol
                    logger.info(f"Calibrated model prediction: {predicted_vol:.6f} (prob={y_prob:.4f})")
                except Exception as e:
                    logger.warning(f"Calibrated model prediction failed: {e}")

            # Try individual models as fallback
            for model_name, model in self.models.items():
                if model_name == self.best_model_name or (len(predictions) == 0):
                    try:
                        y_prob = model.predict_proba(X_scaled)[0, 1]
                        base_vol = features_df['rvol_12'].iloc[-1] if 'rvol_12' in features_df.columns else 0.02
                        predicted_vol = base_vol * (1 + (y_prob - 0.5))
                        predictions[model_name] = predicted_vol
                        logger.info(f"{model_name} prediction: {predicted_vol:.6f}")
                    except Exception as e:
                        logger.warning(f"{model_name} prediction failed: {e}")

            if not predictions:
                # Fallback to historical volatility
                if 'rvol_12' in features_df.columns:
                    predicted_vol = features_df['rvol_12'].iloc[-1]
                else:
                    # Calculate simple volatility from returns
                    returns = df['close'].pct_change().dropna()
                    predicted_vol = returns.std() * np.sqrt(252 * 12)  # Annualized
                predictions['Historical'] = predicted_vol
                logger.warning("All models failed, using historical volatility as fallback")
            else:
                # Ensemble prediction (average of all models)
                predicted_vol = np.mean(list(predictions.values()))

            # Calculate confidence interval
            if len(predictions) > 1:
                prediction_std = np.std(list(predictions.values()))
            else:
                prediction_std = predicted_vol * 0.1  # 10% of predicted value

            z_score = 1.96 if confidence_level == 0.95 else 2.58
            confidence_interval = (
                max(0.001, predicted_vol - z_score * prediction_std),
                predicted_vol + z_score * prediction_std
            )

            # Model confidence based on prediction agreement
            model_confidence = 1.0 - (prediction_std / predicted_vol) if predicted_vol > 0 else 0.5
            model_confidence = max(0.1, min(1.0, model_confidence))

            return VolatilityPrediction(
                predicted_volatility=float(predicted_vol),
                confidence_interval=confidence_interval,
                model_confidence=float(model_confidence),
                contributing_models={k: float(v) for k, v in predictions.items()},
                prediction_timestamp=datetime.utcnow().isoformat() + 'Z',
                horizon_days=horizon_days,
                symbol=data_name,
                model_version=self.model_data.get('version', 'v2_enhanced')
            )

        except Exception as e:
            logger.error(f"Error predicting from DataFrame: {e}")
            raise

    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols with data.

        Returns:
            List of symbol strings
        """
        return self.data_loader.get_available_symbols()

    @classmethod
    def init_app(cls, app):
        """
        Initialize service with Flask app configuration.

        Args:
            app: Flask application instance
        """
        if cls._initialized:
            logger.info("VolatilityForecasterService already initialized")
            return cls._instance

        model_path = app.config.get('VOLATILITY_MODEL_PATH')
        data_dir = app.config.get('VOLATILITY_DATA_DIR')
        cache_dir = app.config.get('VOLATILITY_CACHE_DIR')

        if not model_path or not data_dir:
            logger.warning("Volatility forecaster configuration missing, service not initialized")
            return None

        try:
            cls._instance = cls(model_path, data_dir, cache_dir)
            cls._initialized = True
            logger.info("VolatilityForecasterService initialized successfully")
            return cls._instance
        except Exception as e:
            logger.error(f"Failed to initialize VolatilityForecasterService: {e}")
            return None

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the service.

        Returns:
            VolatilityForecasterService instance or None if not initialized
        """
        if not cls._initialized:
            logger.warning("VolatilityForecasterService not initialized. Call init_app() first.")
            return None
        return cls._instance
