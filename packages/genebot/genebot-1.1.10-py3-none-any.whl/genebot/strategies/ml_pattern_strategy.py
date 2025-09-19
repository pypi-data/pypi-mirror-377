"""
Machine Learning Pattern Recognition Strategy for high-probability trading signals.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn not available, ML features disabled")

from .base_strategy import BaseStrategy, StrategyConfig
from .technical_indicators import TechnicalIndicators
from ..models.data_models import MarketData, TradingSignal, SignalAction


class MLPatternStrategy(BaseStrategy):
    """
    Machine Learning Pattern Recognition Strategy.
    
    This strategy uses machine learning to identify complex patterns in market data:
    - Feature engineering from multiple timeframes
    - Pattern recognition using ensemble methods
    - Candlestick pattern analysis
    - Market microstructure analysis
    - Adaptive learning from recent performance
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the ML Pattern Strategy.
        
        Args:
            config: Strategy configuration containing parameters:
                - lookback_period: Historical data lookback (default: 100)
                - feature_window: Feature calculation window (default: 20)
                - prediction_threshold: ML prediction confidence threshold (default: 0.75)
                - retrain_frequency: Model retraining frequency in signals (default: 50)
                - min_confidence: Minimum signal confidence (default: 0.90)
                - use_ensemble: Use ensemble of models (default: True)
        """
        super().__init__(config)
        
        if not ML_AVAILABLE:
            raise ImportError("scikit-learn is required for MLPatternStrategy")
        
        # Extract parameters
        self.lookback_period = self.parameters.get('lookback_period', 100)
        self.feature_window = self.parameters.get('feature_window', 20)
        self.prediction_threshold = self.parameters.get('prediction_threshold', 0.75)
        self.retrain_frequency = self.parameters.get('retrain_frequency', 50)
        self.min_confidence = self.parameters.get('min_confidence', 0.90)
        self.use_ensemble = self.parameters.get('use_ensemble', True)
        
        # Technical indicators
        self.indicators = TechnicalIndicators()
        
        # ML Models
        self.models = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Strategy state
        self._historical_data = []
        self._feature_history = []
        self._prediction_history = []
        self._performance_history = []
        self._signals_since_retrain = 0
        
        self.logger = logging.getLogger(f"strategy.ml_pattern.{self.name}")
    
    def initialize(self) -> bool:
        """Initialize the strategy."""
        try:
            self.logger.info(f"Initializing ML Pattern Strategy: {self.name}")
            
            if not ML_AVAILABLE:
                self.logger.error("scikit-learn not available")
                return False
            
            # Initialize models
            if self.use_ensemble:
                self.models = {
                    'rf': RandomForestClassifier(
                        n_estimators=100,
                        max_depth=10,
                        min_samples_split=5,
                        random_state=42
                    ),
                    'gb': GradientBoostingClassifier(
                        n_estimators=100,
                        max_depth=6,
                        learning_rate=0.1,
                        random_state=42
                    )
                }
            else:
                self.models = {
                    'rf': RandomForestClassifier(
                        n_estimators=150,
                        max_depth=12,
                        min_samples_split=3,
                        random_state=42
                    )
                }
            
            # Clear state
            self._historical_data.clear()
            self._feature_history.clear()
            self._prediction_history.clear()
            self._performance_history.clear()
            self._signals_since_retrain = 0
            self.is_trained = False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize strategy: {str(e)}")
            return False
    
    def analyze(self, market_data: List[MarketData]) -> Optional[TradingSignal]:
        """
        Analyze market data using ML pattern recognition.
        
        Args:
            market_data: List of market data points
            
        Returns:
            Optional[TradingSignal]: High-confidence ML-based signal
        """
        if len(market_data) < self.get_required_data_length():
            return None
        
        try:
            # Update historical data
            self._update_historical_data(market_data)
            
            # Extract features
            features = self._extract_features(market_data)
            if features is None:
                return None
            
            # Train model if not trained or retrain if needed
            if not self.is_trained:
                if len(self._historical_data) >= self.lookback_period:
                    self._train_models()
                else:
                    return None  # Not enough data to train
            elif self._signals_since_retrain >= self.retrain_frequency:
                self._retrain_models()
            
            # Make prediction
            prediction = self._make_prediction(features)
            if prediction is None:
                return None
            
            action, confidence = prediction
            
            # Generate signal if confidence is high enough
            if confidence >= self.min_confidence:
                current_data = market_data[-1]
                signal = self._create_ml_signal(current_data, action, confidence, features)
                
                if signal:
                    self._signals_since_retrain += 1
                    self.logger.info(f"ML Signal: {action.value} (confidence: {confidence:.3f})")
                
                return signal
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in ML analysis: {str(e)}")
            return None
    
    def get_required_data_length(self) -> int:
        """Get minimum data points required."""
        return max(self.lookback_period, 50)
    
    def validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        try:
            if not ML_AVAILABLE:
                self.logger.error("scikit-learn not available")
                return False
            
            if self.lookback_period < 50:
                self.logger.error("lookback_period must be at least 50")
                return False
            
            if not (0.5 <= self.prediction_threshold <= 1.0):
                self.logger.error("prediction_threshold must be between 0.5 and 1.0")
                return False
            
            if not (0.0 <= self.min_confidence <= 1.0):
                self.logger.error("min_confidence must be between 0.0 and 1.0")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return False
    
    def _update_historical_data(self, market_data: List[MarketData]):
        """Update historical data buffer."""
        # Keep only recent data
        self._historical_data = market_data[-self.lookback_period * 2:]
    
    def _extract_features(self, market_data: List[MarketData]) -> Optional[np.ndarray]:
        """Extract comprehensive features for ML model."""
        try:
            if len(market_data) < self.feature_window:
                return None
            
            # Extract OHLCV data
            opens = [float(d.open) for d in market_data[-self.feature_window:]]
            highs = [float(d.high) for d in market_data[-self.feature_window:]]
            lows = [float(d.low) for d in market_data[-self.feature_window:]]
            closes = [float(d.close) for d in market_data[-self.feature_window:]]
            volumes = [float(d.volume) for d in market_data[-self.feature_window:]]
            
            features = []
            
            # 1. Price-based features
            current_price = closes[-1]
            
            # Price ratios
            features.extend([
                current_price / closes[-2] if len(closes) > 1 else 1.0,  # Price change ratio
                current_price / closes[-5] if len(closes) > 4 else 1.0,  # 5-period ratio
                current_price / closes[-10] if len(closes) > 9 else 1.0,  # 10-period ratio
            ])
            
            # 2. Technical indicators
            sma_5 = self.indicators.sma(closes, 5)
            sma_10 = self.indicators.sma(closes, 10)
            ema_5 = self.indicators.ema(closes, 5)
            rsi = self.indicators.rsi(closes, 14)
            
            if sma_5 and sma_10 and ema_5:
                features.extend([
                    current_price / sma_5[-1],  # Price vs SMA5
                    current_price / sma_10[-1],  # Price vs SMA10
                    current_price / ema_5[-1],  # Price vs EMA5
                    sma_5[-1] / sma_10[-1],  # SMA5 vs SMA10
                ])
            else:
                features.extend([1.0, 1.0, 1.0, 1.0])
            
            if rsi is not None:
                features.append(rsi / 100.0)  # Normalized RSI
            else:
                features.append(0.5)
            
            # 3. Bollinger Bands
            bb_result = self.indicators.bollinger_bands(closes, 20, 2.0)
            if bb_result:
                upper, middle, lower = bb_result
                bb_position = (current_price - lower) / (upper - lower)
                bb_width = (upper - lower) / middle
                features.extend([bb_position, bb_width])
            else:
                features.extend([0.5, 0.1])
            
            # 4. MACD
            macd_result = self.indicators.macd(closes)
            if macd_result:
                macd_line, signal_line, histogram = macd_result
                features.extend([
                    macd_line / current_price,  # Normalized MACD
                    histogram / current_price,  # Normalized histogram
                ])
            else:
                features.extend([0.0, 0.0])
            
            # 5. Candlestick patterns
            candlestick_features = self._extract_candlestick_features(opens, highs, lows, closes)
            features.extend(candlestick_features)
            
            # 6. Volume features
            if len(volumes) >= 10:
                avg_volume = sum(volumes[-10:]) / 10
                volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1.0
                features.append(min(volume_ratio, 5.0))  # Cap at 5x
            else:
                features.append(1.0)
            
            # 7. Volatility features
            if len(closes) >= 10:
                returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
                volatility = np.std(returns[-10:]) if len(returns) >= 10 else 0.0
                features.append(volatility * 100)  # Percentage volatility
            else:
                features.append(1.0)
            
            # 8. Market microstructure
            microstructure_features = self._extract_microstructure_features(opens, highs, lows, closes)
            features.extend(microstructure_features)
            
            # 9. Momentum features
            momentum_features = self._extract_momentum_features(closes)
            features.extend(momentum_features)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            return None
    
    def _extract_candlestick_features(self, opens: List[float], highs: List[float], 
                                    lows: List[float], closes: List[float]) -> List[float]:
        """Extract candlestick pattern features."""
        features = []
        
        try:
            if len(closes) < 3:
                return [0.0] * 8
            
            # Current candle
            o, h, l, c = opens[-1], highs[-1], lows[-1], closes[-1]
            
            # Body and shadow ratios
            body_size = abs(c - o) / (h - l) if h != l else 0.0
            upper_shadow = (h - max(o, c)) / (h - l) if h != l else 0.0
            lower_shadow = (min(o, c) - l) / (h - l) if h != l else 0.0
            
            features.extend([body_size, upper_shadow, lower_shadow])
            
            # Doji pattern (small body)
            is_doji = 1.0 if body_size < 0.1 else 0.0
            features.append(is_doji)
            
            # Hammer/Hanging man (long lower shadow, small body)
            is_hammer = 1.0 if lower_shadow > 0.6 and body_size < 0.3 else 0.0
            features.append(is_hammer)
            
            # Shooting star (long upper shadow, small body)
            is_shooting_star = 1.0 if upper_shadow > 0.6 and body_size < 0.3 else 0.0
            features.append(is_shooting_star)
            
            # Engulfing patterns (need previous candle)
            if len(closes) >= 2:
                prev_o, prev_c = opens[-2], closes[-2]
                
                # Bullish engulfing
                bullish_engulfing = (1.0 if (prev_c < prev_o and c > o and 
                                           c > prev_o and o < prev_c) else 0.0)
                
                # Bearish engulfing
                bearish_engulfing = (1.0 if (prev_c > prev_o and c < o and 
                                           c < prev_o and o > prev_c) else 0.0)
                
                features.extend([bullish_engulfing, bearish_engulfing])
            else:
                features.extend([0.0, 0.0])
            
        except Exception as e:
            self.logger.error(f"Error in candlestick features: {str(e)}")
            features = [0.0] * 8
        
        return features
    
    def _extract_microstructure_features(self, opens: List[float], highs: List[float], 
                                       lows: List[float], closes: List[float]) -> List[float]:
        """Extract market microstructure features."""
        features = []
        
        try:
            if len(closes) < 5:
                return [0.0] * 6
            
            # Gap analysis
            gap = (opens[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0.0
            features.append(gap * 100)  # Percentage gap
            
            # Intraday range
            intraday_range = (highs[-1] - lows[-1]) / opens[-1] if opens[-1] > 0 else 0.0
            features.append(intraday_range * 100)
            
            # Close position within range
            close_position = ((closes[-1] - lows[-1]) / (highs[-1] - lows[-1]) 
                            if highs[-1] != lows[-1] else 0.5)
            features.append(close_position)
            
            # Average true range (ATR) approximation
            tr_values = []
            for i in range(1, min(len(closes), 5)):
                tr = max(
                    highs[-i] - lows[-i],
                    abs(highs[-i] - closes[-i-1]),
                    abs(lows[-i] - closes[-i-1])
                )
                tr_values.append(tr / closes[-i])
            
            atr = sum(tr_values) / len(tr_values) if tr_values else 0.0
            features.append(atr * 100)
            
            # Price acceleration (second derivative)
            if len(closes) >= 3:
                accel = (closes[-1] - 2*closes[-2] + closes[-3]) / closes[-3]
                features.append(accel * 100)
            else:
                features.append(0.0)
            
            # Trend consistency
            if len(closes) >= 5:
                trend_up = sum(1 for i in range(1, 5) if closes[-i] > closes[-i-1])
                trend_consistency = trend_up / 4.0
                features.append(trend_consistency)
            else:
                features.append(0.5)
            
        except Exception as e:
            self.logger.error(f"Error in microstructure features: {str(e)}")
            features = [0.0] * 6
        
        return features
    
    def _extract_momentum_features(self, closes: List[float]) -> List[float]:
        """Extract momentum-based features."""
        features = []
        
        try:
            if len(closes) < 10:
                return [0.0] * 5
            
            # Rate of change over different periods
            roc_3 = (closes[-1] - closes[-4]) / closes[-4] if len(closes) > 3 else 0.0
            roc_5 = (closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0.0
            roc_10 = (closes[-1] - closes[-11]) / closes[-11] if len(closes) > 10 else 0.0
            
            features.extend([roc_3 * 100, roc_5 * 100, roc_10 * 100])
            
            # Momentum oscillator
            if len(closes) >= 10:
                momentum = closes[-1] - closes[-10]
                momentum_normalized = momentum / closes[-10]
                features.append(momentum_normalized * 100)
            else:
                features.append(0.0)
            
            # Price velocity (first derivative)
            if len(closes) >= 2:
                velocity = (closes[-1] - closes[-2]) / closes[-2]
                features.append(velocity * 100)
            else:
                features.append(0.0)
            
        except Exception as e:
            self.logger.error(f"Error in momentum features: {str(e)}")
            features = [0.0] * 5
        
        return features
    
    def _train_models(self):
        """Train ML models on historical data."""
        try:
            if len(self._historical_data) < self.lookback_period:
                return
            
            self.logger.info("Training ML models...")
            
            # Prepare training data
            X, y = self._prepare_training_data()
            
            if len(X) < 50:  # Need minimum samples
                self.logger.warning("Insufficient training data")
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            for name, model in self.models.items():
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                self.logger.info(f"Model {name} accuracy: {accuracy:.3f}")
            
            self.is_trained = True
            self._signals_since_retrain = 0
            
        except Exception as e:
            self.logger.error(f"Error training models: {str(e)}")
    
    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data with features and labels."""
        X, y = [], []
        
        try:
            # Create sliding windows
            for i in range(self.feature_window, len(self._historical_data) - 5):
                window_data = self._historical_data[i-self.feature_window:i]
                
                # Extract features
                features = self._extract_features(window_data)
                if features is None:
                    continue
                
                # Create label (future price movement)
                current_price = float(self._historical_data[i].close)
                future_price = float(self._historical_data[i+5].close)  # 5 periods ahead
                
                price_change = (future_price - current_price) / current_price
                
                # Label: 0=sell, 1=hold, 2=buy
                if price_change > 0.02:  # 2% gain
                    label = 2  # Buy
                elif price_change < -0.02:  # 2% loss
                    label = 0  # Sell
                else:
                    label = 1  # Hold
                
                X.append(features.flatten())
                y.append(label)
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            self.logger.error(f"Error preparing training data: {str(e)}")
            return np.array([]), np.array([])
    
    def _retrain_models(self):
        """Retrain models with recent data."""
        try:
            self.logger.info("Retraining ML models with recent data...")
            self._train_models()
            
        except Exception as e:
            self.logger.error(f"Error retraining models: {str(e)}")
    
    def _make_prediction(self, features: np.ndarray) -> Optional[Tuple[SignalAction, float]]:
        """Make prediction using ensemble of models."""
        try:
            if not self.is_trained:
                return None
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions from all models
            predictions = []
            probabilities = []
            
            for name, model in self.models.items():
                pred = model.predict(features_scaled)[0]
                pred_proba = model.predict_proba(features_scaled)[0]
                
                predictions.append(pred)
                probabilities.append(pred_proba)
            
            # Ensemble prediction (majority vote with confidence weighting)
            if self.use_ensemble and len(predictions) > 1:
                # Average probabilities
                avg_proba = np.mean(probabilities, axis=0)
                final_pred = np.argmax(avg_proba)
                confidence = np.max(avg_proba)
            else:
                final_pred = predictions[0]
                confidence = np.max(probabilities[0])
            
            # Convert to action
            if final_pred == 2 and confidence >= self.prediction_threshold:
                return SignalAction.BUY, confidence
            elif final_pred == 0 and confidence >= self.prediction_threshold:
                return SignalAction.SELL, confidence
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def _create_ml_signal(self, market_data: MarketData, action: SignalAction, 
                         confidence: float, features: np.ndarray) -> Optional[TradingSignal]:
        """Create ML-based trading signal."""
        try:
            return TradingSignal(
                symbol=market_data.symbol,
                action=action,
                confidence=confidence,
                timestamp=market_data.timestamp,
                strategy_name=self.name,
                price=market_data.close,
                metadata={
                    'ml_confidence': confidence,
                    'feature_count': features.shape[1],
                    'model_trained': self.is_trained,
                    'signals_since_retrain': self._signals_since_retrain,
                    'strategy_type': 'ml_pattern_recognition',
                    'ensemble_used': self.use_ensemble,
                    'models': list(self.models.keys())
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating ML signal: {str(e)}")
            return None