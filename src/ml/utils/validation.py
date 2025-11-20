"""
Validation utilities for machine learning components.

This module provides comprehensive validation for data quality,
model inputs, and ML pipeline components.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_timeseries_data(
    data: pd.DataFrame,
    required_columns: List[str] = None,
    min_periods: int = 30
) -> None:
    """
    Validate time series data for ML models.
    
    Args:
        data: Input dataframe
        required_columns: List of required column names
        min_periods: Minimum number of data points required
        
    Raises:
        ValidationError: If validation fails
    """
    if required_columns is None:
        required_columns = ['price']
    
    # Check if dataframe is not empty
    if data is None or len(data) == 0:
        raise ValidationError("Data is empty")
    
    # Check required columns
    missing_columns = set(required_columns) - set(data.columns)
    if missing_columns:
        raise ValidationError(f"Missing required columns: {missing_columns}")
    
    # Check minimum periods
    if len(data) < min_periods:
        raise ValidationError(f"Insufficient data. Need at least {min_periods} periods, got {len(data)}")
    
    # Check for price column validity
    if 'price' in data.columns:
        price_series = data['price']
        
        # Check for missing values
        if price_series.isnull().sum() > 0:
            raise ValidationError("Price data contains missing values")
        
        # Check for non-positive prices
        if (price_series <= 0).any():
            raise ValidationError("Price data contains non-positive values")
        
        # Check for extreme price movements (>50% in one day)
        if len(price_series) > 1:
            returns = price_series.pct_change().dropna()
            extreme_moves = (returns.abs() > 0.5).sum()
            if extreme_moves > 0:
                logger.warning(f"Found {extreme_moves} extreme price movements (>50%)")
    
    # Check for volume column validity
    if 'volume' in data.columns:
        volume_series = data['volume']
        
        if volume_series.isnull().sum() > len(volume_series) * 0.1:
            logger.warning("Volume data has >10% missing values")
        
        if (volume_series < 0).any():
            raise ValidationError("Volume data contains negative values")
    
    # Check date column if present
    if 'date' in data.columns:
        try:
            date_series = pd.to_datetime(data['date'])
            if not date_series.is_monotonic_increasing:
                logger.warning("Date series is not monotonically increasing")
        except Exception as e:
            raise ValidationError(f"Invalid date format: {e}")


def validate_model_inputs(
    features: Union[np.ndarray, pd.DataFrame],
    targets: Union[np.ndarray, pd.Series] = None,
    feature_names: List[str] = None
) -> None:
    """
    Validate inputs for ML model training/prediction.
    
    Args:
        features: Feature array or dataframe
        targets: Target array or series (optional for prediction)
        feature_names: List of feature names
        
    Raises:
        ValidationError: If validation fails
    """
    # Convert to numpy if needed
    if isinstance(features, pd.DataFrame):
        features_array = features.values
    else:
        features_array = features
    
    if targets is not None:
        if isinstance(targets, pd.Series):
            targets_array = targets.values
        else:
            targets_array = targets
    
    # Check feature array
    if features_array is None or len(features_array) == 0:
        raise ValidationError("Features array is empty")
    
    if not isinstance(features_array, np.ndarray):
        raise ValidationError("Features must be numpy array or pandas DataFrame")
    
    if features_array.ndim != 2:
        raise ValidationError(f"Features must be 2D array, got {features_array.ndim}D")
    
    # Check for NaN/Inf values
    if np.isnan(features_array).any():
        raise ValidationError("Features contain NaN values")
    
    if np.isinf(features_array).any():
        raise ValidationError("Features contain infinite values")
    
    # Check targets if provided
    if targets is not None:
        if len(targets_array) != len(features_array):
            raise ValidationError(
                f"Length mismatch: features={len(features_array)}, targets={len(targets_array)}"
            )
        
        if np.isnan(targets_array).any():
            raise ValidationError("Targets contain NaN values")
        
        if np.isinf(targets_array).any():
            raise ValidationError("Targets contain infinite values")
        
        # Check for reasonable volatility range (0.1% to 500%)
        if targets_array.min() < 0.001 or targets_array.max() > 5.0:
            logger.warning(f"Targets outside normal volatility range: {targets_array.min():.3f} to {targets_array.max():.3f}")
    
    # Check feature names
    if feature_names is not None:
        if len(feature_names) != features_array.shape[1]:
            raise ValidationError(
                f"Feature names length ({len(feature_names)}) doesn't match features ({features_array.shape[1]})"
            )


def validate_prediction_inputs(
    current_data: pd.DataFrame,
    required_history: int = 60
) -> None:
    """
    Validate inputs for volatility prediction.
    
    Args:
        current_data: Recent market data
        required_history: Minimum required history
        
    Raises:
        ValidationError: If validation fails
    """
    validate_timeseries_data(current_data, min_periods=required_history)
    
    # Check data recency
    if 'date' in current_data.columns:
        latest_date = pd.to_datetime(current_data['date']).max()
        days_old = (datetime.now() - latest_date).days
        
        if days_old > 7:
            logger.warning(f"Data is {days_old} days old")
        
        if days_old > 30:
            raise ValidationError(f"Data too stale: {days_old} days old")


def validate_garch_data(returns: pd.Series) -> None:
    """
    Validate data specifically for GARCH modeling.
    
    Args:
        returns: Return series
        
    Raises:
        ValidationError: If validation fails
    """
    if returns is None or len(returns) == 0:
        raise ValidationError("Returns series is empty")
    
    if returns.isnull().sum() > 0:
        raise ValidationError("Returns contain missing values")
    
    # Check for stationarity (simplified test)
    if len(returns) > 50:
        # Check if mean is stable (rolling mean doesn't drift too much)
        rolling_mean = returns.rolling(20).mean()
        mean_stability = rolling_mean.std() / abs(rolling_mean.mean())
        
        if mean_stability > 2.0:
            logger.warning("Returns may not be stationary")
    
    # Check for minimum volatility clustering
    squared_returns = returns ** 2
    if len(squared_returns) > 10:
        # Simple test for volatility clustering
        autocorr_1 = squared_returns.autocorr(lag=1)
        if autocorr_1 < 0.1:
            logger.warning("Weak evidence of volatility clustering")


def validate_lstm_data(
    features: np.ndarray,
    sequence_length: int,
    feature_dim: int
) -> None:
    """
    Validate data for LSTM model.
    
    Args:
        features: Feature array
        sequence_length: Required sequence length
        feature_dim: Expected feature dimension
        
    Raises:
        ValidationError: If validation fails
    """
    if features.ndim != 3:
        raise ValidationError(f"LSTM features must be 3D array, got {features.ndim}D")
    
    expected_shape = (None, sequence_length, feature_dim)
    actual_shape = features.shape
    
    if actual_shape[1] != sequence_length:
        raise ValidationError(
            f"Sequence length mismatch: expected {sequence_length}, got {actual_shape[1]}"
        )
    
    if actual_shape[2] != feature_dim:
        raise ValidationError(
            f"Feature dimension mismatch: expected {feature_dim}, got {actual_shape[2]}"
        )
    
    # Check for reasonable data range (scaled features should be roughly [-3, 3])
    if features.max() > 10 or features.min() < -10:
        logger.warning("Features may need better scaling for LSTM")


def validate_ensemble_predictions(predictions: Dict[str, float]) -> None:
    """
    Validate individual model predictions for ensemble.
    
    Args:
        predictions: Dictionary of model predictions
        
    Raises:
        ValidationError: If validation fails
    """
    if not predictions:
        raise ValidationError("No valid predictions for ensemble")
    
    # Check for reasonable volatility values
    for model, pred in predictions.items():
        if pred is None or np.isnan(pred):
            logger.warning(f"Invalid prediction from {model}")
            continue
        
        if pred < 0.001:  # Less than 0.1% volatility
            logger.warning(f"Very low volatility prediction from {model}: {pred:.4f}")
        
        if pred > 2.0:  # More than 200% volatility
            logger.warning(f"Very high volatility prediction from {model}: {pred:.4f}")
    
    # Check for reasonable agreement between models
    valid_preds = [p for p in predictions.values() if not np.isnan(p)]
    
    if len(valid_preds) > 1:
        pred_std = np.std(valid_preds)
        pred_mean = np.mean(valid_preds)
        
        if pred_std / pred_mean > 0.5:  # Coefficient of variation > 50%
            logger.warning("Large disagreement between model predictions")


def check_data_quality(data: pd.DataFrame) -> Dict[str, any]:
    """
    Comprehensive data quality assessment.
    
    Args:
        data: Input dataframe
        
    Returns:
        Dictionary with quality metrics
    """
    quality_report = {
        'total_records': len(data),
        'columns': list(data.columns),
        'missing_values': {},
        'data_types': {},
        'value_ranges': {},
        'outliers': {},
        'quality_score': 0.0
    }
    
    # Missing values
    for col in data.columns:
        missing_pct = data[col].isnull().sum() / len(data) * 100
        quality_report['missing_values'][col] = missing_pct
    
    # Data types
    quality_report['data_types'] = dict(data.dtypes)
    
    # Value ranges for numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        quality_report['value_ranges'][col] = {
            'min': float(data[col].min()),
            'max': float(data[col].max()),
            'mean': float(data[col].mean()),
            'std': float(data[col].std())
        }
        
        # Outlier detection using IQR
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = ((data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))).sum()
        quality_report['outliers'][col] = outlier_count
    
    # Calculate overall quality score
    # Penalize for missing values, extreme outliers
    missing_penalty = sum(quality_report['missing_values'].values()) / len(data.columns)
    outlier_penalty = sum(quality_report['outliers'].values()) / len(data) * 100
    
    quality_score = max(0, 100 - missing_penalty - outlier_penalty)
    quality_report['quality_score'] = quality_score
    
    return quality_report


def validate_market_regime_data(
    returns: pd.Series,
    volume: pd.Series = None,
    min_regime_length: int = 20
) -> None:
    """
    Validate data for market regime detection.
    
    Args:
        returns: Return series
        volume: Volume series (optional)
        min_regime_length: Minimum length for stable regime detection
        
    Raises:
        ValidationError: If validation fails
    """
    validate_timeseries_data(
        pd.DataFrame({'price': np.exp(returns.cumsum())})  # Convert returns to prices for validation
    )
    
    if len(returns) < min_regime_length * 3:
        raise ValidationError(
            f"Insufficient data for regime detection. Need at least {min_regime_length * 3} periods"
        )
    
    # Check for sufficient volatility variation
    rolling_vol = returns.rolling(min_regime_length).std()
    vol_variation = rolling_vol.std() / rolling_vol.mean()
    
    if vol_variation < 0.2:
        logger.warning("Low volatility variation may make regime detection difficult")
    
    # Check volume data if provided
    if volume is not None:
        if len(volume) != len(returns):
            raise ValidationError("Volume and returns series must have same length")
        
        if volume.isnull().sum() > len(volume) * 0.2:
            logger.warning("Volume data has >20% missing values")


def validate_confidence_intervals(
    prediction: float,
    confidence_interval: Tuple[float, float],
    confidence_level: float = 0.95
) -> None:
    """
    Validate prediction confidence intervals.
    
    Args:
        prediction: Point prediction
        confidence_interval: Tuple of (lower, upper) bounds
        confidence_level: Confidence level (0-1)
        
    Raises:
        ValidationError: If validation fails
    """
    lower, upper = confidence_interval
    
    # Basic sanity checks
    if lower >= upper:
        raise ValidationError("Lower bound must be less than upper bound")
    
    if prediction < lower or prediction > upper:
        raise ValidationError("Prediction must be within confidence interval")
    
    # Check for reasonable interval width
    interval_width = upper - lower
    relative_width = interval_width / prediction
    
    if relative_width > 2.0:  # Interval wider than 200% of prediction
        logger.warning(f"Very wide confidence interval: {relative_width:.1%} of prediction")
    
    if relative_width < 0.1:  # Interval narrower than 10% of prediction
        logger.warning(f"Very narrow confidence interval: {relative_width:.1%} of prediction")
    
    # Check bounds are positive for volatility
    if lower <= 0:
        logger.warning("Confidence interval includes non-positive values")


# Utility functions for common validation patterns
def is_valid_returns_series(returns: pd.Series) -> bool:
    """Check if returns series is valid for modeling."""
    try:
        validate_timeseries_data(pd.DataFrame({'price': np.exp(returns.cumsum())}))
        validate_garch_data(returns)
        return True
    except ValidationError:
        return False


def is_sufficient_data_for_ml(data: pd.DataFrame, min_periods: int = 252) -> bool:
    """Check if there's sufficient data for ML modeling."""
    try:
        validate_timeseries_data(data, min_periods=min_periods)
        return True
    except ValidationError:
        return False


def clean_invalid_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean common data issues.
    
    Args:
        data: Input dataframe
        
    Returns:
        Cleaned dataframe
    """
    cleaned = data.copy()
    
    # Remove rows with all NaN
    cleaned = cleaned.dropna(how='all')
    
    # Forward fill missing values for price data
    if 'price' in cleaned.columns:
        cleaned['price'] = cleaned['price'].fillna(method='ffill')
    
    # Replace infinite values with NaN
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
    
    # Remove outliers in returns (>5 standard deviations)
    if 'returns' in cleaned.columns:
        returns_std = cleaned['returns'].std()
        returns_mean = cleaned['returns'].mean()
        outlier_mask = np.abs(cleaned['returns'] - returns_mean) > 5 * returns_std
        cleaned.loc[outlier_mask, 'returns'] = np.nan
        cleaned['returns'] = cleaned['returns'].fillna(method='ffill')
    
    logger.info(f"Data cleaning: {len(data)} -> {len(cleaned)} records")
    
    return cleaned