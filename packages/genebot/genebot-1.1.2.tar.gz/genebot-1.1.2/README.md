# Trading Bot Python

A comprehensive Python trading bot for cryptocurrency markets with support for multiple exchanges, configurable strategies, and robust risk management.

## Features

- **Multi-Exchange Support**: Connect to multiple cryptocurrency exchanges via CCXT
- **Configurable Strategies**: Pluggable trading strategy framework
- **Risk Management**: Comprehensive capital protection mechanisms
- **Data Management**: Historical data collection and storage
- **Backtesting**: Test strategies against historical data
- **Monitoring**: Extensive logging and performance tracking

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd trading-bot-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add your exchange API keys and other settings
```

### 3. Run the Bot

```bash
# Run the main application
python main.py
```

## Project Structure

```
trading-bot-python/
├── src/                    # Source code
│   └── __init__.py
├── tests/                  # Test files
│   └── __init__.py
├── config/                 # Configuration files
│   ├── __init__.py
│   └── logging.py         # Logging configuration
├── docs/                   # Documentation
│   └── README.md
├── main.py                 # Application entry point
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Configuration

The bot uses environment variables for configuration. Key settings include:

- **Database**: SQLite or PostgreSQL connection
- **Exchanges**: API keys for supported exchanges
- **Risk Management**: Position limits and stop-loss settings
- **Logging**: Log level and output format

See `.env.example` for all available configuration options.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Requirements

- Python 3.8+
- Virtual environment (recommended)
- Exchange API keys for trading
- Database (SQLite for development, PostgreSQL for production)

## Security

- Never commit API keys or sensitive data
- Use environment variables for configuration
- Enable sandbox mode for testing
- Implement proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss. Use at your own risk.