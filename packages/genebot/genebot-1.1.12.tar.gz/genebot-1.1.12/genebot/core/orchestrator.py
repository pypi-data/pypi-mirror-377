"""
Trading Bot Orchestrator - Comprehensive Multi-Strategy Trading System

This orchestrator manages all trading strategies simultaneously and implements
aggressive exit strategies to avoid greediness and maximize profits.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

from ..strategies import (
    StrategyEngine, StrategyRegistry, SignalProcessor, StrategyConfigManager,
    MovingAverageStrategy, RSIStrategy, MultiIndicatorStrategy,
    AdvancedMomentumStrategy, MeanReversionStrategy, ATRVolatilityStrategy
)

# Conditional ML import
try:
    from ..strategies import MLPatternStrategy
    ML_AVAILABLE = True
except ImportError:
    MLPatternStrategy = None
    ML_AVAILABLE = False

from ..models.data_models import MarketData, TradingSignal, SignalAction, Position, Order
from ..exceptions import StrategyException, RiskException, TradingBotException
from ..utils.graceful_degradation import graceful_degradation_manager, ComponentStatus, ServiceLevel
from ..utils.retry_handler import retry_with_backoff


class PositionStatus(Enum):
    """Position status enumeration."""
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class ExitReason(Enum):
    """Exit reason enumeration."""
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    TRAILING_STOP = "TRAILING_STOP"
    TIME_EXIT = "TIME_EXIT"
    SIGNAL_REVERSAL = "SIGNAL_REVERSAL"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    PROFIT_PROTECTION = "PROFIT_PROTECTION"


@dataclass
class TradingPosition:
    """Enhanced position with exit management."""
    symbol: str
    side: str  # 'BUY' or 'SELL'
    entry_price: Decimal
    quantity: Decimal
    entry_time: datetime
    strategy_name: str
    confidence: float
    
    # Exit management
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None
    max_profit: Decimal = field(default_factory=lambda: Decimal('0'))
    status: PositionStatus = PositionStatus.OPEN
    
    # Risk management
    max_hold_time: timedelta = field(default_factory=lambda: timedelta(hours=24))
    profit_protection_threshold: float = 0.02  # 2% profit protection
    
    def update_profit_tracking(self, current_price: Decimal):
        """Update profit tracking and trailing stops."""
        if self.side == 'BUY':
            current_profit = (current_price - self.entry_price) / self.entry_price
        else:
            current_profit = (self.entry_price - current_price) / self.entry_price
        
        if current_profit > float(self.max_profit):
            self.max_profit = Decimal(str(current_profit))
            
            # Update trailing stop
            if self.trailing_stop and current_profit > 0.01:  # 1% minimum profit
                if self.side == 'BUY':
                    new_trailing = current_price * Decimal('0.98')  # 2% trailing
                    if not self.trailing_stop or new_trailing > self.trailing_stop:
                        self.trailing_stop = new_trailing
                else:
                    new_trailing = current_price * Decimal('1.02')  # 2% trailing
                    if not self.trailing_stop or new_trailing < self.trailing_stop:
                        self.trailing_stop = new_trailing


@dataclass
class RiskLimits:
    """Risk management limits."""
    max_portfolio_risk: float = 0.02  # 2% max portfolio risk per trade
    max_daily_loss: float = 0.05  # 5% max daily loss
    max_positions: int = 5  # Maximum concurrent positions
    max_position_size: float = 0.10  # 10% max position size
    correlation_limit: float = 0.7  # Maximum correlation between positions


class TradingBotOrchestrator:
    """
    Comprehensive trading bot orchestrator that manages all strategies
    and implements aggressive exit strategies to avoid greediness.
    """
    
    def __init__(self, initial_capital: Decimal = Decimal('100000')):
        """
        Initialize the trading bot orchestrator.
        
        Args:
            initial_capital: Initial trading capital
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = Decimal('0')
        self.total_pnl = Decimal('0')
        
        # Strategy components
        self.strategy_registry = StrategyRegistry()
        self.signal_processor = SignalProcessor()
        self.strategy_engine = StrategyEngine(
            self.strategy_registry, 
            self.signal_processor, 
            max_workers=6
        )
        self.config_manager = StrategyConfigManager()
        
        # Position management
        self.positions: Dict[str, TradingPosition] = {}
        self.closed_positions: List[TradingPosition] = []
        self.risk_limits = RiskLimits()
        
        # State management
        self.is_running = False
        self.last_market_data: Optional[List[MarketData]] = None
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Performance tracking
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        self.logger = logging.getLogger("trading_bot_orchestrator")
        
        # Initialize error handling and graceful degradation
        self._initialize_error_handling()
        
        # Initialize all strategies
        self._initialize_all_strategies()
    
    def _initialize_error_handling(self):
        """Initialize error handling and graceful degradation components."""
        self.logger.info("Initializing error handling and graceful degradation...")
        
        # Register components with graceful degradation manager
        graceful_degradation_manager.register_component(
            "strategy_engine",
            dependencies=set(),
            fallback_handler=self._strategy_engine_fallback,
            critical=True
        )
        
        graceful_degradation_manager.register_component(
            "signal_processor",
            dependencies={"strategy_engine"},
            fallback_handler=self._signal_processor_fallback,
            critical=False
        )
        
        graceful_degradation_manager.register_component(
            "position_manager",
            dependencies=set(),
            fallback_handler=self._position_manager_fallback,
            critical=True
        )
        
        graceful_degradation_manager.register_component(
            "risk_manager",
            dependencies=set(),
            fallback_handler=self._risk_manager_fallback,
            critical=True
        )
        
        self.logger.info("Error handling initialization complete")
    
    async def _strategy_engine_fallback(self, error: Exception):
        """Fallback handler for strategy engine failures."""
        self.logger.warning(f"Strategy engine fallback triggered: {error}")
        # Disable problematic strategies and continue with remaining ones
        await self._disable_failing_strategies()
    
    async def _signal_processor_fallback(self, error: Exception):
        """Fallback handler for signal processor failures."""
        self.logger.warning(f"Signal processor fallback triggered: {error}")
        # Switch to simplified signal processing
        self._use_simplified_signal_processing = True
    
    async def _position_manager_fallback(self, error: Exception):
        """Fallback handler for position manager failures."""
        self.logger.warning(f"Position manager fallback triggered: {error}")
        # Close all positions and halt new trades
        await self._emergency_position_closure()
    
    async def _risk_manager_fallback(self, error: Exception):
        """Fallback handler for risk manager failures."""
        self.logger.critical(f"Risk manager fallback triggered: {error}")
        # Immediately halt all trading
        await self._emergency_shutdown()
    
    def _initialize_all_strategies(self):
        """Initialize all available strategies with optimized parameters."""
        self.logger.info("Initializing all trading strategies...")
        
        # Register all strategy classes
        self.strategy_registry.register_strategy(MovingAverageStrategy)
        self.strategy_registry.register_strategy(RSIStrategy)
        self.strategy_registry.register_strategy(MultiIndicatorStrategy)
        self.strategy_registry.register_strategy(AdvancedMomentumStrategy)
        self.strategy_registry.register_strategy(MeanReversionStrategy)
        self.strategy_registry.register_strategy(ATRVolatilityStrategy)
        
        if ML_AVAILABLE:
            self.strategy_registry.register_strategy(MLPatternStrategy)
        
        # Create optimized strategy configurations for maximum coverage
        strategy_configs = [
            # Multi-Indicator for high-confidence confluence signals
            {
                'type': 'MultiIndicatorStrategy',
                'name': 'multi_indicator_primary',
                'enabled': True,
                'parameters': {
                    'min_confluence': 4,
                    'min_confidence': 0.88,
                    'volume_threshold': 1.3
                }
            },
            
            # Advanced Momentum for trend following
            {
                'type': 'AdvancedMomentumStrategy', 
                'name': 'momentum_primary',
                'enabled': True,
                'parameters': {
                    'momentum_threshold': 2.0,
                    'min_confidence': 0.86,
                    'divergence_lookback': 12
                }
            },
            
            # Mean Reversion for reversal opportunities
            {
                'type': 'MeanReversionStrategy',
                'name': 'mean_reversion_primary',
                'enabled': True,
                'parameters': {
                    'min_confluence': 4,
                    'min_confidence': 0.85,
                    'bb_std_dev': 2.3
                }
            },
            
            # ATR Volatility for breakout trading
            {
                'type': 'ATRVolatilityStrategy',
                'name': 'atr_volatility_primary',
                'enabled': True,
                'parameters': {
                    'atr_multiplier': 2.2,
                    'min_confidence': 0.84,
                    'expansion_threshold': 2.2
                }
            },
            
            # RSI for quick momentum signals
            {
                'type': 'RSIStrategy',
                'name': 'rsi_scalping',
                'enabled': True,
                'parameters': {
                    'rsi_period': 9,
                    'oversold_threshold': 25,
                    'overbought_threshold': 75,
                    'min_confidence': 0.82
                }
            },
            
            # Moving Average for trend confirmation
            {
                'type': 'MovingAverageStrategy',
                'name': 'ma_trend_filter',
                'enabled': True,
                'parameters': {
                    'short_window': 8,
                    'long_window': 21,
                    'min_confidence': 0.80
                }
            }
        ]
        
        # Add ML strategy if available
        if ML_AVAILABLE:
            strategy_configs.append({
                'type': 'MLPatternStrategy',
                'name': 'ml_pattern_primary',
                'enabled': True,
                'parameters': {
                    'prediction_threshold': 0.78,
                    'min_confidence': 0.90,
                    'retrain_frequency': 40
                }
            })
        
        # Create and add strategies to engine
        strategies = self.strategy_registry.create_strategies_from_config(strategy_configs)
        
        for strategy in strategies:
            self.strategy_engine.add_strategy(strategy)
        
        self.logger.info(f"Initialized {len(strategies)} strategies")
    
    def start_trading(self):
        """Start the trading bot orchestrator."""
        if self.is_running:
            self.logger.warning("Trading bot is already running")
            return
        
        self.logger.info("Starting Trading Bot Orchestrator...")
        
        # Start strategy engine
        self.strategy_engine.start_engine()
        started_strategies = self.strategy_engine.start_all_strategies()
        
        self.is_running = True
        self.logger.info(f"Trading bot started with {started_strategies} active strategies")
    
    def stop_trading(self):
        """Stop the trading bot orchestrator."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Trading Bot Orchestrator...")
        
        # Close all open positions
        self._close_all_positions("SYSTEM_SHUTDOWN")
        
        # Stop strategy engine
        self.strategy_engine.stop_engine()
        
        self.is_running = False
        self.logger.info("Trading bot stopped")
    
    @retry_with_backoff(max_retries=2, initial_delay=0.1)
    def process_market_data(self, market_data: List[MarketData]) -> Dict[str, Any]:
        """
        Process market data through all strategies and manage positions.
        
        Args:
            market_data: Latest market data
            
        Returns:
            Dict containing processing results and actions taken
        """
        try:
            if not self.is_running:
                return {'error': 'Trading bot not running'}
            
            # Check if critical components are available
            if not graceful_degradation_manager.can_execute_operation(['strategy_engine', 'risk_manager']):
                self.logger.warning("Critical components unavailable, skipping market data processing")
                return {'error': 'Critical components unavailable'}
            
            self.last_market_data = market_data
            current_price = float(market_data[-1].close)
            
            # Reset daily P&L if new day
            self._check_daily_reset()
            
            # Update existing positions with error handling
            try:
                self._update_positions(market_data[-1])
            except Exception as e:
                self.logger.error(f"Error updating positions: {e}")
                # Note: graceful_degradation_manager would need to be available in this context
            
            # Check exit conditions for all positions
            exit_actions = []
            try:
                exit_actions = self._check_exit_conditions(market_data[-1])
            except Exception as e:
                self.logger.error(f"Error checking exit conditions: {e}")
                # Note: graceful_degradation_manager would need to be available in this context
            
            # Get new signals from all strategies with error handling
            signals = []
            try:
                if graceful_degradation_manager.is_component_available("strategy_engine"):
                    signals = self.strategy_engine.process_market_data(market_data)
            except Exception as e:
                self.logger.error(f"Error processing signals: {e}")
                # Note: graceful_degradation_manager would need to be available in this context
                raise StrategyException(f"Strategy engine failed: {e}", original_exception=e)
            
            # Process new entry signals
            entry_actions = []
            try:
                if graceful_degradation_manager.is_component_available("signal_processor"):
                    entry_actions = self._process_entry_signals(signals, market_data[-1])
            except Exception as e:
                self.logger.error(f"Error processing entry signals: {e}")
                # Note: graceful_degradation_manager would need to be available in this context
            
            # Risk management checks
            risk_actions = []
            try:
                if graceful_degradation_manager.is_component_available("risk_manager"):
                    risk_actions = self._perform_risk_checks(market_data[-1])
            except Exception as e:
                self.logger.error(f"Error performing risk checks: {e}")
                # Note: graceful_degradation_manager would need to be available in this context
                raise RiskException(f"Risk management failed: {e}", original_exception=e)
            
            return {
                'timestamp': market_data[-1].timestamp,
                'current_price': current_price,
                'signals_received': len(signals),
                'entry_actions': entry_actions,
                'exit_actions': exit_actions,
                'risk_actions': risk_actions,
                'open_positions': len(self.positions),
                'daily_pnl': float(self.daily_pnl),
                'total_pnl': float(self.total_pnl),
                'portfolio_value': float(self.current_capital),
                'service_level': graceful_degradation_manager.service_level.value
            }
            
        except Exception as e:
            self.logger.error(f"Critical error in market data processing: {e}")
            raise TradingBotException(f"Market data processing failed: {e}", original_exception=e)
    
    def _process_entry_signals(self, signals: List, market_data: MarketData) -> List[Dict[str, Any]]:
        """Process entry signals with aggressive filtering."""
        entry_actions = []
        
        if not signals:
            return entry_actions
        
        # Sort signals by confidence (highest first)
        sorted_signals = sorted(signals, key=lambda s: s.original_signal.confidence, reverse=True)
        
        for processed_signal in sorted_signals:
            signal = processed_signal.original_signal
            
            # Check if we can enter new position
            if not self._can_enter_position(signal, market_data):
                continue
            
            # Calculate position size
            position_size = self._calculate_position_size(signal, market_data)
            
            if position_size <= 0:
                continue
            
            # Create position
            position = self._create_position(signal, market_data, position_size)
            
            if position:
                self.positions[f"{signal.symbol}_{signal.strategy_name}"] = position
                entry_actions.append({
                    'action': 'ENTER_POSITION',
                    'symbol': signal.symbol,
                    'side': signal.action.value,
                    'size': float(position_size),
                    'price': float(signal.price),
                    'strategy': signal.strategy_name,
                    'confidence': signal.confidence,
                    'stop_loss': float(position.stop_loss) if position.stop_loss else None,
                    'take_profit': float(position.take_profit) if position.take_profit else None
                })
                
                self.logger.info(f"Entered position: {signal.action.value} {signal.symbol} "
                               f"@ ${float(signal.price):.2f} (Strategy: {signal.strategy_name}, "
                               f"Confidence: {signal.confidence:.3f})")
        
        return entry_actions
    
    def _can_enter_position(self, signal: TradingSignal, market_data: MarketData) -> bool:
        """Check if we can enter a new position."""
        # Check maximum positions
        if len(self.positions) >= self.risk_limits.max_positions:
            return False
        
        # Check daily loss limit
        if float(self.daily_pnl) <= -self.risk_limits.max_daily_loss * float(self.initial_capital):
            return False
        
        # Check if we already have a position for this symbol
        existing_positions = [p for p in self.positions.values() if p.symbol == signal.symbol]
        if existing_positions:
            return False
        
        # Check minimum confidence
        if signal.confidence < 0.80:  # Minimum 80% confidence
            return False
        
        return True
    
    def _calculate_position_size(self, signal: TradingSignal, market_data: MarketData) -> Decimal:
        """Calculate position size based on confidence and risk management."""
        base_risk = self.risk_limits.max_portfolio_risk
        
        # Adjust risk based on confidence
        confidence_multiplier = min(signal.confidence / 0.85, 1.2)  # Max 1.2x for high confidence
        
        # Calculate risk amount
        risk_amount = float(self.current_capital) * base_risk * confidence_multiplier
        
        # Calculate position size based on stop loss
        current_price = float(signal.price)
        
        # Estimate stop loss (2% for high confidence signals)
        stop_loss_pct = 0.02 if signal.confidence >= 0.90 else 0.025
        
        if signal.action == SignalAction.BUY:
            stop_price = current_price * (1 - stop_loss_pct)
        else:
            stop_price = current_price * (1 + stop_loss_pct)
        
        risk_per_share = abs(current_price - stop_price)
        
        if risk_per_share <= 0:
            return Decimal('0')
        
        position_size = risk_amount / risk_per_share
        
        # Apply maximum position size limit
        max_position_value = float(self.current_capital) * self.risk_limits.max_position_size
        max_shares = max_position_value / current_price
        
        position_size = min(position_size, max_shares)
        
        return Decimal(str(max(position_size, 0)))
    
    def _create_position(self, signal: TradingSignal, market_data: MarketData, 
                        position_size: Decimal) -> Optional[TradingPosition]:
        """Create a new trading position with exit levels."""
        try:
            current_price = signal.price
            
            # Calculate stop loss and take profit
            if signal.confidence >= 0.90:
                stop_loss_pct = 0.015  # 1.5% for very high confidence
                take_profit_pct = 0.04  # 4% target (2.67:1 R/R)
            elif signal.confidence >= 0.85:
                stop_loss_pct = 0.02   # 2% for high confidence
                take_profit_pct = 0.05  # 5% target (2.5:1 R/R)
            else:
                stop_loss_pct = 0.025  # 2.5% for moderate confidence
                take_profit_pct = 0.06  # 6% target (2.4:1 R/R)
            
            if signal.action == SignalAction.BUY:
                stop_loss = current_price * Decimal(str(1 - stop_loss_pct))
                take_profit = current_price * Decimal(str(1 + take_profit_pct))
            else:
                stop_loss = current_price * Decimal(str(1 + stop_loss_pct))
                take_profit = current_price * Decimal(str(1 - take_profit_pct))
            
            position = TradingPosition(
                symbol=signal.symbol,
                side=signal.action.value,
                entry_price=current_price,
                quantity=position_size,
                entry_time=signal.timestamp,
                strategy_name=signal.strategy_name,
                confidence=signal.confidence,
                stop_loss=stop_loss,
                take_profit=take_profit,
                max_hold_time=timedelta(hours=12 if signal.confidence >= 0.90 else 24)
            )
            
            return position
            
        except Exception as e:
            self.logger.error(f"Error creating position: {str(e)}")
            return None
    
    def _update_positions(self, market_data: MarketData):
        """Update all open positions with current market data."""
        current_price = market_data.close
        
        for position in self.positions.values():
            if position.symbol == market_data.symbol:
                position.update_profit_tracking(current_price)
    
    def _check_exit_conditions(self, market_data: MarketData) -> List[Dict[str, Any]]:
        """Check exit conditions for all positions - AGGRESSIVE EXIT STRATEGY."""
        exit_actions = []
        positions_to_close = []
        
        current_price = market_data.close
        current_time = market_data.timestamp
        
        for position_key, position in self.positions.items():
            if position.symbol != market_data.symbol:
                continue
            
            exit_reason = None
            
            # 1. STOP LOSS - Immediate exit
            if position.stop_loss:
                if ((position.side == 'BUY' and current_price <= position.stop_loss) or
                    (position.side == 'SELL' and current_price >= position.stop_loss)):
                    exit_reason = ExitReason.STOP_LOSS
            
            # 2. TAKE PROFIT - Immediate exit
            if not exit_reason and position.take_profit:
                if ((position.side == 'BUY' and current_price >= position.take_profit) or
                    (position.side == 'SELL' and current_price <= position.take_profit)):
                    exit_reason = ExitReason.TAKE_PROFIT
            
            # 3. TRAILING STOP - Protect profits aggressively
            if not exit_reason and position.trailing_stop:
                if ((position.side == 'BUY' and current_price <= position.trailing_stop) or
                    (position.side == 'SELL' and current_price >= position.trailing_stop)):
                    exit_reason = ExitReason.TRAILING_STOP
            
            # 4. PROFIT PROTECTION - Exit if profit drops from peak
            if not exit_reason and float(position.max_profit) > position.profit_protection_threshold:
                current_profit = self._calculate_current_profit(position, current_price)
                profit_drawdown = float(position.max_profit) - current_profit
                
                # Exit if profit drops by 50% from peak (aggressive profit protection)
                if profit_drawdown > float(position.max_profit) * 0.5:
                    exit_reason = ExitReason.PROFIT_PROTECTION
            
            # 5. TIME EXIT - Don't hold positions too long
            if not exit_reason:
                hold_time = current_time - position.entry_time
                if hold_time > position.max_hold_time:
                    exit_reason = ExitReason.TIME_EXIT
            
            # 6. RISK MANAGEMENT - Emergency exit for large losses
            if not exit_reason:
                current_profit = self._calculate_current_profit(position, current_price)
                if current_profit < -0.04:  # 4% loss emergency exit
                    exit_reason = ExitReason.RISK_MANAGEMENT
            
            # Execute exit if reason found
            if exit_reason:
                positions_to_close.append((position_key, position, exit_reason))
        
        # Close positions
        for position_key, position, exit_reason in positions_to_close:
            pnl = self._close_position(position_key, current_price, exit_reason)
            
            exit_actions.append({
                'action': 'EXIT_POSITION',
                'symbol': position.symbol,
                'side': position.side,
                'size': float(position.quantity),
                'entry_price': float(position.entry_price),
                'exit_price': float(current_price),
                'pnl': float(pnl),
                'reason': exit_reason.value,
                'hold_time': str(market_data.timestamp - position.entry_time),
                'strategy': position.strategy_name
            })
        
        return exit_actions
    
    def _calculate_current_profit(self, position: TradingPosition, current_price: Decimal) -> float:
        """Calculate current profit percentage for a position."""
        if position.side == 'BUY':
            return float((current_price - position.entry_price) / position.entry_price)
        else:
            return float((position.entry_price - current_price) / position.entry_price)
    
    def _close_position(self, position_key: str, exit_price: Decimal, 
                       exit_reason: ExitReason) -> Decimal:
        """Close a position and update P&L."""
        position = self.positions[position_key]
        
        # Calculate P&L
        if position.side == 'BUY':
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        
        # Update capital and P&L tracking
        self.current_capital += pnl
        self.daily_pnl += pnl
        self.total_pnl += pnl
        
        # Update trade statistics
        self.trade_count += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Move to closed positions
        position.status = PositionStatus.CLOSED
        self.closed_positions.append(position)
        
        # Remove from active positions
        del self.positions[position_key]
        
        self.logger.info(f"Closed position: {position.side} {position.symbol} "
                        f"@ ${float(exit_price):.2f} | P&L: ${float(pnl):.2f} "
                        f"| Reason: {exit_reason.value}")
        
        return pnl
    
    def _close_all_positions(self, reason: str):
        """Close all open positions."""
        if not self.last_market_data:
            return
        
        current_price = self.last_market_data[-1].close
        positions_to_close = list(self.positions.keys())
        
        for position_key in positions_to_close:
            self._close_position(position_key, current_price, ExitReason.RISK_MANAGEMENT)
        
        self.logger.info(f"Closed all positions due to: {reason}")
    
    def _perform_risk_checks(self, market_data: MarketData) -> List[Dict[str, Any]]:
        """Perform comprehensive risk management checks."""
        risk_actions = []
        
        # Check daily loss limit
        daily_loss_pct = float(self.daily_pnl) / float(self.initial_capital)
        if daily_loss_pct <= -self.risk_limits.max_daily_loss:
            self._close_all_positions("DAILY_LOSS_LIMIT")
            risk_actions.append({
                'action': 'DAILY_LOSS_LIMIT_TRIGGERED',
                'daily_pnl': float(self.daily_pnl),
                'limit': self.risk_limits.max_daily_loss
            })
        
        # Check portfolio heat (total risk exposure)
        total_risk = sum(
            float(pos.quantity) * float(pos.entry_price) * 0.02  # Assume 2% risk per position
            for pos in self.positions.values()
        )
        
        portfolio_risk_pct = total_risk / float(self.current_capital)
        if portfolio_risk_pct > 0.10:  # 10% max portfolio risk
            # Close lowest confidence positions first
            sorted_positions = sorted(
                self.positions.items(), 
                key=lambda x: x[1].confidence
            )
            
            positions_to_close = sorted_positions[:len(sorted_positions)//2]
            for pos_key, _ in positions_to_close:
                self._close_position(pos_key, market_data.close, ExitReason.RISK_MANAGEMENT)
            
            risk_actions.append({
                'action': 'PORTFOLIO_RISK_REDUCTION',
                'positions_closed': len(positions_to_close),
                'risk_percentage': portfolio_risk_pct
            })
        
        return risk_actions
    
    def _check_daily_reset(self):
        """Check if we need to reset daily P&L."""
        current_date = datetime.now().date()
        reset_date = self.daily_reset_time.date()
        
        if current_date > reset_date:
            self.daily_pnl = Decimal('0')
            self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        win_rate = self.winning_trades / self.trade_count if self.trade_count > 0 else 0
        
        # Calculate average win/loss
        winning_pnl = sum(
            self._calculate_position_pnl(pos) for pos in self.closed_positions
            if self._calculate_position_pnl(pos) > 0
        )
        losing_pnl = sum(
            self._calculate_position_pnl(pos) for pos in self.closed_positions
            if self._calculate_position_pnl(pos) < 0
        )
        
        avg_win = winning_pnl / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = losing_pnl / self.losing_trades if self.losing_trades > 0 else 0
        
        profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float('inf')
        
        return {
            'total_trades': self.trade_count,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'average_win': float(avg_win),
            'average_loss': float(avg_loss),
            'total_pnl': float(self.total_pnl),
            'daily_pnl': float(self.daily_pnl),
            'current_capital': float(self.current_capital),
            'return_percentage': float(self.total_pnl) / float(self.initial_capital) * 100,
            'open_positions': len(self.positions),
            'strategy_performance': self._get_strategy_performance()
        }
    
    def _calculate_position_pnl(self, position: TradingPosition) -> Decimal:
        """Calculate P&L for a closed position."""
        # This would need the exit price, which should be stored in the position
        # For now, return 0 as placeholder
        return Decimal('0')
    
    def _get_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance breakdown by strategy."""
        strategy_stats = {}
        
        for position in self.closed_positions:
            strategy = position.strategy_name
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'trades': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_pnl': 0.0
                }
            
            strategy_stats[strategy]['trades'] += 1
            pnl = float(self._calculate_position_pnl(position))
            strategy_stats[strategy]['total_pnl'] += pnl
            
            if pnl > 0:
                strategy_stats[strategy]['wins'] += 1
            else:
                strategy_stats[strategy]['losses'] += 1
        
        # Calculate win rates
        for stats in strategy_stats.values():
            stats['win_rate'] = stats['wins'] / stats['trades'] if stats['trades'] > 0 else 0
        
        return strategy_stats    
    
    # Error handling and recovery methods
    
    async def _disable_failing_strategies(self):
        """Disable strategies that are consistently failing."""
        self.logger.warning("Disabling failing strategies...")
        
        # Get strategy performance and disable poor performers
        strategy_performance = self._get_strategy_performance()
        
        for strategy_name, stats in strategy_performance.items():
            if stats['trades'] >= 5 and stats['win_rate'] < 0.3:
                self.logger.warning(f"Disabling strategy {strategy_name} due to poor performance")
                # Disable strategy in the engine
                if hasattr(self.strategy_engine, 'disable_strategy'):
                    self.strategy_engine.disable_strategy(strategy_name)
    
    async def _emergency_position_closure(self):
        """Emergency closure of all positions."""
        self.logger.critical("Emergency position closure initiated")
        
        try:
            for position_id, position in self.positions.items():
                if position.status == PositionStatus.OPEN:
                    self.logger.warning(f"Emergency closing position {position_id}")
                    position.status = PositionStatus.CLOSING
                    position.exit_reason = ExitReason.RISK_MANAGEMENT
                    position.exit_timestamp = datetime.now()
                    
                    # In a real implementation, this would place market orders
                    # to close positions immediately
                    
            # Clear all positions
            self.closed_positions.extend(self.positions.values())
            self.positions.clear()
            
        except Exception as e:
            self.logger.error(f"Error during emergency position closure: {e}")
    
    async def _emergency_shutdown(self):
        """Emergency shutdown of the trading bot."""
        self.logger.critical("Emergency shutdown initiated")
        
        try:
            # Close all positions first
            await self._emergency_position_closure()
            
            # Stop the trading bot
            self.is_running = False
            
            # Update service level to emergency
            await graceful_degradation_manager.update_component_status(
                "risk_manager",
                ComponentStatus.FAILED,
                "Emergency shutdown triggered"
            )
            
        except Exception as e:
            self.logger.error(f"Error during emergency shutdown: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health information."""
        return {
            'orchestrator_status': 'running' if self.is_running else 'stopped',
            'positions_count': len(self.positions),
            'daily_pnl': float(self.daily_pnl),
            'service_level': graceful_degradation_manager.service_level.value,
            'component_health': graceful_degradation_manager.get_system_health(),
            'last_update': datetime.now().isoformat()
        }