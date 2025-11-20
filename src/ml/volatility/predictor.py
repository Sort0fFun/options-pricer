"""
Volatility Prediction Module using Machine Learning

This module implements GARCH and LSTM models for predicting volatility
of NSE futures contracts, with ensemble methods for improved accuracy.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Statistical models
from arch import arch_model
from sklearn.ensemble import VotingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Deep learning
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. LSTM models will be disabled.")

from ..data.features import FeatureEngine
from ..utils.validation import validate_timeseries_data

logger = logging.getLogger(__name__)


@dataclass
class VolatilityPrediction:
    """
    Container for volatility prediction results.
    
    Attributes:
        predicted_volatility: Main volatility prediction (annualized)
        confidence_interval: Tuple of (lower, upper) confidence bounds
        model_confidence: Confidence score (0-1)
        contributing_models: Dictionary of individual model predictions
        prediction_date: Date when prediction was made
        horizon_days: Forecast horizon in days
        symbol: Asset symbol
        methodology: Model type used ("GARCH", "LSTM", "Ensemble")
    """
    predicted_volatility: float
    confidence_interval: Tuple[float, float]
    model_confidence: float
    contributing_models: Dict[str, float]
    prediction_date: datetime
    horizon_days: int
    symbol: str
    methodology: str


@dataclass
class ModelPerformance:
    """
    Container for model performance metrics.
    
    Attributes:
        rmse: Root Mean Square Error
        mae: Mean Absolute Error
        mape: Mean Absolute Percentage Error
        r_squared: R-squared coefficient
        sharpe_ratio: Sharpe ratio using predicted volatility
        hit_rate: Percentage of directional predictions correct
        model_type: Type of model evaluated
    """
    rmse: float
    mae: float
    mape: float
    r_squared: float
    sharpe_ratio: float
    hit_rate: float
    model_type: str


class GARCHModel:
    """
    GARCH(1,1) model for volatility clustering prediction.
    
    GARCH models are specifically designed to handle volatility clustering,
    where periods of high volatility tend to be followed by high volatility.
    """
    
    def __init__(self, mean_model: str = 'constant', vol_model: str = 'GARCH'):
        """
        Initialize GARCH model.
        
        Args:
            mean_model: Mean model specification ('constant', 'AR', 'HAR')
            vol_model: Volatility model ('GARCH', 'EGARCH', 'GJR-GARCH')
        """
        self.mean_model = mean_model
        self.vol_model = vol_model
        self.model = None
        self.fitted_model = None
        self.is_fitted = False
        
    def fit(self, returns: pd.Series) -> None:
        """
        Fit GARCH model to return series.
        
        Args:
            returns: Time series of returns (should be stationary)
        """
        try:
            # Create GARCH model
            self.model = arch_model(
                returns * 100,  # Convert to percentage returns
                mean=self.mean_model,
                vol=self.vol_model,
                p=1, q=1  # GARCH(1,1)
            )
            
            # Fit model
            self.fitted_model = self.model.fit(disp='off', show_warning=False)
            self.is_fitted = True
            
            logger.info(f"GARCH model fitted successfully. AIC: {self.fitted_model.aic:.2f}")
            
        except Exception as e:
            logger.error(f"Error fitting GARCH model: {e}")
            raise
    
    def predict(self, horizon: int = 1) -> Tuple[float, float]:
        """
        Predict volatility for given horizon.
        
        Args:
            horizon: Forecast horizon in days
            
        Returns:
            Tuple of (predicted_volatility, forecast_variance)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            # Get forecast
            forecast = self.fitted_model.forecast(horizon=horizon)
            
            # Extract variance forecast and convert to volatility
            variance_forecast = forecast.variance.iloc[-1, 0] / 10000  # Convert back from percentage
            volatility_forecast = np.sqrt(variance_forecast * 252)  # Annualize
            
            return volatility_forecast, variance_forecast
            
        except Exception as e:
            logger.error(f"Error in GARCH prediction: {e}")
            raise
    
    def get_parameters(self) -> Dict[str, float]:
        """Get fitted model parameters."""
        if not self.is_fitted:
            return {}
        
        params = self.fitted_model.params
        return {
            'omega': params.get('omega', 0),
            'alpha[1]': params.get('alpha[1]', 0),
            'beta[1]': params.get('beta[1]', 0)
        }


