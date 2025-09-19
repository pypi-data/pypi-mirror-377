# Strategy Development Guide

## Overview

This guide provides comprehensive instructions for developing custom trading strategies for the Trading Bot Python system. Strategies are the core logic that determines when to buy, sell, or hold positions based on market data analysis.

## Strategy Architecture

### BaseStrategy Class

All strategies must inherit from the `BaseStrategy` abstract base class:

```python
from abc import ABC, abstractmethod
from src.strategies.base_strategy import BaseStrategy
from src.models.data_models import MarketData, TradingSignal
from typing import Dict, List, Any

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "my_custom_strategy"
        self.version = "1.0.0"
        
        # Initialize strategy parameters
        self.param1 = config.get('param1', default_value)
        self.param2 = config.get('param2', default_value)
    
    @abstractmethod
    def analyze(self, data: MarketData) -> TradingSignal:
        """Analyze market data and generate trading signal"""
        pass
    
    @abstractmethod
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Update strategy parameters dynamically"""
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """Return list of required technical indicators"""
        pass
```

### Required Methods

#### analyze(data: MarketData) -> TradingSignal

This is the core method where your strategy logic resides. It receives market data and returns a trading signal.

```python
def analyze(self, data: MarketData) -> TradingSignal:
    # Example: Simple moving average crossover
    short_ma = self.calculate_sma(data, period=10)
    long_ma = self.calculate_sma(data, period=20)
    
    if short_ma > long_ma:
        action = "BUY"
        confidence = 0.7
    elif short_ma < long_ma:
        action = "SELL"
        confidence = 0.7
    else:
        action = "HOLD"
        confidence = 0.5
    
    return TradingSignal(
        symbol=data.symbol,
        action=action,
        confidence=confidence,
        timestamp=data.timestamp,
        strategy_name=self.name,
        metadata={
            "short_ma": short_ma,
            "long_ma": long_ma,
            "price": data.close
        }
    )
```

#### update_parameters(params: Dict[str, Any]) -> None

Allows dynamic parameter updates without restarting the strategy.

```python
def update_parameters(self, params: Dict[str, Any]) -> None:
    if 'short_period' in params:
        self.short_period = params['short_period']
    if 'long_period' in params:
        self.long_period = params['long_period']
    
    # Validate parameters
    if self.short_period >= self.long_period:
        raise ValueError("Short period must be less than long period")
```

#### get_required_indicators() -> List[str]

Returns the technical indicators your strategy needs.

```python
def get_required_indicators(self) -> List[str]:
    return ["sma", "ema", "rsi", "macd"]
```

## Strategy Examples

### 1. Simple Moving Average Crossover

```python
from src.strategies.base_strategy import BaseStrategy
from src.strategies.technical_indicators import TechnicalIndicators

class MovingAverageCrossover(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "ma_crossover"
        self.short_period = config.get('short_period', 10)
        self.long_period = config.get('long_period', 20)
        self.indicators = TechnicalIndicators()
    
    def analyze(self, data: MarketData) -> TradingSignal:
        # Get historical data for calculations
        historical_data = self.get_historical_data(data.symbol, self.long_period + 5)
        
        if len(historical_data) < self.long_period:
            return self._hold_signal(data)
        
        # Calculate moving averages
        short_ma = self.indicators.sma(historical_data, self.short_period)
        long_ma = self.indicators.sma(historical_data, self.long_period)
        
        current_short = short_ma[-1]
        current_long = long_ma[-1]
        prev_short = short_ma[-2] if len(short_ma) > 1 else current_short
        prev_long = long_ma[-2] if len(long_ma) > 1 else current_long
        
        # Detect crossover
        if prev_short <= prev_long and current_short > current_long:
            # Golden cross - bullish signal
            return TradingSignal(
                symbol=data.symbol,
                action="BUY",
                confidence=0.8,
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={
                    "short_ma": current_short,
                    "long_ma": current_long,
                    "crossover_type": "golden"
                }
            )
        elif prev_short >= prev_long and current_short < current_long:
            # Death cross - bearish signal
            return TradingSignal(
                symbol=data.symbol,
                action="SELL",
                confidence=0.8,
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={
                    "short_ma": current_short,
                    "long_ma": current_long,
                    "crossover_type": "death"
                }
            )
        
        return self._hold_signal(data)
    
    def _hold_signal(self, data: MarketData) -> TradingSignal:
        return TradingSignal(
            symbol=data.symbol,
            action="HOLD",
            confidence=0.5,
            timestamp=data.timestamp,
            strategy_name=self.name,
            metadata={}
        )
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        if 'short_period' in params:
            self.short_period = max(1, int(params['short_period']))
        if 'long_period' in params:
            self.long_period = max(2, int(params['long_period']))
        
        if self.short_period >= self.long_period:
            raise ValueError("Short period must be less than long period")
    
    def get_required_indicators(self) -> List[str]:
        return ["sma"]
```

