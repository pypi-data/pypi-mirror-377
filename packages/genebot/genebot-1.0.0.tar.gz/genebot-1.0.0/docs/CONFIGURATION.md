# Configuration Reference

## Overview

The Trading Bot Python system uses a hierarchical configuration system that supports YAML files, environment variables, and runtime parameter updates. This document provides comprehensive reference for all configuration options.

## Configuration Structure

### Main Configuration File

The main configuration file is located at `config/trading_bot_config.yaml`:

```yaml
# Trading Bot Configuration
version: "1.0.0"
environment: "development"  # development, staging, production

# Application Settings
app:
  name: "TradingBot"
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  timezone: "UTC"
  data_retention_days: 30
  max_concurrent_strategies: 5

# Database Configuration
database:
  url: "${DATABASE_URL}"  # Environment variable
  pool_size: 10
  max_overflow: 20
  echo: false  # Set to true for SQL query logging
  
  # Alternative SQLite configuration
  # url: "sqlite:///trading_bot.db"

# Exchange Configuration
exchanges:
  binance:
    enabled: true
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true  # Use testnet for development
    rate_limit: 1200  # Requests per minute
    timeout: 30  # Connection timeout in seconds
    
  coinbase:
    enabled: false
    api_key: "${COINBASE_API_KEY}"
    api_secret: "${COINBASE_API_SECRET}"
    passphrase: "${COINBASE_PASSPHRASE}"
    sandbox: true
    rate_limit: 600
    timeout: 30

# Strategy Configuration
strategies:
  moving_average:
    enabled: true
    class: "MovingAverageStrategy"
    parameters:
      short_period: 10
      long_period: 20
      confidence_threshold: 0.7
    symbols:
      - "BTC/USDT"
      - "ETH/USDT"
    timeframes:
      - "1h"
      - "4h"
    
  rsi_strategy:
    enabled: true
    class: "RSIStrategy"
    parameters:
      period: 14
      oversold_threshold: 30
      overbought_threshold: 70
    symbols:
      - "BTC/USDT"
      - "ETH/USDT"
      - "ADA/USDT"
    timeframes:
      - "1h"

# Risk Management Configuration
risk_management:
  global:
    max_portfolio_risk: 0.02  # 2% of portfolio per trade
    max_daily_loss: 0.05      # 5% daily loss limit
    max_drawdown: 0.15        # 15% maximum drawdown
    position_sizing_method: "fixed_fractional"  # fixed_fractional, kelly, equal_weight
    
  stop_loss:
    enabled: true
    default_percentage: 0.05  # 5% stop loss
    trailing_stop: true
    trailing_percentage: 0.03  # 3% trailing stop
    
  position_limits:
    max_position_size: 0.1    # 10% of portfolio per position
    max_positions: 10         # Maximum number of open positions
    min_trade_amount: 10      # Minimum trade amount in base currency

# Data Collection Configuration
data:
  collection:
    enabled: true
    symbols:
      - "BTC/USDT"
      - "ETH/USDT"
      - "ADA/USDT"
      - "DOT/USDT"
    timeframes:
      - "1m"
      - "5m"
      - "1h"
      - "4h"
      - "1d"
    
  storage:
    compress_data: true
    backup_enabled: true
    backup_interval_hours: 24
    
  validation:
    check_data_integrity: true
    remove_outliers: true
    outlier_threshold: 3.0  # Standard deviations

# Monitoring Configuration
monitoring:
  enabled: true
  metrics_port: 8000
  health_check_port: 8001
  
  prometheus:
    enabled: true
    port: 9090
    scrape_interval: "15s"
    
  alerting:
    enabled: true
    channels:
      - type: "email"
        smtp_server: "${SMTP_SERVER}"
        smtp_port: 587
        username: "${SMTP_USERNAME}"
        password: "${SMTP_PASSWORD}"
        recipients:
          - "admin@example.com"
      
      - type: "slack"
        webhook_url: "${SLACK_WEBHOOK_URL}"
        channel: "#trading-alerts"
    
    rules:
      - name: "high_loss"
        condition: "daily_pnl < -0.03"
        severity: "critical"
        message: "Daily loss exceeds 3%"
        
      - name: "strategy_failure"
        condition: "strategy_errors > 5"
        severity: "warning"
        message: "Strategy generating multiple errors"

# Backtesting Configuration
backtesting:
  default_capital: 10000
  commission: 0.001  # 0.1% commission
  slippage: 0.0005   # 0.05% slippage
  
  performance_metrics:
    - "total_return"
    - "sharpe_ratio"
    - "max_drawdown"
    - "win_rate"
    - "profit_factor"
    - "calmar_ratio"

# Logging Configuration
logging:
  version: 1
  disable_existing_loggers: false
  
  formatters:
    standard:
      format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    json:
      format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
  
  handlers:
    console:
      class: "logging.StreamHandler"
      level: "INFO"
      formatter: "standard"
      stream: "ext://sys.stdout"
    
    file:
      class: "logging.handlers.RotatingFileHandler"
      level: "DEBUG"
      formatter: "json"
      filename: "logs/trading_bot.log"
      maxBytes: 10485760  # 10MB
      backupCount: 5
    
    error_file:
      class: "logging.handlers.RotatingFileHandler"
      level: "ERROR"
      formatter: "json"
      filename: "logs/errors.log"
      maxBytes: 10485760
      backupCount: 5
  
  loggers:
    "":
      level: "INFO"
      handlers: ["console", "file"]
      propagate: false
    
    "trading_bot.errors":
      level: "ERROR"
      handlers: ["error_file"]
      propagate: false
```

