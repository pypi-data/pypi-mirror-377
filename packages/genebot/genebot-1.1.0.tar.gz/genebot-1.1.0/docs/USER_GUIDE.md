# Trading Bot User Guide

## Overview

This comprehensive user guide provides step-by-step instructions for operating and monitoring the Trading Bot Python system. Whether you're a beginner or experienced trader, this guide will help you effectively use the bot for automated trading.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Running the Bot](#running-the-bot)
4. [Monitoring and Alerts](#monitoring-and-alerts)
5. [Strategy Management](#strategy-management)
6. [Risk Management](#risk-management)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

Before using the trading bot, ensure you have:

- Python 3.9 or higher installed
- Exchange API keys (with appropriate permissions)
- Basic understanding of trading concepts
- Sufficient capital for trading (start small!)

### Initial Setup

1. **Clone and Install**
   ```bash
   git clone https://github.com/your-org/trading-bot-python.git
   cd trading-bot-python
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Configure Database**
   ```bash
   # For development (SQLite)
   export DATABASE_URL="sqlite:///trading_bot.db"
   
   # For production (PostgreSQL)
   export DATABASE_URL="postgresql://user:pass@localhost:5432/trading_bot"
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

### First Run (Paper Trading)

Always start with paper trading to familiarize yourself with the system:

```bash
# Set paper trading mode
export PAPER_TRADING=true

# Start the bot
python main.py
```

## Configuration

### Basic Configuration

The main configuration file is `config/trading_bot_config.yaml`. Key sections include:

#### Exchange Settings
```yaml
exchanges:
  binance:
    enabled: true
    api_key: "${BINANCE_API_KEY}"
    api_secret: "${BINANCE_API_SECRET}"
    sandbox: true  # Start with testnet
```

#### Strategy Settings
```yaml
strategies:
  moving_average:
    enabled: true
    parameters:
      short_period: 10
      long_period: 20
    symbols:
      - "BTC/USDT"
    timeframes:
      - "1h"
```

#### Risk Management
```yaml
risk_management:
  global:
    max_portfolio_risk: 0.02  # 2% risk per trade
    max_daily_loss: 0.05      # 5% daily loss limit
```

### Environment-Specific Configurations

Use different configurations for different environments:

- `examples/configuration_examples/development_config.yaml` - For testing
- `examples/configuration_examples/production_config.yaml` - For live trading

## Running the Bot

### Command Line Interface

#### Basic Commands

```bash
# Start the bot
python main.py

# Start with specific config
python main.py --config config/my_config.yaml

# Start in paper trading mode
python main.py --paper-trading

# Start with specific log level
python main.py --log-level DEBUG

# Run backtest only
python main.py --backtest-only --start-date 2023-01-01 --end-date 2023-12-31
```

#### Advanced Options

```bash
# Start specific strategies only
python main.py --strategies moving_average,rsi_strategy

# Start with custom symbols
python main.py --symbols BTC/USDT,ETH/USDT

# Dry run (no actual trades)
python main.py --dry-run

# Enable profiling
python main.py --profile
```

### Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop the bot
docker-compose down
```

### Systemd Service (Linux)

Create a systemd service for automatic startup:

```ini
# /etc/systemd/system/trading-bot.service
[Unit]
Description=Trading Bot Python
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/opt/trading-bot
ExecStart=/opt/trading-bot/venv/bin/python main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/trading-bot

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# Check status
sudo systemctl status trading-bot
```

## Monitoring and Alerts

### Web Dashboard

Access the monitoring dashboard at `http://localhost:8000` (or your configured port).

#### Key Metrics to Monitor

1. **Portfolio Performance**
   - Total P&L
   - Daily P&L
   - Win rate
   - Sharpe ratio

2. **Strategy Performance**
   - Signal frequency
   - Strategy accuracy
   - Individual strategy P&L

3. **Risk Metrics**
   - Current drawdown
   - Position sizes
   - Risk exposure

4. **System Health**
   - Exchange connectivity
   - Data feed status
   - Error rates

### Grafana Dashboards

If using Grafana (recommended for production):

1. **Access Grafana**: `http://localhost:3000`
2. **Default credentials**: admin/admin
3. **Import dashboards** from `deployment/grafana/dashboards/`

#### Key Dashboards

- **Trading Bot Overview**: High-level performance metrics
- **Strategy Analysis**: Detailed strategy performance
- **Risk Monitoring**: Risk metrics and alerts
- **System Health**: Technical system metrics

### Alert Configuration

#### Email Alerts

Configure SMTP settings in your environment:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

#### Slack Alerts

Set up Slack webhook:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

#### Alert Rules

Common alert configurations:

```yaml
alerting:
  rules:
    - name: "high_loss"
      condition: "daily_pnl < -0.03"
      severity: "critical"
      message: "Daily loss exceeds 3%"
      
    - name: "strategy_failure"
      condition: "strategy_errors > 5"
      severity: "warning"
      message: "Strategy generating errors"
```

### Log Monitoring

#### Log Locations

- **Application logs**: `logs/trading_bot.log`
- **Error logs**: `logs/errors.log`
- **Trade logs**: `logs/trades.log`

#### Log Analysis

```bash
# View recent logs
tail -f logs/trading_bot.log

# Search for errors
grep "ERROR" logs/trading_bot.log

# View trade history
grep "TRADE_EXECUTED" logs/trades.log | jq '.'

# Monitor specific strategy
grep "moving_average" logs/trading_bot.log
```

## Strategy Management

### Enabling/Disabling Strategies

#### Via Configuration File

```yaml
strategies:
  moving_average:
    enabled: false  # Disable strategy
```

#### Via API (if enabled)

```bash
# Disable strategy
curl -X POST http://localhost:8000/api/strategies/moving_average/disable

# Enable strategy
curl -X POST http://localhost:8000/api/strategies/moving_average/enable

# Update parameters
curl -X PUT http://localhost:8000/api/strategies/moving_average/parameters \
  -H "Content-Type: application/json" \
  -d '{"short_period": 12, "long_period": 24}'
```

### Strategy Performance Analysis

#### Viewing Strategy Metrics

```bash
# Get strategy performance
python scripts/analyze_strategy.py --strategy moving_average --days 30

# Compare strategies
python scripts/compare_strategies.py --strategies moving_average,rsi_strategy
```

#### Backtesting Strategies

```bash
# Backtest single strategy
python scripts/backtest.py \
  --strategy moving_average \
  --symbol BTC/USDT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Backtest multiple strategies
python scripts/backtest.py \
  --strategies moving_average,rsi_strategy \
  --symbols BTC/USDT,ETH/USDT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31
```

### Adding New Strategies

1. **Create strategy file** in `src/strategies/`
2. **Inherit from BaseStrategy**
3. **Register strategy** in configuration
4. **Test thoroughly** before live trading

Example:
```python
from src.strategies.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def analyze(self, data):
        # Your strategy logic here
        pass
```

## Risk Management

### Position Sizing

The bot automatically calculates position sizes based on your risk settings:

```yaml
risk_management:
  global:
    max_portfolio_risk: 0.02  # 2% of portfolio at risk per trade
    position_sizing_method: "fixed_fractional"
```

### Stop Loss Management

Configure automatic stop losses:

```yaml
risk_management:
  stop_loss:
    enabled: true
    default_percentage: 0.05  # 5% stop loss
    trailing_stop: true
    trailing_percentage: 0.03  # 3% trailing stop
```

### Portfolio Limits

Set overall portfolio limits:

```yaml
risk_management:
  position_limits:
    max_position_size: 0.1    # 10% max per position
    max_positions: 5          # Maximum 5 open positions
    max_daily_loss: 0.05      # 5% daily loss limit
```

### Emergency Stop

#### Manual Emergency Stop

```bash
# Stop all trading immediately
python scripts/emergency_stop.py

# Close all positions
python scripts/close_all_positions.py
```

#### Automatic Circuit Breakers

The bot includes automatic circuit breakers:

- **Daily loss limit**: Stops trading if daily loss exceeds threshold
- **Drawdown limit**: Stops trading if drawdown exceeds threshold
- **Error threshold**: Stops trading if too many errors occur

## Troubleshooting

### Common Issues

#### 1. Bot Won't Start

**Symptoms**: Bot exits immediately or shows connection errors

**Solutions**:
```bash
# Check configuration
python -c "from config.manager import ConfigManager; ConfigManager().validate()"

# Test database connection
python -c "from src.database import test_connection; test_connection()"

# Verify API keys
python scripts/test_exchange_connection.py
```

#### 2. No Trading Signals

**Symptoms**: Bot runs but doesn't generate any trades

**Solutions**:
- Check strategy parameters (may be too restrictive)
- Verify market data is being received
- Review strategy logs for errors
- Test strategy with historical data

```bash
# Test strategy with recent data
python scripts/test_strategy.py --strategy moving_average --symbol BTC/USDT
```

#### 3. Exchange Connection Issues

**Symptoms**: API errors, connection timeouts

**Solutions**:
- Verify API keys and permissions
- Check exchange status
- Review rate limiting settings
- Test with different exchange endpoints

```bash
# Test exchange connectivity
python scripts/test_exchange.py --exchange binance
```

#### 4. High Memory Usage

**Symptoms**: Bot consumes excessive memory

**Solutions**:
- Reduce data retention period
- Limit number of symbols/timeframes
- Enable data compression
- Restart bot periodically

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Start with debug logging
python main.py --log-level DEBUG

# Enable profiling
python main.py --profile

# Memory tracking
python main.py --track-memory
```

### Health Checks

The bot provides health check endpoints:

```bash
# Check overall health
curl http://localhost:8001/health

# Check specific components
curl http://localhost:8001/health/database
curl http://localhost:8001/health/exchanges
curl http://localhost:8001/health/strategies
```

## Best Practices

### Security

1. **API Key Security**
   - Use environment variables for API keys
   - Enable IP restrictions on exchange accounts
   - Use read-only keys for monitoring
   - Rotate keys regularly

2. **System Security**
   - Run bot with limited user privileges
   - Use firewall to restrict network access
   - Keep system and dependencies updated
   - Monitor for unauthorized access

### Risk Management

1. **Start Small**
   - Begin with paper trading
   - Use small position sizes initially
   - Gradually increase exposure as confidence grows

2. **Diversification**
   - Don't put all capital in one strategy
   - Trade multiple uncorrelated assets
   - Use different timeframes

3. **Monitoring**
   - Check bot performance daily
   - Set up comprehensive alerts
   - Review and adjust strategies regularly

### Performance Optimization

1. **Resource Management**
   - Monitor CPU and memory usage
   - Optimize database queries
   - Use appropriate data retention periods

2. **Strategy Optimization**
   - Regularly backtest strategies
   - Monitor strategy performance metrics
   - Disable underperforming strategies

3. **Data Management**
   - Ensure reliable data feeds
   - Implement data validation
   - Have backup data sources

### Maintenance

1. **Regular Tasks**
   - Review logs weekly
   - Update dependencies monthly
   - Backup configuration and data
   - Test disaster recovery procedures

2. **Performance Review**
   - Monthly strategy performance review
   - Quarterly risk assessment
   - Annual system architecture review

### Documentation

1. **Keep Records**
   - Document configuration changes
   - Maintain trading journal
   - Record system modifications

2. **Version Control**
   - Use git for code changes
   - Tag releases
   - Maintain changelog

## Support and Community

### Getting Help

1. **Documentation**: Check this guide and API documentation
2. **Logs**: Review application logs for error details
3. **GitHub Issues**: Report bugs and feature requests
4. **Community**: Join discussions and share experiences

### Contributing

1. **Bug Reports**: Use GitHub issues with detailed information
2. **Feature Requests**: Describe use cases and benefits
3. **Code Contributions**: Follow contribution guidelines
4. **Documentation**: Help improve guides and examples

---

**Disclaimer**: Trading involves risk of loss. This bot is provided as-is without warranty. Always test thoroughly before live trading and never risk more than you can afford to lose.