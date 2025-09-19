# API Reference

## Overview

This document provides comprehensive API documentation for all public interfaces in the Trading Bot Python system.

## Core Components

### Configuration Manager

#### ConfigManager

Main configuration handler for the trading bot.

```python
from config.manager import ConfigManager

# Initialize configuration
config = ConfigManager()

# Load configuration from file
config.load_config("config/trading_bot_config.yaml")

# Get exchange configuration
exchange_config = config.get_exchange_config("binance")

# Get strategy configuration
strategy_config = config.get_strategy_config("moving_average")
```

**Methods:**

- `load_config(config_path: str) -> None`: Load configuration from YAML file
- `get_exchange_config(exchange_name: str) -> ExchangeConfig`: Get exchange-specific configuration
- `get_strategy_config(strategy_name: str) -> StrategyConfig`: Get strategy-specific configuration
- `validate_config() -> bool`: Validate all configuration settings

### Exchange Management

#### ExchangeAdapter (Abstract Base Class)

Base class for all exchange implementations.

```python
from src.exchanges.base import ExchangeAdapter

class CustomExchange(ExchangeAdapter):
    def connect(self) -> bool:
        # Implementation
        pass
    
    def get_market_data(self, symbol: str) -> MarketData:
        # Implementation
        pass
```

**Abstract Methods:**

- `connect() -> bool`: Establish connection to exchange
- `disconnect() -> None`: Close exchange connection
- `get_market_data(symbol: str) -> MarketData`: Fetch current market data
- `place_order(order: Order) -> str`: Place trading order
- `cancel_order(order_id: str) -> bool`: Cancel existing order
- `get_balance() -> Dict[str, float]`: Get account balance

#### CCXTAdapter

CCXT library wrapper for exchange operations.

```python
from src.exchanges.ccxt_adapter import CCXTAdapter

# Initialize exchange adapter
adapter = CCXTAdapter("binance", {
    "apiKey": "your_api_key",
    "secret": "your_secret",
    "sandbox": True
})

# Connect to exchange
if adapter.connect():
    # Get market data
    data = adapter.get_market_data("BTC/USDT")
    
    # Place order
    order_id = adapter.place_order(Order(
        symbol="BTC/USDT",
        side="buy",
        amount=0.001,
        price=50000,
        order_type="limit"
    ))
```

### Strategy Framework

#### BaseStrategy (Abstract Base Class)

Base class for all trading strategies.

```python
from src.strategies.base_strategy import BaseStrategy
from src.models.data_models import MarketData, TradingSignal

class MyStrategy(BaseStrategy):
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "my_strategy"
    
    def analyze(self, data: MarketData) -> TradingSignal:
        # Strategy logic here
        return TradingSignal(
            symbol=data.symbol,
            action="BUY",
            confidence=0.8,
            timestamp=data.timestamp,
            strategy_name=self.name
        )
```

**Abstract Methods:**

- `analyze(data: MarketData) -> TradingSignal`: Analyze market data and generate signal
- `update_parameters(params: dict) -> None`: Update strategy parameters
- `get_required_indicators() -> List[str]`: Get list of required technical indicators

#### StrategyEngine

Manages strategy lifecycle and execution.

```python
from src.strategies.strategy_engine import StrategyEngine

# Initialize strategy engine
engine = StrategyEngine()

# Register strategies
engine.register_strategy("moving_average", MovingAverageStrategy)
engine.register_strategy("rsi", RSIStrategy)

# Start strategy execution
engine.start()

# Get active strategies
active_strategies = engine.get_active_strategies()
```

**Methods:**

- `register_strategy(name: str, strategy_class: Type[BaseStrategy]) -> None`: Register strategy class
- `start() -> None`: Start strategy execution
- `stop() -> None`: Stop strategy execution
- `get_active_strategies() -> List[str]`: Get list of active strategy names

### Risk Management

#### RiskManager

Main risk control orchestrator.

```python
from src.risk.risk_manager import RiskManager

# Initialize risk manager
risk_manager = RiskManager(config)

# Check if order passes risk controls
order = Order(symbol="BTC/USDT", side="buy", amount=0.1)
if risk_manager.validate_order(order):
    # Order is safe to execute
    pass
```