class LSTMModel:
    """
    LSTM neural network for volatility prediction.
    
    LSTM networks can capture long-term dependencies and non-linear patterns
    in volatility that traditional statistical models might miss.
    """
    
    def __init__(
        self, 
        sequence_length: int = 60,
        features_dim: int = 5,
        lstm_units: List[int] = [50, 25],
        dropout_rate: float = 0.2
    ):
        """
        Initialize LSTM model.
        
        Args:
            sequence_length: Number of previous days to use for prediction
            features_dim: Number of input features
            lstm_units: List of LSTM layer sizes
            dropout_rate: Dropout rate for regularization
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models")
        
        self.sequence_length = sequence_length
        self.features_dim = features_dim
        self.lstm_units = lstm_units
        self.dropout_rate = dropout_rate
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        self.is_fitted = False
        
        # Build model architecture
        self._build_model()
    
    def _build_model(self) -> None:
        """Build LSTM model architecture."""
        self.model = Sequential()
        
        # First LSTM layer
        self.model.add(LSTM(
            self.lstm_units[0],
            return_sequences=True if len(self.lstm_units) > 1 else False,
            input_shape=(self.sequence_length, self.features_dim)
        ))
        self.model.add(Dropout(self.dropout_rate))
        
        # Additional LSTM layers
        for i, units in enumerate(self.lstm_units[1:]):
            return_seq = i < len(self.lstm_units) - 2
            self.model.add(LSTM(units, return_sequences=return_seq))
            self.model.add(Dropout(self.dropout_rate))
        
        # Dense layers
        self.model.add(Dense(10, activation='relu'))
        self.model.add(Dropout(self.dropout_rate / 2))
        self.model.add(Dense(1, activation='linear'))
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info(f"LSTM model built with {self.model.count_params()} parameters")
    
    def _prepare_sequences(self, features: np.ndarray, targets: np.ndarray = None) -> Tuple:
        """
        Prepare sequences for LSTM training/prediction.
        
        Args:
            features: Feature array
            targets: Target array (None for prediction)
            
        Returns:
            Tuple of prepared sequences
        """
        X_sequences = []
        y_sequences = [] if targets is not None else None
        
        for i in range(self.sequence_length, len(features)):
            X_sequences.append(features[i-self.sequence_length:i])
            if targets is not None:
                y_sequences.append(targets[i])
        
        X_sequences = np.array(X_sequences)
        
        if targets is not None:
            y_sequences = np.array(y_sequences)
            return X_sequences, y_sequences
        
        return X_sequences
    
    def fit(
        self, 
        features: np.ndarray, 
        targets: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: int = 0
    ) -> None:
        """
        Fit LSTM model to training data.
        
        Args:
            features: Input features array
            targets: Target volatility values
            validation_split: Fraction of data for validation
            epochs: Maximum training epochs
            batch_size: Training batch size
            verbose: Verbosity level
        """
        try:
            # Scale features and targets
            features_scaled = self.scaler_X.fit_transform(features)
            targets_scaled = self.scaler_y.fit_transform(targets.reshape(-1, 1)).flatten()
            
            # Prepare sequences
            X_seq, y_seq = self._prepare_sequences(features_scaled, targets_scaled)
            
            if len(X_seq) < 50:
                raise ValueError(f"Insufficient data for training. Need at least 50 sequences, got {len(X_seq)}")
            
            # Callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=15,
                    restore_best_weights=True
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=10,
                    min_lr=1e-6
                )
            ]
            
            # Train model
            history = self.model.fit(
                X_seq, y_seq,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=verbose
            )
            
            self.is_fitted = True
            self.training_history = history.history
            
            logger.info(f"LSTM model trained. Final loss: {history.history['loss'][-1]:.6f}")
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            raise
    
    def predict(self, features: np.ndarray) -> float:
        """
        Predict volatility using fitted LSTM model.
        
        Args:
            features: Input features for prediction
            
        Returns:
            Predicted volatility
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            # Scale features
            features_scaled = self.scaler_X.transform(features)
            
            # Prepare sequence
            if len(features_scaled) < self.sequence_length:
                raise ValueError(f"Need at least {self.sequence_length} data points for prediction")
            
            X_seq = features_scaled[-self.sequence_length:].reshape(1, self.sequence_length, self.features_dim)
            
            # Predict
            prediction_scaled = self.model.predict(X_seq, verbose=0)
            prediction = self.scaler_y.inverse_transform(prediction_scaled.reshape(-1, 1))[0, 0]
            
            return max(0.01, prediction)  # Ensure positive volatility
            
        except Exception as e:
            logger.error(f"Error in LSTM prediction: {e}")
            raise