### 2. RSI Mean Reversion Strategy

```python
class RSIMeanReversion(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "rsi_mean_reversion"
        self.rsi_period = config.get('rsi_period', 14)
        self.oversold_threshold = config.get('oversold_threshold', 30)
        self.overbought_threshold = config.get('overbought_threshold', 70)
        self.indicators = TechnicalIndicators()
    
    def analyze(self, data: MarketData) -> TradingSignal:
        historical_data = self.get_historical_data(data.symbol, self.rsi_period + 10)
        
        if len(historical_data) < self.rsi_period + 1:
            return self._hold_signal(data)
        
        # Calculate RSI
        rsi_values = self.indicators.rsi(historical_data, self.rsi_period)
        current_rsi = rsi_values[-1]
        
        # Generate signals based on RSI levels
        if current_rsi < self.oversold_threshold:
            # Oversold - potential buy signal
            confidence = min(0.9, (self.oversold_threshold - current_rsi) / self.oversold_threshold)
            return TradingSignal(
                symbol=data.symbol,
                action="BUY",
                confidence=confidence,
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={
                    "rsi": current_rsi,
                    "threshold": self.oversold_threshold,
                    "condition": "oversold"
                }
            )
        elif current_rsi > self.overbought_threshold:
            # Overbought - potential sell signal
            confidence = min(0.9, (current_rsi - self.overbought_threshold) / (100 - self.overbought_threshold))
            return TradingSignal(
                symbol=data.symbol,
                action="SELL",
                confidence=confidence,
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={
                    "rsi": current_rsi,
                    "threshold": self.overbought_threshold,
                    "condition": "overbought"
                }
            )
        
        return self._hold_signal(data)
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        if 'rsi_period' in params:
            self.rsi_period = max(2, int(params['rsi_period']))
        if 'oversold_threshold' in params:
            self.oversold_threshold = max(0, min(50, float(params['oversold_threshold'])))
        if 'overbought_threshold' in params:
            self.overbought_threshold = max(50, min(100, float(params['overbought_threshold'])))
    
    def get_required_indicators(self) -> List[str]:
        return ["rsi"]
```

### 3. Multi-Indicator Strategy

