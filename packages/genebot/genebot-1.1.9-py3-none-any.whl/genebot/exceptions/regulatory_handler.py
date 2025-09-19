"""
Regulatory violation detection and handling system.

This module provides functionality for detecting regulatory violations,
handling compliance issues, and implementing corrective actions across
different market types and jurisdictions.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from .multi_market_exceptions import (
    MarketType,
    RegulatoryViolationException,
    NonRecoverableException
)


class ViolationType(Enum):
    """Types of regulatory violations."""
    POSITION_LIMIT_EXCEEDED = "position_limit_exceeded"
    LEVERAGE_LIMIT_EXCEEDED = "leverage_limit_exceeded"
    TRADING_HOURS_VIOLATION = "trading_hours_violation"
    WASH_TRADING = "wash_trading"
    MARKET_MANIPULATION = "market_manipulation"
    INSIDER_TRADING = "insider_trading"
    INSUFFICIENT_MARGIN = "insufficient_margin"
    UNAUTHORIZED_TRADING = "unauthorized_trading"
    REPORTING_VIOLATION = "reporting_violation"
    KYC_VIOLATION = "kyc_violation"
    AML_VIOLATION = "aml_violation"
    FIDUCIARY_BREACH = "fiduciary_breach"
    DISCLOSURE_VIOLATION = "disclosure_violation"


class Severity(Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of corrective actions."""
    WARNING = "warning"
    POSITION_REDUCTION = "position_reduction"
    TRADING_HALT = "trading_halt"
    ACCOUNT_SUSPENSION = "account_suspension"
    FORCED_LIQUIDATION = "forced_liquidation"
    REPORTING_REQUIRED = "reporting_required"
    MANUAL_REVIEW = "manual_review"
    SYSTEM_SHUTDOWN = "system_shutdown"


@dataclass
class RegulatoryRule:
    """Represents a regulatory rule."""
    id: str
    name: str
    description: str
    market_type: MarketType
    jurisdiction: str
    violation_type: ViolationType
    severity: Severity
    threshold_value: Optional[float] = None
    time_window: Optional[timedelta] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ViolationEvent:
    """Represents a regulatory violation event."""
    id: str
    rule_id: str
    violation_type: ViolationType
    severity: Severity
    market_type: MarketType
    jurisdiction: str
    description: str
    detected_at: datetime
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    affected_symbols: List[str] = field(default_factory=list)
    affected_accounts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class CorrectiveAction:
    """Represents a corrective action to be taken."""
    id: str
    violation_id: str
    action_type: ActionType
    description: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