## Environment Variables

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/trading_bot
# Or for SQLite: DATABASE_URL=sqlite:///trading_bot.db

# Exchange API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

COINBASE_API_KEY=your_coinbase_api_key
COINBASE_API_SECRET=your_coinbase_api_secret
COINBASE_PASSPHRASE=your_coinbase_passphrase

# Monitoring and Alerting
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Security
SECRET_KEY=your_secret_key_for_encryption
JWT_SECRET=your_jwt_secret_for_api_auth

# Optional: Override configuration values
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Environment-Specific Configuration

#### Development Environment

```yaml
# config/environments/development.yaml
environment: "development"
app:
  log_level: "DEBUG"
exchanges:
  binance:
    sandbox: true
  coinbase:
    sandbox: true
database:
  echo: true  # Enable SQL logging
monitoring:
  alerting:
    enabled: false  # Disable alerts in development
```

#### Production Environment

```yaml
# config/environments/production.yaml
environment: "production"
app:
  log_level: "INFO"
exchanges:
  binance:
    sandbox: false
  coinbase:
    sandbox: false
database:
  echo: false
  pool_size: 20
  max_overflow: 40
monitoring:
  alerting:
    enabled: true
risk_management:
  global:
    max_portfolio_risk: 0.01  # More conservative in production
```

## Configuration Validation

### Schema Validation

The system uses Pydantic models for configuration validation:

```python
from pydantic import BaseModel, validator
from typing import List, Dict, Optional

class ExchangeConfig(BaseModel):
    enabled: bool = True
    api_key: str
    api_secret: str
    sandbox: bool = True
    rate_limit: int = 1200
    timeout: int = 30
    
    @validator('rate_limit')
    def validate_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('Rate limit must be positive')
        return v

class StrategyConfig(BaseModel):
    enabled: bool = True
    class_name: str = Field(alias='class')
    parameters: Dict[str, Any] = {}
    symbols: List[str] = []
    timeframes: List[str] = ['1h']
    
    @validator('symbols')
    def validate_symbols(cls, v):
        if not v:
            raise ValueError('At least one symbol must be specified')
        return v

class RiskManagementConfig(BaseModel):
    max_portfolio_risk: float = 0.02
    max_daily_loss: float = 0.05
    max_drawdown: float = 0.15
    
    @validator('max_portfolio_risk', 'max_daily_loss', 'max_drawdown')
    def validate_risk_percentages(cls, v):
        if not 0 < v <= 1:
            raise ValueError('Risk percentages must be between 0 and 1')
        return v
```

### Configuration Loading

```python
from config.manager import ConfigManager

# Load configuration
config_manager = ConfigManager()
config_manager.load_config('config/trading_bot_config.yaml')

# Load environment-specific overrides
config_manager.load_environment_config('development')

# Validate configuration
if config_manager.validate():
    print("Configuration is valid")
else:
    print("Configuration validation failed")
```

## Dynamic Configuration Updates

### Runtime Parameter Updates

```python
# Update strategy parameters at runtime
config_manager.update_strategy_parameters('moving_average', {
    'short_period': 12,
    'long_period': 26
})

# Update risk management settings
config_manager.update_risk_settings({
    'max_portfolio_risk': 0.015,
    'stop_loss_percentage': 0.04
})
```

### Configuration Hot Reload

