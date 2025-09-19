"""
Unit tests for risk management components.

Tests for RiskManager, PositionSizer, StopLossManager, and DrawdownMonitor.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from src.risk.risk_manager import RiskManager, RiskConfig, RiskLevel, RiskAssessment
from src.risk.position_sizer import PositionSizer, SizingMethod
from src.risk.stop_loss_manager import StopLossManager, StopLossConfig, StopLossType
from src.risk.drawdown_monitor import DrawdownMonitor, DrawdownConfig, DrawdownSeverity
from src.models.data_models import (
    MarketData, TradingSignal, Position, Order, 
    SignalAction, OrderSide, OrderType, OrderStatus
)


class TestRiskManager:
    """Test cases for RiskManager."""
    
    @pytest.fixture
    def risk_config(self):
        """Create test risk configuration."""
        return RiskConfig(
            max_portfolio_risk_pct=0.02,
            max_daily_loss_pct=0.05,
            max_drawdown_pct=0.10,
            max_position_size_pct=0.20,
            max_positions=10,
            default_stop_loss_pct=0.02
        )
    
    @pytest.fixture
    def risk_manager(self, risk_config):
        """Create test risk manager."""
        return RiskManager(risk_config)
    
    @pytest.fixture
    def sample_signal(self):
        """Create sample trading signal."""
        return TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.85,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000")
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("49500"),
            high=Decimal("50500"),
            low=Decimal("49000"),
            close=Decimal("50000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
    
    @pytest.fixture
    def sample_position(self):
        """Create sample position."""
        return Position(
            symbol="BTCUSDT",
            size=Decimal("0.1"),
            entry_price=Decimal("49000"),
            current_price=Decimal("50000"),
            timestamp=datetime.now(),
            exchange="binance",
            side=OrderSide.BUY
        )
    
    def test_risk_manager_initialization(self, risk_manager):
        """Test risk manager initialization."""
        assert risk_manager.config is not None
        assert risk_manager.position_sizer is not None
        assert risk_manager.stop_loss_manager is not None
        assert risk_manager.drawdown_monitor is not None
        assert risk_manager.daily_pnl == Decimal("0")
        assert risk_manager.daily_trades == 0
        assert not risk_manager.trading_halted
    
    def test_assess_trade_risk_low_risk(self, risk_manager, sample_signal, sample_market_data):
        """Test trade risk assessment for low risk scenario."""
        portfolio_value = Decimal("100000")
        current_positions = []
        
        assessment = risk_manager.assess_trade_risk(
            sample_signal, sample_market_data, portfolio_value, current_positions
        )
        
        assert isinstance(assessment, RiskAssessment)
        assert assessment.level in [RiskLevel.LOW, RiskLevel.MEDIUM]
        assert 0.0 <= assessment.score <= 1.0
        assert assessment.max_position_size is not None
        assert not assessment.should_halt_trading
    
    def test_assess_trade_risk_high_risk(self, risk_manager, sample_signal, sample_market_data):
        """Test trade risk assessment for high risk scenario."""
        portfolio_value = Decimal("10000")  # Small portfolio
        
        # Create many existing positions to increase concentration risk
        current_positions = []
        for i in range(8):
            position = Position(
                symbol=f"SYMBOL{i}",
                size=Decimal("10"),  # Larger positions
                entry_price=Decimal("100"),
                current_price=Decimal("80"),  # 20% loss each
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            )
            current_positions.append(position)
        
        assessment = risk_manager.assess_trade_risk(
            sample_signal, sample_market_data, portfolio_value, current_positions
        )
        
        # Should be at least medium risk due to high losses and concentration
        assert assessment.level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.max_position_size is not None
    
    def test_validate_order_success(self, risk_manager, sample_position):
        """Test successful order validation."""
        order = Order(
            id="test_order_1",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            price=Decimal("50000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
        
        portfolio_value = Decimal("100000")
        current_positions = [sample_position]
        
        is_valid, reason = risk_manager.validate_order(order, portfolio_value, current_positions)
        
        assert is_valid
        assert "validation passed" in reason.lower()
    
    def test_validate_order_position_size_limit(self, risk_manager):
        """Test order validation with position size limit exceeded."""
        order = Order(
            id="test_order_1",
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            amount=Decimal("30"),  # Large amount
            price=Decimal("50000"),
            order_type=OrderType.LIMIT,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
        
        portfolio_value = Decimal("100000")
        current_positions = []
        
        is_valid, reason = risk_manager.validate_order(order, portfolio_value, current_positions)
        
        assert not is_valid
        assert "exceeds limit" in reason.lower()
    
    def test_halt_and_resume_trading(self, risk_manager):
        """Test trading halt and resume functionality."""
        # Test halt
        risk_manager.halt_trading("Test halt reason")
        assert risk_manager.trading_halted
        assert risk_manager.halt_reason == "Test halt reason"
        
        # Test resume
        risk_manager.resume_trading()
        assert not risk_manager.trading_halted
        assert risk_manager.halt_reason == ""
    
    def test_record_trade_pnl(self, risk_manager):
        """Test recording trade P&L."""
        initial_pnl = risk_manager.daily_pnl
        initial_trades = risk_manager.daily_trades
        
        risk_manager.record_trade_pnl(Decimal("100"))
        
        assert risk_manager.daily_pnl == initial_pnl + Decimal("100")
        assert risk_manager.daily_trades == initial_trades + 1
    
    def test_daily_loss_limit_halt(self, risk_manager):
        """Test automatic halt when daily loss limit is exceeded."""
        # Record large loss
        large_loss = Decimal("-6000")  # Exceeds 5% of 100k portfolio
        risk_manager.record_trade_pnl(large_loss)
        
        # Should trigger halt
        assert risk_manager.trading_halted
        assert "daily loss limit" in risk_manager.halt_reason.lower()


class TestPositionSizer:
    """Test cases for PositionSizer."""
    
    @pytest.fixture
    def risk_config(self):
        """Create test risk configuration."""
        return RiskConfig()
    
    @pytest.fixture
    def position_sizer(self, risk_config):
        """Create test position sizer."""
        return PositionSizer(risk_config)
    
    @pytest.fixture
    def sample_signal(self):
        """Create sample trading signal."""
        return TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy"
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("49500"),
            high=Decimal("50500"),
            low=Decimal("49000"),
            close=Decimal("50000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
    
    def test_calculate_position_size_fixed_percentage(self, position_sizer, sample_signal, sample_market_data):
        """Test fixed percentage position sizing."""
        portfolio_value = Decimal("100000")
        current_positions = []
        
        size = position_sizer.calculate_position_size(
            sample_signal, sample_market_data, portfolio_value, current_positions,
            SizingMethod.FIXED_PERCENTAGE
        )
        
        assert size > 0
        assert size <= portfolio_value * Decimal("0.20")  # Max position size
        assert size >= portfolio_value * Decimal("0.01")  # Min position size
    
    def test_calculate_position_size_volatility_adjusted(self, position_sizer, sample_signal, sample_market_data):
        """Test volatility-adjusted position sizing."""
        portfolio_value = Decimal("100000")
        current_positions = []
        
        size = position_sizer.calculate_position_size(
            sample_signal, sample_market_data, portfolio_value, current_positions,
            SizingMethod.VOLATILITY_ADJUSTED
        )
        
        assert size > 0
        assert size <= portfolio_value * Decimal("0.20")
    
    def test_calculate_shares_from_size(self, position_sizer):
        """Test share calculation from position size."""
        position_size = Decimal("5000")
        price = Decimal("50000")
        
        shares = position_sizer.calculate_shares_from_size(position_size, price)
        
        assert shares == Decimal("0.1")
    
    def test_validate_position_size_success(self, position_sizer):
        """Test successful position size validation."""
        position_size = Decimal("5000")
        portfolio_value = Decimal("100000")
        current_positions = []
        
        is_valid, reason = position_sizer.validate_position_size(
            position_size, portfolio_value, current_positions
        )
        
        assert is_valid
        assert "validation passed" in reason.lower()
    
    def test_validate_position_size_too_large(self, position_sizer):
        """Test position size validation with size too large."""
        position_size = Decimal("25000")  # 25% of portfolio
        portfolio_value = Decimal("100000")
        current_positions = []
        
        is_valid, reason = position_sizer.validate_position_size(
            position_size, portfolio_value, current_positions
        )
        
        assert not is_valid
        assert "exceeds maximum" in reason.lower()
    
    def test_get_sizing_recommendation(self, position_sizer, sample_signal, sample_market_data):
        """Test getting sizing recommendations."""
        portfolio_value = Decimal("100000")
        current_positions = []
        
        recommendation = position_sizer.get_sizing_recommendation(
            sample_signal, sample_market_data, portfolio_value, current_positions
        )
        
        assert 'recommended_method' in recommendation
        assert 'recommended_size' in recommendation
        assert 'all_methods' in recommendation
        assert 'risk_metrics' in recommendation


class TestStopLossManager:
    """Test cases for StopLossManager."""
    
    @pytest.fixture
    def risk_config(self):
        """Create test risk configuration."""
        return RiskConfig()
    
    @pytest.fixture
    def stop_loss_config(self):
        """Create test stop loss configuration."""
        return StopLossConfig()
    
    @pytest.fixture
    def stop_loss_manager(self, risk_config, stop_loss_config):
        """Create test stop loss manager."""
        return StopLossManager(risk_config, stop_loss_config)
    
    @pytest.fixture
    def sample_position(self):
        """Create sample position."""
        return Position(
            symbol="BTCUSDT",
            size=Decimal("0.1"),
            entry_price=Decimal("50000"),
            current_price=Decimal("51000"),
            timestamp=datetime.now(),
            exchange="binance",
            side=OrderSide.BUY
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("50500"),
            high=Decimal("51500"),
            low=Decimal("50000"),
            close=Decimal("51000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
    
    def test_create_fixed_stop_loss(self, stop_loss_manager, sample_position, sample_market_data):
        """Test creating a fixed stop loss."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        assert stop_order.stop_type == StopLossType.FIXED
        assert stop_order.symbol == sample_position.symbol
        assert stop_order.stop_price < sample_position.entry_price  # Stop below entry for BUY
        assert stop_order.is_active
    
    def test_create_trailing_stop_loss(self, stop_loss_manager, sample_position, sample_market_data):
        """Test creating a trailing stop loss."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.TRAILING
        )
        
        assert stop_order.stop_type == StopLossType.TRAILING
        assert stop_order.trail_distance is not None
        assert stop_order.activation_price is not None
    
    def test_update_stop_loss(self, stop_loss_manager, sample_position, sample_market_data):
        """Test updating stop loss."""
        # Create initial stop
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        # Update with new market data
        new_market_data = MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("51000"),
            high=Decimal("52000"),
            low=Decimal("50500"),
            close=Decimal("51500"),
            volume=Decimal("1000"),
            exchange="binance"
        )
        
        # Update position price
        sample_position.current_price = Decimal("51500")
        
        update_result = stop_loss_manager.update_stop_loss(sample_position, new_market_data)
        
        assert 'action' in update_result
        assert 'stop_order' in update_result
    
    def test_check_stop_trigger_not_triggered(self, stop_loss_manager, sample_position, sample_market_data):
        """Test stop loss not triggered."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        # Price above stop loss
        is_triggered = stop_loss_manager._check_stop_trigger(
            sample_position, sample_market_data, stop_order
        )
        
        assert not is_triggered
    
    def test_check_stop_trigger_triggered(self, stop_loss_manager, sample_position, sample_market_data):
        """Test stop loss triggered."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        # Create market data with price below stop loss
        trigger_market_data = MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("48000"),
            high=Decimal("48500"),
            low=Decimal("47500"),
            close=Decimal("48000"),  # Below stop loss
            volume=Decimal("1000"),
            exchange="binance"
        )
        
        is_triggered = stop_loss_manager._check_stop_trigger(
            sample_position, trigger_market_data, stop_order
        )
        
        assert is_triggered
    
    def test_remove_stop_loss(self, stop_loss_manager, sample_position, sample_market_data):
        """Test removing stop loss."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        position_id = f"{sample_position.symbol}_{sample_position.exchange}"
        
        # Verify stop exists
        assert position_id in stop_loss_manager.active_stops
        
        # Remove stop
        removed = stop_loss_manager.remove_stop_loss(position_id)
        
        assert removed
        assert position_id not in stop_loss_manager.active_stops
    
    def test_get_stop_loss_info(self, stop_loss_manager, sample_position, sample_market_data):
        """Test getting stop loss information."""
        stop_order = stop_loss_manager.create_stop_loss(
            sample_position, sample_market_data, StopLossType.FIXED
        )
        
        position_id = f"{sample_position.symbol}_{sample_position.exchange}"
        info = stop_loss_manager.get_stop_loss_info(position_id)
        
        assert info is not None
        assert info['symbol'] == sample_position.symbol
        assert info['stop_type'] == StopLossType.FIXED.value
        assert 'stop_price' in info
        assert 'created_at' in info


