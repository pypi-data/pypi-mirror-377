# Trading Bot CLI User Guide

## Overview

The Trading Bot CLI is a comprehensive command-line interface for managing your multi-market trading bot. It provides easy-to-use commands for:

- **Account Management**: Add, remove, enable/disable crypto exchanges and forex brokers
- **Account Validation**: Verify configurations before starting the bot
- **Bot Control**: Start, stop, and monitor the trading bot
- **Reporting**: Generate detailed trading reports and performance analysis

## Installation

### 1. Install CLI Dependencies

```bash
# Install CLI-specific dependencies
pip install -r requirements-cli.txt

# Or install individual packages
pip install colorama tabulate PyYAML python-dotenv pydantic
```

### 2. Make CLI Executable

```bash
# Make the CLI script executable
chmod +x scripts/trading_bot_cli.py

# Optional: Create a symlink for easier access
ln -s $(pwd)/scripts/trading_bot_cli.py /usr/local/bin/trading-bot
```

## Quick Start

### 1. Add Your First Exchange Account

```bash
# Add a crypto exchange (interactive mode)
python scripts/trading_bot_cli.py add-crypto

# Add a crypto exchange (command line mode)
python scripts/trading_bot_cli.py add-crypto \
  --name binance \
  --exchange-type binance \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --sandbox
```

### 2. Add a Forex Broker

```bash
# Add OANDA broker (interactive mode)
python scripts/trading_bot_cli.py add-forex

# Add OANDA broker (command line mode)
python scripts/trading_bot_cli.py add-forex \
  --name oanda \
  --broker-type oanda \
  --api-key YOUR_OANDA_API_KEY \
  --account-id YOUR_ACCOUNT_ID \
  --sandbox
```

### 3. Validate Your Accounts

```bash
# Validate all configured accounts
python scripts/trading_bot_cli.py validate-accounts
```

### 4. Start the Trading Bot

```bash
# Start the bot (validates accounts first)
python scripts/trading_bot_cli.py start
```

## Command Reference

### Account Management Commands

#### Add Crypto Exchange

```bash
python scripts/trading_bot_cli.py add-crypto [OPTIONS]
```

**Options:**
- `--name TEXT`: Exchange name
- `--exchange-type CHOICE`: Exchange type (binance, coinbase, kraken, kucoin, bybit)
- `--api-key TEXT`: API key
- `--api-secret TEXT`: API secret
- `--api-passphrase TEXT`: API passphrase (required for Coinbase)
- `--sandbox`: Use sandbox/testnet mode
- `--rate-limit INTEGER`: Rate limit per minute (default: 1200)
- `--timeout INTEGER`: Request timeout in seconds (default: 30)
- `--enabled`: Enable the account
- `--force`: Overwrite existing account

**Examples:**

```bash
# Interactive mode
python scripts/trading_bot_cli.py add-crypto

# Binance testnet
python scripts/trading_bot_cli.py add-crypto \
  --name binance-testnet \
  --exchange-type binance \
  --api-key your_testnet_key \
  --api-secret your_testnet_secret \
  --sandbox \
  --enabled

# Coinbase Pro
python scripts/trading_bot_cli.py add-crypto \
  --name coinbase \
  --exchange-type coinbase \
  --api-key your_api_key \
  --api-secret your_api_secret \
  --api-passphrase your_passphrase
```

#### Add Forex Broker

```bash
python scripts/trading_bot_cli.py add-forex [OPTIONS]
```

**Options:**
- `--name TEXT`: Broker name
- `--broker-type CHOICE`: Broker type (oanda, mt5, interactive_brokers)
- `--api-key TEXT`: API key (OANDA)
- `--account-id TEXT`: Account ID (OANDA)
- `--server TEXT`: Server (MT5)
- `--login TEXT`: Login (MT5)
- `--password TEXT`: Password (MT5)
- `--host TEXT`: Host (Interactive Brokers)
- `--port INTEGER`: Port (Interactive Brokers)
- `--client-id INTEGER`: Client ID (Interactive Brokers)
- `--sandbox`: Use sandbox mode
- `--timeout INTEGER`: Request timeout in seconds
- `--enabled`: Enable the account
- `--force`: Overwrite existing account

**Examples:**

```bash
# OANDA demo account
python scripts/trading_bot_cli.py add-forex \
  --name oanda-demo \
  --broker-type oanda \
  --api-key your_demo_api_key \
  --account-id your_demo_account_id \
  --sandbox

# MetaTrader 5
python scripts/trading_bot_cli.py add-forex \
  --name mt5-demo \
  --broker-type mt5 \
  --server Demo-Server \
  --login 12345678 \
  --password your_password \
  --sandbox

# Interactive Brokers
python scripts/trading_bot_cli.py add-forex \
  --name ib-paper \
  --broker-type interactive_brokers \
  --host 127.0.0.1 \
  --port 7497 \
  --client-id 1 \
  --sandbox
```