class RegulatoryMonitor:
    """Monitors for regulatory violations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[str, RegulatoryRule] = {}
        self.violations: Dict[str, ViolationEvent] = {}
        self.violation_callbacks: Dict[ViolationType, List[Callable]] = {}
        self.position_limits: Dict[str, Dict[str, float]] = {}
        self.trading_history: List[Dict[str, Any]] = []
        self.account_info: Dict[str, Dict[str, Any]] = {}
    
    def register_rule(self, rule: RegulatoryRule) -> None:
        """Register a regulatory rule."""
        self.rules[rule.id] = rule
        self.logger.info(f"Registered regulatory rule: {rule.name} ({rule.id})")
    
    def register_violation_callback(
        self,
        violation_type: ViolationType,
        callback: Callable
    ) -> None:
        """Register callback for specific violation types."""
        callbacks = self.violation_callbacks.setdefault(violation_type, [])
        callbacks.append(callback)
    
    def set_position_limits(
        self,
        market_type: MarketType,
        limits: Dict[str, float]
    ) -> None:
        """Set position limits for a market type."""
        key = market_type.value
        self.position_limits[key] = limits
        self.logger.info(f"Set position limits for {key}: {limits}")
    
    def update_account_info(
        self,
        account_id: str,
        info: Dict[str, Any]
    ) -> None:
        """Update account information."""
        self.account_info[account_id] = info
    
    def record_trade(
        self,
        trade_data: Dict[str, Any]
    ) -> None:
        """Record a trade for monitoring."""
        trade_data['timestamp'] = datetime.now(timezone.utc)
        self.trading_history.append(trade_data)
        
        # Keep only last 10000 trades
        if len(self.trading_history) > 10000:
            self.trading_history.pop(0)
        
        # Check for violations
        self._check_trade_violations(trade_data)
    
    def check_position_limits(
        self,
        market_type: MarketType,
        symbol: str,
        current_position: float,
        proposed_change: float
    ) -> Optional[ViolationEvent]:
        """Check if position change would violate limits."""
        limits = self.position_limits.get(market_type.value, {})
        
        if symbol not in limits:
            return None
        
        limit = limits[symbol]
        new_position = abs(current_position + proposed_change)
        
        if new_position > limit:
            violation = self._create_violation(
                rule_id="position_limit",
                violation_type=ViolationType.POSITION_LIMIT_EXCEEDED,
                severity=Severity.HIGH,
                market_type=market_type,
                description=f"Position limit exceeded for {symbol}",
                current_value=new_position,
                threshold_value=limit,
                affected_symbols=[symbol]
            )
            return violation
        
        return None
    
    def check_leverage_limits(
        self,
        market_type: MarketType,
        account_id: str,
        current_leverage: float,
        max_leverage: float
    ) -> Optional[ViolationEvent]:
        """Check if leverage exceeds limits."""
        if current_leverage > max_leverage:
            violation = self._create_violation(
                rule_id="leverage_limit",
                violation_type=ViolationType.LEVERAGE_LIMIT_EXCEEDED,
                severity=Severity.HIGH,
                market_type=market_type,
                description=f"Leverage limit exceeded for account {account_id}",
                current_value=current_leverage,
                threshold_value=max_leverage,
                affected_accounts=[account_id]
            )
            return violation
        
        return None
    
    def check_wash_trading(
        self,
        symbol: str,
        time_window: timedelta = timedelta(minutes=5)
    ) -> Optional[ViolationEvent]:
        """Check for wash trading patterns."""
        cutoff_time = datetime.now(timezone.utc) - time_window
        recent_trades = [
            t for t in self.trading_history
            if t.get('symbol') == symbol and t.get('timestamp', datetime.min) >= cutoff_time
        ]
        
        if len(recent_trades) < 4:
            return None
        
        # Simple wash trading detection: alternating buy/sell with similar prices
        buy_trades = [t for t in recent_trades if t.get('side') == 'buy']
        sell_trades = [t for t in recent_trades if t.get('side') == 'sell']
        
        if len(buy_trades) >= 2 and len(sell_trades) >= 2:
            # Check if trades are alternating and prices are similar
            if self._detect_wash_pattern(buy_trades, sell_trades):
                violation = self._create_violation(
                    rule_id="wash_trading",
                    violation_type=ViolationType.WASH_TRADING,
                    severity=Severity.CRITICAL,
                    market_type=MarketType.CRYPTO,  # Default, should be determined from trades
                    description=f"Potential wash trading detected for {symbol}",
                    affected_symbols=[symbol]
                )
                return violation
        
        return None
    
    def check_trading_hours(
        self,
        market_type: MarketType,
        trade_time: datetime
    ) -> Optional[ViolationEvent]:
        """Check if trading is allowed at the given time."""
        if market_type == MarketType.CRYPTO:
            return None  # Crypto markets are always open
        
        # This would check against market session rules
        # Simplified implementation
        if market_type == MarketType.FOREX:
            # Check if it's weekend (simplified)
            if trade_time.weekday() >= 5:  # Saturday or Sunday
                violation = self._create_violation(
                    rule_id="trading_hours",
                    violation_type=ViolationType.TRADING_HOURS_VIOLATION,
                    severity=Severity.MEDIUM,
                    market_type=market_type,
                    description=f"Trading attempted outside market hours"
                )
                return violation
        
        return None
    
    def _check_trade_violations(self, trade_data: Dict[str, Any]) -> None:
        """Check a trade for various violations."""
        symbol = trade_data.get('symbol')
        if not symbol:
            return
        
        # Check wash trading
        wash_violation = self.check_wash_trading(symbol)
        if wash_violation:
            self._handle_violation(wash_violation)
        
        # Check trading hours
        trade_time = trade_data.get('timestamp', datetime.now(timezone.utc))
        market_type = MarketType(trade_data.get('market_type', 'crypto'))
        hours_violation = self.check_trading_hours(market_type, trade_time)
        if hours_violation:
            self._handle_violation(hours_violation)
    
    def _detect_wash_pattern(
        self,
        buy_trades: List[Dict[str, Any]],
        sell_trades: List[Dict[str, Any]]
    ) -> bool:
        """Detect wash trading patterns."""
        # Simplified wash trading detection
        # In reality, this would be much more sophisticated
        
        if len(buy_trades) < 2 or len(sell_trades) < 2:
            return False
        
        # Check if prices are very similar (within 1%)
        buy_prices = [t.get('price', 0) for t in buy_trades]
        sell_prices = [t.get('price', 0) for t in sell_trades]
        
        avg_buy_price = sum(buy_prices) / len(buy_prices)
        avg_sell_price = sum(sell_prices) / len(sell_prices)
        
        if avg_buy_price == 0 or avg_sell_price == 0:
            return False
        
        price_diff = abs(avg_buy_price - avg_sell_price) / avg_buy_price
        
        return price_diff < 0.01  # Less than 1% difference
    
    def _create_violation(
        self,
        rule_id: str,
        violation_type: ViolationType,
        severity: Severity,
        market_type: MarketType,
        description: str,
        current_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        affected_symbols: Optional[List[str]] = None,
        affected_accounts: Optional[List[str]] = None
    ) -> ViolationEvent:
        """Create a violation event."""
        violation_id = f"{rule_id}_{datetime.now().timestamp()}"
        
        violation = ViolationEvent(
            id=violation_id,
            rule_id=rule_id,
            violation_type=violation_type,
            severity=severity,
            market_type=market_type,
            jurisdiction="US",  # Default, should be configurable
            description=description,
            detected_at=datetime.now(timezone.utc),
            current_value=current_value,
            threshold_value=threshold_value,
            affected_symbols=affected_symbols or [],
            affected_accounts=affected_accounts or []
        )
        
        self.violations[violation_id] = violation
        return violation
    
    def _handle_violation(self, violation: ViolationEvent) -> None:
        """Handle a detected violation."""
        self.logger.warning(
            f"Regulatory violation detected: {violation.violation_type.value} "
            f"({violation.severity.value}) - {violation.description}"
        )
        
        # Call registered callbacks
        callbacks = self.violation_callbacks.get(violation.violation_type, [])
        for callback in callbacks:
            try:
                callback(violation)
            except Exception as e:
                self.logger.error(f"Violation callback error: {e}")
    
    def get_violations(
        self,
        market_type: Optional[MarketType] = None,
        severity: Optional[Severity] = None,
        resolved: Optional[bool] = None
    ) -> List[ViolationEvent]:
        """Get violations matching criteria."""
        violations = list(self.violations.values())
        
        if market_type:
            violations = [v for v in violations if v.market_type == market_type]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        if resolved is not None:
            violations = [v for v in violations if v.resolved == resolved]
        
        return violations
    
    def resolve_violation(
        self,
        violation_id: str,
        resolution_notes: str
    ) -> bool:
        """Mark a violation as resolved."""
        if violation_id in self.violations:
            violation = self.violations[violation_id]
            violation.resolved = True
            violation.resolved_at = datetime.now(timezone.utc)
            violation.resolution_notes = resolution_notes
            
            self.logger.info(f"Resolved violation {violation_id}: {resolution_notes}")
            return True
        
        return False


class RegulatoryActionHandler:
    """Handles corrective actions for regulatory violations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.actions: Dict[str, CorrectiveAction] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}
    
    def register_action_handler(
        self,
        action_type: ActionType,
        handler: Callable
    ) -> None:
        """Register handler for specific action types."""
        self.action_handlers[action_type] = handler
    
    async def create_corrective_action(
        self,
        violation: ViolationEvent,
        action_type: ActionType,
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> CorrectiveAction:
        """Create and execute a corrective action."""
        action_id = f"{violation.id}_{action_type.value}_{datetime.now().timestamp()}"
        
        action = CorrectiveAction(
            id=action_id,
            violation_id=violation.id,
            action_type=action_type,
            description=description,
            created_at=datetime.now(timezone.utc),
            parameters=parameters or {}
        )
        
        self.actions[action_id] = action
        
        # Execute the action
        await self._execute_action(action)
        
        return action
    
    async def _execute_action(self, action: CorrectiveAction) -> None:
        """Execute a corrective action."""
        handler = self.action_handlers.get(action.action_type)
        
        if not handler:
            self.logger.error(f"No handler registered for action type {action.action_type.value}")
            action.error_message = f"No handler for {action.action_type.value}"
            return
        
        try:
            self.logger.info(f"Executing corrective action: {action.description}")
            
            await handler(action)
            
            action.executed_at = datetime.now(timezone.utc)
            action.success = True
            
            self.logger.info(f"Successfully executed action {action.id}")
            
        except Exception as e:
            action.error_message = str(e)
            self.logger.error(f"Failed to execute action {action.id}: {e}")
    
    def get_actions(
        self,
        violation_id: Optional[str] = None,
        action_type: Optional[ActionType] = None
    ) -> List[CorrectiveAction]:
        """Get actions matching criteria."""
        actions = list(self.actions.values())
        
        if violation_id:
            actions = [a for a in actions if a.violation_id == violation_id]
        
        if action_type:
            actions = [a for a in actions if a.action_type == action_type]
        
        return actions


class RegulatoryComplianceManager:
    """Main regulatory compliance manager."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitor = RegulatoryMonitor()
        self.action_handler = RegulatoryActionHandler()
        self._setup_default_handlers()
    
    def _setup_default_handlers(self) -> None:
        """Setup default violation and action handlers."""
        # Register violation callbacks
        self.monitor.register_violation_callback(
            ViolationType.POSITION_LIMIT_EXCEEDED,
            self._handle_position_limit_violation
        )
        
        self.monitor.register_violation_callback(
            ViolationType.LEVERAGE_LIMIT_EXCEEDED,
            self._handle_leverage_violation
        )
        
        self.monitor.register_violation_callback(
            ViolationType.WASH_TRADING,
            self._handle_wash_trading_violation
        )
        
        # Register action handlers
        self.action_handler.register_action_handler(
            ActionType.TRADING_HALT,
            self._handle_trading_halt
        )
        
        self.action_handler.register_action_handler(
            ActionType.POSITION_REDUCTION,
            self._handle_position_reduction
        )
    
    async def _handle_position_limit_violation(self, violation: ViolationEvent) -> None:
        """Handle position limit violations."""
        await self.action_handler.create_corrective_action(
            violation,
            ActionType.POSITION_REDUCTION,
            f"Reduce position for {violation.affected_symbols}",
            {"symbols": violation.affected_symbols}
        )
    
    async def _handle_leverage_violation(self, violation: ViolationEvent) -> None:
        """Handle leverage violations."""
        await self.action_handler.create_corrective_action(
            violation,
            ActionType.TRADING_HALT,
            f"Halt trading for accounts {violation.affected_accounts}",
            {"accounts": violation.affected_accounts}
        )
    
    async def _handle_wash_trading_violation(self, violation: ViolationEvent) -> None:
        """Handle wash trading violations."""
        await self.action_handler.create_corrective_action(
            violation,
            ActionType.MANUAL_REVIEW,
            f"Manual review required for wash trading on {violation.affected_symbols}",
            {"symbols": violation.affected_symbols}
        )
    
    async def _handle_trading_halt(self, action: CorrectiveAction) -> None:
        """Handle trading halt action."""
        # Implementation would halt trading for specified accounts/symbols
        self.logger.warning(f"Trading halt executed: {action.description}")
    
    async def _handle_position_reduction(self, action: CorrectiveAction) -> None:
        """Handle position reduction action."""
        # Implementation would reduce positions for specified symbols
        self.logger.warning(f"Position reduction executed: {action.description}")
    
    def get_monitor(self) -> RegulatoryMonitor:
        """Get the regulatory monitor."""
        return self.monitor
    
    def get_action_handler(self) -> RegulatoryActionHandler:
        """Get the action handler."""
        return self.action_handler