**Methods:**

- `validate_order(order: Order) -> bool`: Validate order against risk rules
- `update_position(position: Position) -> None`: Update position tracking
- `check_drawdown() -> bool`: Check if drawdown limits exceeded
- `get_position_size(symbol: str, signal: TradingSignal) -> float`: Calculate appropriate position size

### Data Management

#### MarketDataCollector

Real-time and historical data collection.

```python
from src.data.collector import MarketDataCollector

# Initialize data collector
collector = MarketDataCollector(exchange_adapter)

# Start real-time data collection
collector.start_realtime_collection(["BTC/USDT", "ETH/USDT"])

# Get historical data
historical_data = collector.get_historical_data(
    symbol="BTC/USDT",
    timeframe="1h",
    start_date="2023-01-01",
    end_date="2023-12-31"
)
```

**Methods:**

- `start_realtime_collection(symbols: List[str]) -> None`: Start real-time data collection
- `stop_realtime_collection() -> None`: Stop real-time data collection
- `get_historical_data(symbol: str, timeframe: str, start_date: str, end_date: str) -> List[MarketData]`: Get historical market data

### Backtesting

#### BacktestEngine

Historical strategy testing and performance analysis.

```python
from src.backtesting.backtest_engine import BacktestEngine

# Initialize backtest engine
engine = BacktestEngine()

# Run backtest
results = engine.run_backtest(
    strategy=MovingAverageStrategy(),
    data=historical_data,
    initial_capital=10000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Generate report
engine.generate_report(results, "backtest_report.html")
```

**Methods:**

- `run_backtest(strategy: BaseStrategy, data: List[MarketData], **kwargs) -> BacktestResults`: Run strategy backtest
- `generate_report(results: BacktestResults, output_path: str) -> None`: Generate HTML report

## Data Models

### MarketData

```python
@dataclass
class MarketData:
    symbol: str          # Trading pair symbol (e.g., "BTC/USDT")
    timestamp: datetime  # Data timestamp
    open: float         # Opening price
    high: float         # Highest price
    low: float          # Lowest price
    close: float        # Closing price
    volume: float       # Trading volume
    exchange: str       # Exchange name
```

### TradingSignal

```python
@dataclass
class TradingSignal:
    symbol: str          # Trading pair symbol
    action: str          # Action: "BUY", "SELL", "HOLD"
    confidence: float    # Signal confidence (0.0 to 1.0)
    timestamp: datetime  # Signal timestamp
    strategy_name: str   # Name of generating strategy
    metadata: Dict[str, Any]  # Additional signal data
```

### Order

```python
@dataclass
class Order:
    id: str             # Unique order identifier
    symbol: str         # Trading pair symbol
    side: str           # Order side: "buy" or "sell"
    amount: float       # Order amount
    price: float        # Order price
    order_type: str     # Order type: "market", "limit", "stop"
    status: str         # Order status
    timestamp: datetime # Order timestamp
    exchange: str       # Exchange name
```

### Position

```python
@dataclass
class Position:
    symbol: str          # Trading pair symbol
    size: float          # Position size (positive for long, negative for short)
    entry_price: float   # Average entry price
    current_price: float # Current market price
    unrealized_pnl: float # Unrealized profit/loss
    timestamp: datetime  # Last update timestamp
```

## Error Handling

### Exception Hierarchy

```python
# Base exception
class TradingBotException(Exception):
    """Base exception for trading bot"""

# Specific exceptions
class ExchangeException(TradingBotException):
    """Exchange-related errors"""

class StrategyException(TradingBotException):
    """Strategy execution errors"""

class RiskException(TradingBotException):
    """Risk management violations"""

class DataException(TradingBotException):
    """Data-related errors"""
```

## Configuration Reference

See [Configuration Guide](CONFIGURATION.md) for detailed configuration options.

## Examples

See the `examples/` directory for complete usage examples:

- `examples/basic_strategies_example.py` - Basic strategy implementation
- `examples/exchange_example.py` - Exchange connectivity
- `examples/backtesting_example.py` - Backtesting workflow
- `examples/risk_management_example.py` - Risk management setup