#### List All Accounts

```bash
python scripts/trading_bot_cli.py list-accounts
```

This command displays all configured accounts in a formatted table showing:
- Account name and type
- Status (enabled/disabled)
- Mode (sandbox/live)
- Configuration details

#### Remove Account

```bash
python scripts/trading_bot_cli.py remove-account NAME TYPE
```

**Arguments:**
- `NAME`: Account name
- `TYPE`: Account type (crypto or forex)

**Examples:**

```bash
# Remove crypto exchange
python scripts/trading_bot_cli.py remove-account binance crypto

# Remove forex broker
python scripts/trading_bot_cli.py remove-account oanda forex
```

#### Enable/Disable Account

```bash
# Enable an account
python scripts/trading_bot_cli.py enable-account NAME TYPE

# Disable an account
python scripts/trading_bot_cli.py disable-account NAME TYPE
```

**Examples:**

```bash
# Enable binance exchange
python scripts/trading_bot_cli.py enable-account binance crypto

# Disable oanda broker
python scripts/trading_bot_cli.py disable-account oanda forex
```

#### Validate Accounts

```bash
python scripts/trading_bot_cli.py validate-accounts
```

This command:
- Validates all account configurations
- Checks for placeholder credentials
- Verifies required fields for each broker type
- Displays validation results in a formatted table

### Trading Bot Control Commands

#### Start Trading Bot

```bash
python scripts/trading_bot_cli.py start
```

This command:
1. Validates all configured accounts
2. Checks that at least one account is enabled
3. Starts the trading bot with validated accounts
4. Displays active accounts and their modes

#### Stop Trading Bot

```bash
python scripts/trading_bot_cli.py stop
```

Gracefully stops the running trading bot.

#### Bot Status

```bash
python scripts/trading_bot_cli.py status
```

Shows current bot status including:
- Running state
- Uptime
- Last started time
- Active accounts

### Reporting Commands

#### Generate Trading Reports

```bash
python scripts/trading_bot_cli.py report [OPTIONS]
```

**Options:**
- `--type CHOICE`: Report type (summary, detailed, performance, compliance)
- `--start-date DATE`: Start date (YYYY-MM-DD format)
- `--end-date DATE`: End date (YYYY-MM-DD format)
- `--output PATH`: Output file path

**Report Types:**

1. **Summary Report** (`--type summary`):
   - Total trades and P&L
   - Win rate and trade statistics
   - Breakdown by exchange and strategy

2. **Detailed Report** (`--type detailed`):
   - Individual trade details
   - Complete trade history table
   - All trade parameters

3. **Performance Report** (`--type performance`):
   - Performance metrics (Sharpe ratio, drawdown, etc.)
   - Best and worst trades
   - Risk-adjusted returns

4. **Compliance Report** (`--type compliance`):
   - Daily trading summaries
   - Large position reporting
   - Regulatory compliance data

**Examples:**

```bash
# Generate summary report for last 30 days
python scripts/trading_bot_cli.py report --type summary

# Generate detailed report for specific date range
python scripts/trading_bot_cli.py report \
  --type detailed \
  --start-date 2024-01-01 \
  --end-date 2024-01-31

# Generate performance report and save to file
python scripts/trading_bot_cli.py report \
  --type performance \
  --start-date 2024-01-01 \
  --output reports/performance_jan_2024.txt

# Generate compliance report
python scripts/trading_bot_cli.py report \
  --type compliance \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --output reports/compliance_2024.txt
```

## Configuration Files

The CLI manages configuration in the following files:

### Account Configuration (`config/accounts.yaml`)

```yaml
crypto_exchanges:
  binance:
    name: binance
    exchange_type: binance
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    sandbox: true
    rate_limit: 1200
    timeout: 30
    enabled: true

forex_brokers:
  oanda:
    name: oanda
    broker_type: oanda
    api_key: "your_oanda_api_key"
    account_id: "your_account_id"
    sandbox: true
    timeout: 30
    enabled: true
```

### Main Bot Configuration (`config/trading_bot_config.yaml`)

This file contains the main trading bot configuration including strategies, risk management, and other settings.

## Security Best Practices

### 1. Credential Management

**Never store credentials in plain text:**

