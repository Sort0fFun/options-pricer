"""
Market Regime Detection Module

This module implements market regime detection using Hidden Markov Models (HMM)
and other statistical methods to identify different market states.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

@dataclass
class MarketRegime:
    """Container for market regime information."""
    regime: str
    probability: float
    start_date: datetime
    characteristics: Dict[str, float]
    recommended_strategies: List[str]

class RegimeDetector:
    """Detects market regimes using HMM and statistical analysis."""
    
    def __init__(self, n_regimes: int = 3):
        """Initialize the regime detector.
        
        Args:
            n_regimes: Number of market regimes to detect (default: 3)
        """
        self.n_regimes = n_regimes
        self.model = hmm.GaussianHMM(
            n_components=n_regimes,
            covariance_type="full",
            n_iter=100
        )
        self.scaler = StandardScaler()
        self.regime_labels = [
            "Low Volatility",
            "Normal Trading",
            "High Volatility"
        ]
        
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for regime detection.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Array of processed features
        """
        # Calculate technical features
        returns = data['close'].pct_change().fillna(0)
        volatility = returns.rolling(window=20).std().fillna(0)
        volume_ma = data['volume'].rolling(window=20).mean().fillna(0)
        
        features = np.column_stack([
            returns,
            volatility,
            data['volume'] / volume_ma - 1
        ])
        
        return self.scaler.fit_transform(features)
    
    def detect_regime(self, data: pd.DataFrame) -> MarketRegime:
        """Detect current market regime.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            MarketRegime object with regime information
        """
        # Prepare features
        features = self._prepare_features(data)
        
        # Fit model and predict regime
        self.model.fit(features)
        regime_probs = self.model.predict_proba(features)
        current_regime = regime_probs[-1]
        
        # Get regime characteristics
        regime_idx = current_regime.argmax()
        characteristics = {
            'volatility': data['close'].pct_change().std() * np.sqrt(252),
            'trend': (data['close'].iloc[-1] / data['close'].iloc[0] - 1),
            'volume_ratio': (data['volume'].iloc[-5:].mean() / 
                           data['volume'].iloc[-20:-5].mean())
        }
        
        # Recommend strategies based on regime
        strategies = self._get_recommended_strategies(regime_idx, characteristics)
        
        return MarketRegime(
            regime=self.regime_labels[regime_idx],
            probability=current_regime[regime_idx],
            start_date=data.index[-1],
            characteristics=characteristics,
            recommended_strategies=strategies
        )
    
    def _get_recommended_strategies(
        self,
        regime_idx: int,
        characteristics: Dict[str, float]
    ) -> List[str]:
        """Get recommended options strategies for the current regime."""
        
        if regime_idx == 0:  # Low Volatility
            return [
                "Iron Condor",
                "Covered Call",
                "Short Straddle",
                "Calendar Spread"
            ]
        elif regime_idx == 1:  # Normal Trading
            return [
                "Vertical Spreads",
                "Butterfly Spread",
                "Collar",
                "Diagonal Spread"
            ]
        else:  # High Volatility
            return [
                "Long Straddle",
                "Long Strangle",
                "Back Spread",
                "Protective Put"
            ]