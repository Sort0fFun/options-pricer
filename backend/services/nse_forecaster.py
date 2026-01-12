"""
NSE Volatility Forecaster Service

Provides volatility and price forecasting using GARCH and ARIMA models
specifically designed for NSE (Nairobi Securities Exchange) derivatives data.
"""

import logging
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from arch import arch_model
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

from .nse_data_service import NSEDataService

from backend.models.nse_symbols import NSE_SYMBOLS

logger = logging.getLogger(__name__)


@dataclass
class VolatilityForecastResult:
    """Container for volatility forecast results."""
    symbol: str
    name: str
    model_type: str
    historical_volatility_daily: float
    historical_volatility_annual: float
    forecasted_volatility_daily: List[float]
    forecasted_volatility_annual: List[float]
    forecast_horizon: int
    model_params: Dict
    aic: float
    bic: float
    log_likelihood: float
    observations: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PriceForecastResult:
    """Container for price forecast results."""
    symbol: str
    name: str
    current_price: float
    forecasted_prices: List[float]
    confidence_interval_lower: List[float]
    confidence_interval_upper: List[float]
    forecast_horizon: int
    arima_order: Tuple[int, int, int]
    aic: float
    bic: float
    observations: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['arima_order'] = list(result['arima_order'])
        return result


class NSEVolatilityForecaster:
    """
    Volatility and price forecaster for NSE derivatives.
    
    Uses GARCH family models for volatility forecasting and ARIMA for price forecasting.
    """
    
    _instance = None
    
    def __init__(self, data_service: NSEDataService = None):
        """
        Initialize the forecaster.
        
        Args:
            data_service: NSEDataService instance for data loading
        """
        self.data_service = data_service or NSEDataService.get_instance()
        self.garch_model = None
        self.arima_model = None
        self._last_symbol = None
        
    @classmethod
    def init_app(cls, app):
        """Initialize forecaster with Flask app."""
        data_service = NSEDataService.get_instance()
        cls._instance = cls(data_service)
        logger.info("NSE Volatility Forecaster initialized")
        
    @classmethod
    def get_instance(cls) -> 'NSEVolatilityForecaster':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def calculate_historical_volatility(
        self,
        symbol: str,
        window: int = None
    ) -> Dict:
        """
        Calculate historical volatility metrics for a symbol.
        
        Args:
            symbol: NSE symbol
            window: Rolling window for volatility calculation
            
        Returns:
            Dictionary with volatility metrics
        """
        try:
            returns = self.data_service.get_returns_for_volatility(symbol)
        except ValueError as e:
            return {'symbol': symbol, 'error': str(e)}
        
        # Annualization factor (252 trading days)
        annual_factor = np.sqrt(252)
        
        # Calculate volatility metrics
        daily_vol = np.std(returns)
        annual_vol = daily_vol * annual_factor
        
        # Rolling volatility if enough data
        rolling_vol = None
        if window and len(returns) >= window:
            rolling_vol = pd.Series(returns).rolling(window).std().dropna().values * annual_factor
        
        symbol_info = NSE_SYMBOLS.get(symbol.upper(), {})
        
        return {
            'symbol': symbol.upper(),
            'name': symbol_info.get('name', symbol),
            'daily_volatility': float(daily_vol),
            'annualized_volatility': float(annual_vol),
            'rolling_volatility': rolling_vol.tolist() if rolling_vol is not None else None,
            'observations': len(returns),
            'mean_return': float(np.mean(returns)),
            'max_return': float(np.max(returns)),
            'min_return': float(np.min(returns)),
            'skewness': float(pd.Series(returns).skew()),
            'kurtosis': float(pd.Series(returns).kurtosis())
        }
    
    def forecast_volatility_garch(
        self,
        symbol: str,
        horizon: int = 5,
        p: int = 1,
        q: int = 1,
        model_type: str = 'GARCH'
    ) -> Dict:
        """
        Forecast volatility using GARCH family models.
        
        Args:
            symbol: NSE symbol
            horizon: Forecast horizon (number of periods)
            p: GARCH lag order for variance
            q: GARCH lag order for squared residuals
            model_type: Model type - 'GARCH', 'EGARCH', or 'TARCH'
            
        Returns:
            Dictionary with forecast results
        """
        symbol = symbol.upper()
        symbol_info = NSE_SYMBOLS.get(symbol, {})
        
        try:
            returns = self.data_service.get_returns_for_volatility(symbol)
        except ValueError as e:
            return {
                'symbol': symbol,
                'name': symbol_info.get('name', symbol),
                'error': str(e)
            }
        
        # Validate model type
        vol_model = model_type.upper()
        if vol_model not in ['GARCH', 'EGARCH', 'TARCH']:
            vol_model = 'GARCH'
        
        try:
            # Build and fit model
            if vol_model == 'EGARCH':
                model = arch_model(returns, vol='EGARCH', p=p, q=q, rescale=False)
            elif vol_model == 'TARCH':
                model = arch_model(returns, vol='GARCH', p=p, o=1, q=q, rescale=False)
            else:
                model = arch_model(returns, vol='GARCH', p=p, q=q, rescale=False)
            
            self.garch_model = model.fit(disp='off', show_warning=False)
            self._last_symbol = symbol
            
            # Generate forecast
            forecast = self.garch_model.forecast(horizon=horizon)
            forecasted_variance = forecast.variance.values[-1, :]
            forecasted_volatility = np.sqrt(forecasted_variance)
            
            # Annualization
            annual_factor = np.sqrt(252)
            
            # Extract model parameters
            params = {}
            for param_name in self.garch_model.params.index:
                params[param_name] = float(self.garch_model.params[param_name])
            
            result = VolatilityForecastResult(
                symbol=symbol,
                name=symbol_info.get('name', symbol),
                model_type=vol_model,
                historical_volatility_daily=float(np.std(returns)),
                historical_volatility_annual=float(np.std(returns) * annual_factor),
                forecasted_volatility_daily=forecasted_volatility.tolist(),
                forecasted_volatility_annual=(forecasted_volatility * annual_factor).tolist(),
                forecast_horizon=horizon,
                model_params=params,
                aic=float(self.garch_model.aic),
                bic=float(self.garch_model.bic),
                log_likelihood=float(self.garch_model.loglikelihood),
                observations=len(returns),
                timestamp=datetime.utcnow().isoformat()
            )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"GARCH model error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol_info.get('name', symbol),
                'error': str(e),
                'historical_volatility_daily': float(np.std(returns)),
                'observations': len(returns)
            }
    
    def forecast_price_arima(
        self,
        symbol: str,
        horizon: int = 5,
        order: Tuple[int, int, int] = None
    ) -> Dict:
        """
        Forecast future prices using ARIMA model.
        
        Args:
            symbol: NSE symbol
            horizon: Forecast horizon (number of periods)
            order: ARIMA order (p, d, q). If None, auto-selected.
            
        Returns:
            Dictionary with price forecast results
        """
        symbol = symbol.upper()
        symbol_info = NSE_SYMBOLS.get(symbol, {})
        
        try:
            prices = self.data_service.get_prices_for_arima(symbol)
        except ValueError as e:
            return {
                'symbol': symbol,
                'name': symbol_info.get('name', symbol),
                'error': str(e)
            }
        
        # Auto-select order if not provided
        if order is None:
            try:
                # Test for stationarity
                adf_result = adfuller(prices)
                if adf_result[1] > 0.05:  # Non-stationary
                    order = (1, 1, 1)
                else:
                    order = (1, 0, 1)
            except:
                order = (1, 1, 1)
        
        try:
            # Fit ARIMA model - wrap in pandas Series for statsmodels
            prices_series = pd.Series(prices)
            model = ARIMA(prices_series, order=order)
            self.arima_model = model.fit()
            self._last_symbol = symbol
            
            # Generate forecast with confidence intervals
            forecast_result = self.arima_model.get_forecast(steps=horizon)
            forecasted_prices = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()
            
            result = PriceForecastResult(
                symbol=symbol,
                name=symbol_info.get('name', symbol),
                current_price=float(prices[-1]),
                forecasted_prices=forecasted_prices.values.tolist() if hasattr(forecasted_prices, 'values') else list(forecasted_prices),
                confidence_interval_lower=conf_int.iloc[:, 0].values.tolist() if hasattr(conf_int, 'iloc') else list(conf_int[:, 0]),
                confidence_interval_upper=conf_int.iloc[:, 1].values.tolist() if hasattr(conf_int, 'iloc') else list(conf_int[:, 1]),
                forecast_horizon=horizon,
                arima_order=order,
                aic=float(self.arima_model.aic),
                bic=float(self.arima_model.bic),
                observations=len(prices),
                timestamp=datetime.utcnow().isoformat()
            )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"ARIMA model error for {symbol}: {e}")
            return {
                'symbol': symbol,
                'name': symbol_info.get('name', symbol),
                'error': str(e),
                'current_price': float(prices[-1]) if len(prices) > 0 else None,
                'observations': len(prices)
            }
    
    def combined_forecast(
        self,
        symbol: str,
        horizon: int = 5,
        garch_type: str = 'GARCH'
    ) -> Dict:
        """
        Generate combined volatility and price forecast.
        
        Args:
            symbol: NSE symbol
            horizon: Forecast horizon
            garch_type: GARCH model variant
            
        Returns:
            Dictionary with both forecasts
        """
        symbol = symbol.upper()
        symbol_info = NSE_SYMBOLS.get(symbol, {})
        
        # Get forecasts
        vol_forecast = self.forecast_volatility_garch(symbol, horizon, model_type=garch_type)
        price_forecast = self.forecast_price_arima(symbol, horizon)
        
        # Get current price info
        current_data = self.data_service.get_latest_prices(symbol)
        
        return {
            'symbol': symbol,
            'name': symbol_info.get('name', symbol),
            'type': symbol_info.get('type', 'UNKNOWN'),
            'sector': symbol_info.get('sector', ''),
            'current_data': current_data,
            'volatility_forecast': vol_forecast,
            'price_forecast': price_forecast,
            'forecast_horizon': horizon,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_available_symbols(self) -> List[Dict]:
        """Get list of symbols with sufficient data for forecasting."""
        return self.data_service.get_symbols_with_data()
    
    def get_model_summary(self, model_type: str = 'garch') -> Optional[str]:
        """Get summary of last fitted model."""
        if model_type.lower() == 'garch' and self.garch_model:
            return str(self.garch_model.summary())
        elif model_type.lower() == 'arima' and self.arima_model:
            return str(self.arima_model.summary())
        return None