class VolatilityPredictor:
    """
    Main volatility prediction engine combining GARCH and LSTM models.
    
    This class orchestrates the ensemble of models to provide robust
    volatility predictions for NSE futures contracts.
    """
    
    def __init__(self, use_lstm: bool = True):
        """
        Initialize volatility predictor.
        
        Args:
            use_lstm: Whether to use LSTM models (requires TensorFlow)
        """
        self.use_lstm = use_lstm and TENSORFLOW_AVAILABLE
        self.garch_model = GARCHModel()
        self.lstm_model = LSTMModel() if self.use_lstm else None
        self.feature_engine = FeatureEngine()
        self.is_fitted = False
        self.training_data = None
        self.model_weights = {'garch': 0.6, 'lstm': 0.4} if self.use_lstm else {'garch': 1.0}
        
        logger.info(f"VolatilityPredictor initialized. LSTM enabled: {self.use_lstm}")
    
    def fit(
        self, 
        price_data: pd.DataFrame,
        validation_split: float = 0.2,
        min_periods: int = 252
    ) -> None:
        """
        Fit all models to historical price data.
        
        Args:
            price_data: DataFrame with columns ['date', 'price', 'volume']
            validation_split: Fraction of data for validation
            min_periods: Minimum number of periods required
        """
        try:
            # Validate input data
            validate_timeseries_data(price_data)
            
            if len(price_data) < min_periods:
                raise ValueError(f"Insufficient data. Need at least {min_periods} periods.")
            
            # Calculate returns
            price_data = price_data.copy()
            price_data['returns'] = np.log(price_data['price'] / price_data['price'].shift(1))
            price_data = price_data.dropna()
            
            # Generate features
            features = self.feature_engine.generate_features(price_data)
            
            # Calculate realized volatility as target
            realized_vol = self._calculate_realized_volatility(price_data['returns'])
            
            # Split data
            split_idx = int(len(features) * (1 - validation_split))
            
            # Fit GARCH model
            logger.info("Fitting GARCH model...")
            garch_returns = price_data['returns'].iloc[:split_idx]
            self.garch_model.fit(garch_returns)
            
            # Fit LSTM model if enabled
            if self.use_lstm:
                logger.info("Fitting LSTM model...")
                lstm_features = features.iloc[:split_idx].values
                lstm_targets = realized_vol[:split_idx]
                
                self.lstm_model.fit(
                    features=lstm_features,
                    targets=lstm_targets,
                    validation_split=0.2,
                    epochs=100,
                    verbose=0
                )
            
            # Store training data
            self.training_data = {
                'features': features,
                'realized_vol': realized_vol,
                'returns': price_data['returns'],
                'split_idx': split_idx
            }
            
            # Evaluate models
            self._evaluate_models()
            
            self.is_fitted = True
            logger.info("All models fitted successfully")
            
        except Exception as e:
            logger.error(f"Error fitting volatility predictor: {e}")
            raise
    
    def _calculate_realized_volatility(
        self, 
        returns: pd.Series, 
        window: int = 30
    ) -> np.ndarray:
        """
        Calculate realized volatility using rolling window.
        
        Args:
            returns: Return series
            window: Rolling window size
            
        Returns:
            Array of realized volatilities
        """
        # Calculate rolling volatility (annualized)
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        return rolling_vol.values[window-1:]  # Remove NaN values
    
    def _evaluate_models(self) -> Dict[str, ModelPerformance]:
        """
        Evaluate model performance on validation data.
        
        Returns:
            Dictionary of model performances
        """
        if not self.training_data:
            raise ValueError("No training data available for evaluation")
        
        split_idx = self.training_data['split_idx']
        features = self.training_data['features']
        realized_vol = self.training_data['realized_vol']
        
        # Validation data
        val_features = features.iloc[split_idx:]
        val_targets = realized_vol[split_idx:]
        
        performances = {}
        
        # Evaluate GARCH
        garch_predictions = []
        for i in range(len(val_targets)):
            try:
                vol_pred, _ = self.garch_model.predict(horizon=1)
                garch_predictions.append(vol_pred)
            except:
                garch_predictions.append(np.nan)
        
        garch_predictions = np.array(garch_predictions)
        valid_mask = ~np.isnan(garch_predictions) & ~np.isnan(val_targets)
        
        if np.sum(valid_mask) > 0:
            performances['garch'] = self._calculate_performance_metrics(
                val_targets[valid_mask], 
                garch_predictions[valid_mask], 
                'GARCH'
            )
        
        # Evaluate LSTM if available
        if self.use_lstm and len(val_features) >= self.lstm_model.sequence_length:
            try:
                lstm_predictions = []
                for i in range(self.lstm_model.sequence_length, len(val_features)):
                    feat_window = val_features.iloc[i-self.lstm_model.sequence_length:i].values
                    pred = self.lstm_model.predict(feat_window)
                    lstm_predictions.append(pred)
                
                lstm_predictions = np.array(lstm_predictions)
                lstm_targets = val_targets[self.lstm_model.sequence_length:]
                
                valid_mask = ~np.isnan(lstm_predictions) & ~np.isnan(lstm_targets)
                
                if np.sum(valid_mask) > 0:
                    performances['lstm'] = self._calculate_performance_metrics(
                        lstm_targets[valid_mask],
                        lstm_predictions[valid_mask],
                        'LSTM'
                    )
            except Exception as e:
                logger.warning(f"LSTM evaluation failed: {e}")
        
        return performances
    
    def _calculate_performance_metrics(
        self, 
        actual: np.ndarray, 
        predicted: np.ndarray, 
        model_type: str
    ) -> ModelPerformance:
        """Calculate comprehensive performance metrics."""
        
        # Basic metrics
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mae = mean_absolute_error(actual, predicted)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        r2 = r2_score(actual, predicted)
        
        # Financial metrics
        # Simplified Sharpe ratio calculation
        returns = np.random.normal(0, predicted, len(predicted))  # Simulated returns
        sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        
        # Hit rate (directional accuracy)
        if len(actual) > 1:
            actual_direction = np.diff(actual) > 0
            predicted_direction = np.diff(predicted) > 0
            hit_rate = np.mean(actual_direction == predicted_direction) * 100
        else:
            hit_rate = 0
        
        return ModelPerformance(
            rmse=rmse,
            mae=mae,
            mape=mape,
            r_squared=r2,
            sharpe_ratio=sharpe,
            hit_rate=hit_rate,
            model_type=model_type
        )
    
    def predict_volatility(
        self,
        current_data: pd.DataFrame,
        horizon_days: int = 30,
        confidence_level: float = 0.95
    ) -> VolatilityPrediction:
        """
        Predict volatility using ensemble of models.
        
        Args:
            current_data: Recent market data
            horizon_days: Forecast horizon in days
            confidence_level: Confidence level for intervals
            
        Returns:
            VolatilityPrediction object
        """
        if not self.is_fitted:
            raise ValueError("Models must be fitted before prediction")
        
        try:
            # Generate features for current data
            features = self.feature_engine.generate_features(current_data)
            
            # Get individual model predictions
            predictions = {}
            
            # GARCH prediction
            try:
                garch_vol, _ = self.garch_model.predict(horizon=horizon_days)
                predictions['garch'] = garch_vol
            except Exception as e:
                logger.warning(f"GARCH prediction failed: {e}")
                predictions['garch'] = np.nan
            
            # LSTM prediction
            if self.use_lstm and len(features) >= self.lstm_model.sequence_length:
                try:
                    recent_features = features.tail(self.lstm_model.sequence_length).values
                    lstm_vol = self.lstm_model.predict(recent_features)
                    predictions['lstm'] = lstm_vol
                except Exception as e:
                    logger.warning(f"LSTM prediction failed: {e}")
                    predictions['lstm'] = np.nan
            
            # Ensemble prediction
            valid_predictions = {k: v for k, v in predictions.items() if not np.isnan(v)}
            
            if not valid_predictions:
                raise ValueError("All model predictions failed")
            
            # Weighted average
            ensemble_vol = sum(
                self.model_weights.get(model, 0) * pred 
                for model, pred in valid_predictions.items()
            ) / sum(self.model_weights.get(model, 0) for model in valid_predictions.keys())
            
            # Calculate confidence interval (simplified)
            prediction_std = np.std(list(valid_predictions.values())) if len(valid_predictions) > 1 else ensemble_vol * 0.1
            z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
            
            confidence_interval = (
                max(0.01, ensemble_vol - z_score * prediction_std),
                ensemble_vol + z_score * prediction_std
            )
            
            # Model confidence based on agreement
            model_confidence = 1.0 - (prediction_std / ensemble_vol) if ensemble_vol > 0 else 0.5
            model_confidence = max(0.1, min(1.0, model_confidence))
            
            return VolatilityPrediction(
                predicted_volatility=ensemble_vol,
                confidence_interval=confidence_interval,
                model_confidence=model_confidence,
                contributing_models=valid_predictions,
                prediction_date=datetime.now(),
                horizon_days=horizon_days,
                symbol=current_data.get('symbol', 'UNKNOWN'),
                methodology='Ensemble'
            )
            
        except Exception as e:
            logger.error(f"Error in volatility prediction: {e}")
            raise
    
    def update_model_weights(self, performance_metrics: Dict[str, ModelPerformance]) -> None:
        """
        Update ensemble weights based on model performance.
        
        Args:
            performance_metrics: Dictionary of model performance metrics
        """
        if not performance_metrics:
            return
        
        # Calculate weights based on inverse RMSE (better models get higher weight)
        total_inv_rmse = 0
        model_inv_rmse = {}
        
        for model, perf in performance_metrics.items():
            if perf.rmse > 0:
                inv_rmse = 1.0 / perf.rmse
                model_inv_rmse[model] = inv_rmse
                total_inv_rmse += inv_rmse
        
        # Update weights
        if total_inv_rmse > 0:
            for model in model_inv_rmse:
                self.model_weights[model] = model_inv_rmse[model] / total_inv_rmse
        
        logger.info(f"Updated model weights: {self.model_weights}")
    
    def get_model_summary(self) -> Dict:
        """Get summary of fitted models."""
        summary = {
            'is_fitted': self.is_fitted,
            'models_enabled': {
                'garch': True,
                'lstm': self.use_lstm
            },
            'model_weights': self.model_weights
        }
        
        if self.is_fitted:
            summary['garch_parameters'] = self.garch_model.get_parameters()
            
            if self.training_data:
                summary['training_periods'] = len(self.training_data['returns'])
                summary['validation_split'] = (
                    len(self.training_data['returns']) - self.training_data['split_idx']
                ) / len(self.training_data['returns'])
        
        return summary


# Convenience functions
def quick_volatility_prediction(
    price_data: pd.DataFrame,
    horizon_days: int = 30
) -> float:
    """
    Quick volatility prediction for simple use cases.
    
    Args:
        price_data: Historical price data
        horizon_days: Forecast horizon
        
    Returns:
        Predicted volatility
    """
    predictor = VolatilityPredictor(use_lstm=False)  # Use only GARCH for speed
    predictor.fit(price_data)
    prediction = predictor.predict_volatility(price_data.tail(100), horizon_days)
    return prediction.predicted_volatility