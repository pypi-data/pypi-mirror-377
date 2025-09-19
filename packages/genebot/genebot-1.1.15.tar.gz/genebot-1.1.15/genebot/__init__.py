"""
GeneBot - Advanced Multi-Market Trading Bot
==========================================

A comprehensive trading bot supporting crypto exchanges and forex brokers
with advanced risk management, strategy orchestration, and multi-market capabilities.

Features:
- Multi-market trading (Crypto + Forex)
- Advanced strategy engine
- Comprehensive risk management
- Real-time monitoring and alerting
- Backtesting and performance analysis
- Compliance and audit trails
- Cross-market arbitrage
- Portfolio management

Author: GeneBot Development Team
Version: 1.1.14
License: MIT
"""

__version__ = "1.1.14"
__author__ = "GeneBot Development Team"
__email__ = "support@genebot.ai"
__description__ = "Advanced Multi-Market Trading Bot"

# Import core components
from .core import TradingBotOrchestrator

__all__ = [
    '__version__',
    '__author__',
    '__description__',
    'TradingBotOrchestrator'
]