```python
class MultiIndicatorStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "multi_indicator"
        self.ma_short = config.get('ma_short', 10)
        self.ma_long = config.get('ma_long', 20)
        self.rsi_period = config.get('rsi_period', 14)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        self.indicators = TechnicalIndicators()
    
    def analyze(self, data: MarketData) -> TradingSignal:
        required_periods = max(self.ma_long, self.rsi_period, self.macd_slow) + 10
        historical_data = self.get_historical_data(data.symbol, required_periods)
        
        if len(historical_data) < required_periods:
            return self._hold_signal(data)
        
        # Calculate all indicators
        sma_short = self.indicators.sma(historical_data, self.ma_short)
        sma_long = self.indicators.sma(historical_data, self.ma_long)
        rsi = self.indicators.rsi(historical_data, self.rsi_period)
        macd_line, macd_signal, macd_histogram = self.indicators.macd(
            historical_data, self.macd_fast, self.macd_slow, self.macd_signal
        )
        
        # Current values
        current_price = data.close
        current_sma_short = sma_short[-1]
        current_sma_long = sma_long[-1]
        current_rsi = rsi[-1]
        current_macd = macd_line[-1]
        current_macd_signal = macd_signal[-1]
        
        # Scoring system
        bullish_score = 0
        bearish_score = 0
        
        # MA trend
        if current_sma_short > current_sma_long:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # Price vs MA
        if current_price > current_sma_short:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # RSI conditions
        if current_rsi < 30:
            bullish_score += 2  # Oversold
        elif current_rsi > 70:
            bearish_score += 2  # Overbought
        elif 40 < current_rsi < 60:
            bullish_score += 0.5  # Neutral zone
        
        # MACD conditions
        if current_macd > current_macd_signal:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # Generate signal based on scores
        total_score = bullish_score + bearish_score
        if total_score == 0:
            return self._hold_signal(data)
        
        if bullish_score > bearish_score:
            confidence = min(0.9, bullish_score / total_score)
            if confidence > 0.6:
                return TradingSignal(
                    symbol=data.symbol,
                    action="BUY",
                    confidence=confidence,
                    timestamp=data.timestamp,
                    strategy_name=self.name,
                    metadata={
                        "bullish_score": bullish_score,
                        "bearish_score": bearish_score,
                        "rsi": current_rsi,
                        "macd": current_macd,
                        "price_vs_ma": current_price / current_sma_short
                    }
                )
        else:
            confidence = min(0.9, bearish_score / total_score)
            if confidence > 0.6:
                return TradingSignal(
                    symbol=data.symbol,
                    action="SELL",
                    confidence=confidence,
                    timestamp=data.timestamp,
                    strategy_name=self.name,
                    metadata={
                        "bullish_score": bullish_score,
                        "bearish_score": bearish_score,
                        "rsi": current_rsi,
                        "macd": current_macd,
                        "price_vs_ma": current_price / current_sma_short
                    }
                )
        
        return self._hold_signal(data)
    
    def update_parameters(self, params: Dict[str, Any]) -> None:
        # Update parameters with validation
        for param, value in params.items():
            if hasattr(self, param):
                setattr(self, param, value)
    
    def get_required_indicators(self) -> List[str]:
        return ["sma", "rsi", "macd"]
```

## Best Practices

### 1. Strategy Design Principles

- **Keep it simple**: Start with simple strategies and add complexity gradually
- **Validate inputs**: Always check if you have enough historical data
- **Handle edge cases**: Account for missing data, market closures, etc.
- **Use proper risk management**: Never risk more than you can afford to lose
- **Backtest thoroughly**: Test your strategy on historical data before live trading

### 2. Performance Optimization

```python
class OptimizedStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Cache frequently used calculations
        self._indicator_cache = {}
        self._last_calculation_time = None
    
    def analyze(self, data: MarketData) -> TradingSignal:
        # Use caching to avoid recalculating indicators
        cache_key = f"{data.symbol}_{data.timestamp}"
        
        if cache_key not in self._indicator_cache:
            self._indicator_cache[cache_key] = self._calculate_indicators(data)
        
        indicators = self._indicator_cache[cache_key]
        return self._generate_signal(data, indicators)
    
    def _calculate_indicators(self, data: MarketData) -> Dict[str, float]:
        # Expensive calculations here
        pass
```

### 3. Error Handling

```python
def analyze(self, data: MarketData) -> TradingSignal:
    try:
        # Strategy logic here
        return self._generate_signal(data)
    except Exception as e:
        self.logger.error(f"Strategy {self.name} failed: {str(e)}")
        # Return safe default signal
        return TradingSignal(
            symbol=data.symbol,
            action="HOLD",
            confidence=0.0,
            timestamp=data.timestamp,
            strategy_name=self.name,
            metadata={"error": str(e)}
        )
```

### 4. Configuration Management

```python
# strategy_config.yaml
strategies:
  my_custom_strategy:
    enabled: true
    parameters:
      short_period: 10
      long_period: 20
      risk_threshold: 0.02
    symbols:
      - "BTC/USDT"
      - "ETH/USDT"
    timeframes:
      - "1h"
      - "4h"
```

## Testing Your Strategy

### Unit Testing