class TestDrawdownMonitor:
    """Test cases for DrawdownMonitor."""
    
    @pytest.fixture
    def risk_config(self):
        """Create test risk configuration."""
        return RiskConfig()
    
    @pytest.fixture
    def drawdown_config(self):
        """Create test drawdown configuration."""
        return DrawdownConfig()
    
    @pytest.fixture
    def drawdown_monitor(self, risk_config, drawdown_config):
        """Create test drawdown monitor."""
        return DrawdownMonitor(risk_config, drawdown_config)
    
    def test_drawdown_monitor_initialization(self, drawdown_monitor):
        """Test drawdown monitor initialization."""
        assert drawdown_monitor.config is not None
        assert drawdown_monitor.peak_value == Decimal("0")
        assert drawdown_monitor.current_drawdown_event is None
        assert len(drawdown_monitor.historical_drawdowns) == 0
    
    def test_update_portfolio_value_new_peak(self, drawdown_monitor):
        """Test updating portfolio value with new peak."""
        initial_value = Decimal("100000")
        higher_value = Decimal("110000")
        
        # Set initial value
        result1 = drawdown_monitor.update_portfolio_value(initial_value)
        assert result1['current_drawdown_pct'] == 0.0
        assert drawdown_monitor.peak_value == initial_value
        
        # Set higher value (new peak)
        result2 = drawdown_monitor.update_portfolio_value(higher_value)
        assert result2['current_drawdown_pct'] == 0.0
        assert drawdown_monitor.peak_value == higher_value
    
    def test_update_portfolio_value_drawdown(self, drawdown_monitor):
        """Test updating portfolio value with drawdown."""
        peak_value = Decimal("100000")
        drawdown_value = Decimal("90000")  # 10% drawdown
        
        # Set peak
        drawdown_monitor.update_portfolio_value(peak_value)
        
        # Create drawdown
        result = drawdown_monitor.update_portfolio_value(drawdown_value)
        
        assert result['current_drawdown_pct'] == 0.1  # 10%
        assert result['severity'] == DrawdownSeverity.MODERATE.value
        assert drawdown_monitor.current_drawdown_event is not None
        assert drawdown_monitor.current_drawdown_event.is_active
    
    def test_get_position_size_adjustment(self, drawdown_monitor):
        """Test position size adjustment based on drawdown."""
        # No drawdown
        adjustment1 = drawdown_monitor.get_position_size_adjustment(0.0)
        assert adjustment1 == 1.0
        
        # Minor drawdown
        adjustment2 = drawdown_monitor.get_position_size_adjustment(0.06)  # 6%
        assert adjustment2 < 1.0
        
        # Severe drawdown
        adjustment3 = drawdown_monitor.get_position_size_adjustment(0.16)  # 16%
        assert adjustment3 < adjustment2
    
    def test_should_halt_trading(self, drawdown_monitor):
        """Test trading halt recommendation."""
        # Low drawdown - no halt
        should_halt1, reason1 = drawdown_monitor.should_halt_trading(0.05)  # 5%
        assert not should_halt1
        
        # High drawdown - should halt
        should_halt2, reason2 = drawdown_monitor.should_halt_trading(0.15)  # 15%
        assert should_halt2
        assert "halt threshold" in reason2.lower()
    
    def test_should_emergency_exit(self, drawdown_monitor):
        """Test emergency exit recommendation."""
        # Moderate drawdown - no emergency exit
        should_exit1, reason1 = drawdown_monitor.should_emergency_exit(0.10)  # 10%
        assert not should_exit1
        
        # Critical drawdown - emergency exit
        should_exit2, reason2 = drawdown_monitor.should_emergency_exit(0.20)  # 20%
        assert should_exit2
        assert "emergency exit" in reason2.lower()
    
    def test_reset_peak(self, drawdown_monitor):
        """Test resetting peak value."""
        # Create initial peak and drawdown
        drawdown_monitor.update_portfolio_value(Decimal("100000"))
        drawdown_monitor.update_portfolio_value(Decimal("90000"))  # Create drawdown
        
        assert drawdown_monitor.current_drawdown_event is not None
        
        # Reset peak
        new_peak = Decimal("120000")
        drawdown_monitor.reset_peak(new_peak)
        
        assert drawdown_monitor.peak_value == new_peak
        assert drawdown_monitor.current_drawdown_event is None  # Should end drawdown
    
    def test_drawdown_event_lifecycle(self, drawdown_monitor):
        """Test complete drawdown event lifecycle."""
        peak_value = Decimal("100000")
        trough_value = Decimal("85000")  # 15% drawdown
        recovery_value = Decimal("87000")  # Slight recovery
        
        # Set peak
        drawdown_monitor.update_portfolio_value(peak_value)
        assert drawdown_monitor.current_drawdown_event is None
        
        # Create drawdown
        result1 = drawdown_monitor.update_portfolio_value(trough_value)
        assert drawdown_monitor.current_drawdown_event is not None
        assert drawdown_monitor.current_drawdown_event.is_active
        assert result1['severity'] == DrawdownSeverity.SEVERE.value
        
        # Partial recovery (not enough to end drawdown)
        result2 = drawdown_monitor.update_portfolio_value(recovery_value)
        assert drawdown_monitor.current_drawdown_event.is_active
        
        # Full recovery
        full_recovery_value = Decimal("102000")  # Above original peak
        result3 = drawdown_monitor.update_portfolio_value(full_recovery_value)
        assert drawdown_monitor.current_drawdown_event is None  # Should end
        assert len(drawdown_monitor.historical_drawdowns) == 1
    
    def test_get_drawdown_statistics(self, drawdown_monitor):
        """Test getting drawdown statistics."""
        # Create some drawdown history
        drawdown_monitor.update_portfolio_value(Decimal("100000"))
        drawdown_monitor.update_portfolio_value(Decimal("90000"))
        drawdown_monitor.update_portfolio_value(Decimal("105000"))  # Recovery
        
        stats = drawdown_monitor.get_drawdown_statistics()
        
        assert 'current_drawdown_pct' in stats
        assert 'peak_value' in stats
        assert 'total_drawdown_events' in stats
        assert 'thresholds' in stats
        assert stats['total_drawdown_events'] >= 0