```bash
# Use environment variables
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"

# Add to CLI command
python scripts/trading_bot_cli.py add-crypto \
  --name binance \
  --exchange-type binance \
  --api-key "$BINANCE_API_KEY" \
  --api-secret "$BINANCE_API_SECRET"
```

**Use .env files:**

```bash
# Create .env file
echo "BINANCE_API_KEY=your_api_key" >> .env
echo "BINANCE_API_SECRET=your_api_secret" >> .env

# CLI will automatically load from .env
```

### 2. Sandbox Mode

Always start with sandbox/testnet accounts:

```bash
# Always use --sandbox for testing
python scripts/trading_bot_cli.py add-crypto \
  --name binance-testnet \
  --exchange-type binance \
  --sandbox
```

### 3. File Permissions

Secure your configuration files:

```bash
# Restrict access to configuration files
chmod 600 config/accounts.yaml
chmod 600 .env
```

## Troubleshooting

### Common Issues

#### 1. "Exchange already exists" Error

```bash
# Use --force to overwrite
python scripts/trading_bot_cli.py add-crypto --name binance --force
```

#### 2. "Invalid configuration" Error

Check that all required fields are provided:
- Coinbase requires `api_passphrase`
- MT5 requires `server`, `login`, and `password`
- OANDA requires `api_key` and `account_id`

#### 3. "No accounts configured" Warning

Add at least one account before starting the bot:

```bash
python scripts/trading_bot_cli.py add-crypto
python scripts/trading_bot_cli.py validate-accounts
python scripts/trading_bot_cli.py start
```

#### 4. Validation Warnings

"Appears to have placeholder credentials" - Replace placeholder values with real credentials:

```bash
# Check for placeholder patterns
grep -i "placeholder\|example\|test_\|your_" config/accounts.yaml
```

### Getting Help

```bash
# General help
python scripts/trading_bot_cli.py --help

# Command-specific help
python scripts/trading_bot_cli.py add-crypto --help
python scripts/trading_bot_cli.py report --help
```

## Advanced Usage

### 1. Batch Account Setup

Create a script to set up multiple accounts:

```bash
#!/bin/bash
# setup_accounts.sh

# Add multiple crypto exchanges
python scripts/trading_bot_cli.py add-crypto \
  --name binance --exchange-type binance \
  --api-key "$BINANCE_API_KEY" --api-secret "$BINANCE_API_SECRET" \
  --sandbox

python scripts/trading_bot_cli.py add-crypto \
  --name coinbase --exchange-type coinbase \
  --api-key "$COINBASE_API_KEY" --api-secret "$COINBASE_API_SECRET" \
  --api-passphrase "$COINBASE_PASSPHRASE" --sandbox

# Add forex brokers
python scripts/trading_bot_cli.py add-forex \
  --name oanda --broker-type oanda \
  --api-key "$OANDA_API_KEY" --account-id "$OANDA_ACCOUNT_ID" \
  --sandbox

# Validate all accounts
python scripts/trading_bot_cli.py validate-accounts
```

### 2. Automated Reporting

Set up automated daily reports:

```bash
#!/bin/bash
# daily_report.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/daily"
mkdir -p "$REPORT_DIR"

# Generate daily summary
python scripts/trading_bot_cli.py report \
  --type summary \
  --start-date "$DATE" \
  --end-date "$DATE" \
  --output "$REPORT_DIR/summary_$DATE.txt"

# Generate performance report for last 7 days
WEEK_AGO=$(date -d '7 days ago' +%Y-%m-%d)
python scripts/trading_bot_cli.py report \
  --type performance \
  --start-date "$WEEK_AGO" \
  --end-date "$DATE" \
  --output "$REPORT_DIR/performance_weekly_$DATE.txt"
```

### 3. Configuration Backup

Backup your account configurations:

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup account configurations
cp config/accounts.yaml "$BACKUP_DIR/"
cp config/trading_bot_config.yaml "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || true

echo "Configuration backed up to $BACKUP_DIR"
```

## Integration with Trading Bot

The CLI integrates seamlessly with the main trading bot:

1. **Account configurations** are automatically loaded by the bot
2. **Validation** ensures accounts are properly configured before bot startup
3. **Reports** are generated from the bot's trading database
4. **Bot control** commands interface with the main bot process

This provides a complete workflow from account setup to bot operation and performance analysis.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the command help: `python scripts/trading_bot_cli.py COMMAND --help`
3. Check the main trading bot documentation
4. Verify your account configurations with `validate-accounts`

The CLI is designed to be intuitive and self-documenting. Most commands provide interactive prompts when required information is not provided via command-line arguments.