```python
# Enable configuration hot reload
config_manager.enable_hot_reload(interval=60)  # Check every 60 seconds

# Register callback for configuration changes
def on_config_change(section, old_value, new_value):
    print(f"Configuration changed: {section}")
    # Handle configuration change

config_manager.register_change_callback(on_config_change)
```

## Advanced Configuration

### Custom Strategy Configuration

```yaml
strategies:
  custom_ml_strategy:
    enabled: true
    class: "MLStrategy"
    parameters:
      model_path: "models/random_forest_model.pkl"
      feature_columns:
        - "rsi"
        - "macd"
        - "bollinger_bands"
      prediction_threshold: 0.7
      retrain_interval_days: 7
    symbols:
      - "BTC/USDT"
    timeframes:
      - "1h"
    
    # Custom configuration sections
    model_config:
      type: "random_forest"
      n_estimators: 100
      max_depth: 10
      random_state: 42
    
    feature_engineering:
      lookback_periods: [5, 10, 20]
      technical_indicators:
        - "sma"
        - "ema"
        - "rsi"
        - "macd"
        - "bollinger_bands"
```

### Multi-Exchange Configuration

```yaml
exchanges:
  binance:
    enabled: true
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    symbols:
      - "BTC/USDT"
      - "ETH/USDT"
    
  coinbase:
    enabled: true
    api_key: "${COINBASE_API_KEY}"
    api_secret: "${COINBASE_API_SECRET}"
    symbols:
      - "BTC-USD"
      - "ETH-USD"
    
  kraken:
    enabled: false
    api_key: "${KRAKEN_API_KEY}"
    api_secret: "${KRAKEN_API_SECRET}"
    symbols:
      - "XBTUSD"
      - "ETHUSD"

# Symbol mapping between exchanges
symbol_mapping:
  "BTC/USDT": 
    binance: "BTCUSDT"
    coinbase: "BTC-USD"
    kraken: "XBTUSD"
  "ETH/USDT":
    binance: "ETHUSDT"
    coinbase: "ETH-USD"
    kraken: "ETHUSD"
```

### Performance Optimization Configuration

```yaml
performance:
  # Threading configuration
  max_worker_threads: 4
  strategy_execution_timeout: 30
  
  # Caching configuration
  cache:
    enabled: true
    type: "redis"  # redis, memory
    redis_url: "${REDIS_URL}"
    ttl_seconds: 300
    max_size: 1000
  
  # Data processing optimization
  data_processing:
    batch_size: 1000
    parallel_processing: true
    max_parallel_workers: 2
    
  # Memory management
  memory:
    max_memory_usage_mb: 1024
    garbage_collection_interval: 300
```

## Configuration Best Practices

### 1. Security

- Never commit API keys or secrets to version control
- Use environment variables for sensitive data
- Encrypt configuration files in production
- Rotate API keys regularly
- Use separate API keys for different environments

### 2. Environment Management

- Use separate configuration files for each environment
- Override sensitive settings with environment variables
- Validate configuration on startup
- Use configuration schemas for validation
- Document all configuration options

### 3. Performance

- Cache frequently accessed configuration values
- Use lazy loading for large configuration sections
- Minimize configuration file size
- Use appropriate data types for configuration values
- Profile configuration loading performance

### 4. Maintenance

- Version your configuration files
- Use meaningful names for configuration sections
- Group related configuration options
- Provide default values for optional settings
- Document configuration changes in changelog

## Troubleshooting

### Common Configuration Issues

1. **Invalid API Keys**
   ```
   Error: Exchange authentication failed
   Solution: Verify API keys and permissions
   ```

2. **Database Connection Failed**
   ```
   Error: Could not connect to database
   Solution: Check DATABASE_URL and database server status
   ```

3. **Configuration Validation Failed**
   ```
   Error: Invalid configuration value for 'max_portfolio_risk'
   Solution: Ensure risk values are between 0 and 1
   ```

4. **Missing Environment Variables**
   ```
   Error: Environment variable 'BINANCE_API_KEY' not found
   Solution: Create .env file with required variables
   ```

### Configuration Debugging

```python
# Enable configuration debugging
import logging
logging.getLogger('config').setLevel(logging.DEBUG)

# Print current configuration
config_manager.print_config()

# Validate specific configuration section
config_manager.validate_section('exchanges')

# Check environment variable resolution
config_manager.check_env_vars()
```

This configuration reference provides comprehensive guidance for setting up and managing the Trading Bot Python system. Always test configuration changes in a development environment before applying them to production.