# Integration tests
class TestRiskManagementIntegration:
    """Integration tests for risk management components."""
    
    @pytest.fixture
    def risk_manager(self):
        """Create risk manager for integration tests."""
        return RiskManager()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for integration tests."""
        signal = TradingSignal(
            symbol="BTCUSDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy"
        )
        
        market_data = MarketData(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            open=Decimal("49500"),
            high=Decimal("50500"),
            low=Decimal("49000"),
            close=Decimal("50000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
        
        position = Position(
            symbol="BTCUSDT",
            size=Decimal("0.1"),
            entry_price=Decimal("49000"),
            current_price=Decimal("50000"),
            timestamp=datetime.now(),
            exchange="binance",
            side=OrderSide.BUY
        )
        
        return signal, market_data, position
    
    def test_complete_risk_assessment_workflow(self, risk_manager, sample_data):
        """Test complete risk assessment workflow."""
        signal, market_data, position = sample_data
        portfolio_value = Decimal("100000")
        current_positions = [position]
        
        # 1. Assess trade risk
        assessment = risk_manager.assess_trade_risk(
            signal, market_data, portfolio_value, current_positions
        )
        
        assert isinstance(assessment, RiskAssessment)
        assert assessment.max_position_size is not None
        
        # 2. Create order based on assessment
        # Ensure we have a valid position size
        position_size = max(assessment.max_position_size, Decimal("100"))  # Minimum $100
        order = Order(
            id="test_order_1",
            symbol=signal.symbol,
            side=OrderSide.BUY,
            amount=position_size / market_data.close,
            price=market_data.close,
            order_type=OrderType.LIMIT,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
        
        # 3. Validate order
        is_valid, reason = risk_manager.validate_order(order, portfolio_value, current_positions)
        
        if assessment.level != RiskLevel.CRITICAL:
            assert is_valid
        
        # 4. Update position risk
        risk_update = risk_manager.update_position_risk(position, market_data)
        
        assert 'risk_score' in risk_update
        assert 'recommendations' in risk_update
        
        # 5. Check portfolio health
        health = risk_manager.check_portfolio_health(portfolio_value, current_positions)
        
        assert 'health_level' in health
        assert 'health_score' in health
    
    def test_risk_escalation_scenario(self, risk_manager):
        """Test risk escalation scenario with multiple losing positions."""
        portfolio_value = Decimal("100000")
        
        # Create multiple losing positions with significant losses
        losing_positions = []
        for i in range(5):
            position = Position(
                symbol=f"SYMBOL{i}",
                size=Decimal("200"),  # Larger positions
                entry_price=Decimal("100"),
                current_price=Decimal("70"),  # 30% loss each
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            )
            losing_positions.append(position)
        
        # Check portfolio health
        health = risk_manager.check_portfolio_health(portfolio_value, losing_positions)
        
        # Should show degraded health due to significant unrealized losses
        assert health['health_level'] in ['EXCELLENT', 'GOOD', 'FAIR', 'POOR']
        
        # Should have some warnings or drawdown
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in losing_positions)
        assert total_unrealized_pnl < 0  # Should have losses
    
    def test_recovery_scenario(self, risk_manager):
        """Test recovery scenario after drawdown."""
        portfolio_value = Decimal("100000")
        
        # Set initial peak
        risk_manager.drawdown_monitor.update_portfolio_value(Decimal("100000"))
        
        # Simulate drawdown
        risk_manager.drawdown_monitor.update_portfolio_value(Decimal("85000"))  # 15% drawdown
        
        # Check that drawdown is detected
        health1 = risk_manager.check_portfolio_health(Decimal("85000"), [])
        assert health1['drawdown_status']['current_drawdown_pct'] > 0.1  # Should be > 10%
        assert health1['drawdown_status']['severity'] in [DrawdownSeverity.SEVERE.value, DrawdownSeverity.MODERATE.value]
        
        # Simulate recovery
        risk_manager.drawdown_monitor.update_portfolio_value(Decimal("105000"))  # Recovery
        
        # Check that drawdown is reduced
        health2 = risk_manager.check_portfolio_health(Decimal("105000"), [])
        assert health2['drawdown_status']['current_drawdown_pct'] == 0.0


if __name__ == "__main__":
    pytest.main([__file__])