```python
import unittest
from unittest.mock import Mock
from src.strategies.my_strategy import MyCustomStrategy

class TestMyCustomStrategy(unittest.TestCase):
    def setUp(self):
        self.config = {
            'short_period': 10,
            'long_period': 20
        }
        self.strategy = MyCustomStrategy(self.config)
    
    def test_bullish_signal(self):
        # Create mock data that should generate BUY signal
        mock_data = Mock()
        mock_data.symbol = "BTC/USDT"
        mock_data.close = 50000
        
        signal = self.strategy.analyze(mock_data)
        self.assertEqual(signal.action, "BUY")
        self.assertGreater(signal.confidence, 0.5)
    
    def test_parameter_update(self):
        new_params = {'short_period': 15}
        self.strategy.update_parameters(new_params)
        self.assertEqual(self.strategy.short_period, 15)
```

### Backtesting

```python
from src.backtesting.backtest_engine import BacktestEngine

# Load historical data
historical_data = load_historical_data("BTC/USDT", "2023-01-01", "2023-12-31")

# Initialize strategy
strategy = MyCustomStrategy(config)

# Run backtest
engine = BacktestEngine()
results = engine.run_backtest(
    strategy=strategy,
    data=historical_data,
    initial_capital=10000
)

# Analyze results
print(f"Total Return: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown:.2%}")
```

## Strategy Registration

### Automatic Registration

```python
# In your strategy file
from src.strategies.strategy_registry import strategy_registry

@strategy_registry.register("my_custom_strategy")
class MyCustomStrategy(BaseStrategy):
    # Strategy implementation
    pass
```

### Manual Registration

```python
from src.strategies.strategy_registry import StrategyRegistry

registry = StrategyRegistry()
registry.register_strategy("my_strategy", MyCustomStrategy)
```

## Deployment

### Configuration File

```yaml
# config/strategies/my_strategy.yaml
name: "my_custom_strategy"
version: "1.0.0"
enabled: true
parameters:
  short_period: 10
  long_period: 20
  confidence_threshold: 0.6
symbols:
  - "BTC/USDT"
  - "ETH/USDT"
risk_management:
  max_position_size: 0.1
  stop_loss_percentage: 0.05
```

### Loading Strategy

```python
from src.strategies.strategy_engine import StrategyEngine

engine = StrategyEngine()
engine.load_strategy_from_config("config/strategies/my_strategy.yaml")
engine.start()
```

## Advanced Topics

### Machine Learning Integration

```python
import joblib
from sklearn.ensemble import RandomForestClassifier

class MLStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = joblib.load(config['model_path'])
        self.feature_columns = config['feature_columns']
    
    def analyze(self, data: MarketData) -> TradingSignal:
        features = self._extract_features(data)
        prediction = self.model.predict_proba([features])[0]
        
        # Convert ML prediction to trading signal
        if prediction[1] > 0.7:  # Buy class
            return TradingSignal(
                symbol=data.symbol,
                action="BUY",
                confidence=prediction[1],
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={"ml_prediction": prediction.tolist()}
            )
        elif prediction[0] > 0.7:  # Sell class
            return TradingSignal(
                symbol=data.symbol,
                action="SELL",
                confidence=prediction[0],
                timestamp=data.timestamp,
                strategy_name=self.name,
                metadata={"ml_prediction": prediction.tolist()}
            )
        
        return self._hold_signal(data)
```

### Portfolio-Level Strategies

```python
class PortfolioStrategy(BaseStrategy):
    def analyze_portfolio(self, portfolio_data: Dict[str, MarketData]) -> List[TradingSignal]:
        """Analyze entire portfolio and generate signals for multiple symbols"""
        signals = []
        
        # Calculate portfolio-level metrics
        total_value = sum(data.close for data in portfolio_data.values())
        
        for symbol, data in portfolio_data.items():
            weight = data.close / total_value
            signal = self._analyze_symbol_in_context(data, weight, portfolio_data)
            signals.append(signal)
        
        return signals
```

This guide provides a comprehensive foundation for developing custom trading strategies. Remember to always test your strategies thoroughly before deploying them with real money.