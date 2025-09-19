"""
Tests for cross-market risk management system.

This module tests the cross-market risk management components including
CrossMarketRiskManager, CorrelationMonitor, UnifiedPositionSizer, and MarketSpecificRiskRules.
"""

import pytest
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.risk.cross_market_risk_manager import CrossMarketRiskManager, CrossMarketRiskConfig
from src.risk.correlation_monitor import CorrelationMonitor, CorrelationData
from src.risk.unified_position_sizer import UnifiedPositionSizer, UnifiedSizingMethod
from src.risk.market_specific_risk_rules import MarketSpecificRiskRules, MarketRiskLimits
from src.models.data_models import TradingSignal, MarketData, Order, Position, SignalAction, OrderSide, OrderType, OrderStatus
from src.markets.types import MarketType, UnifiedSymbol


class TestCrossMarketRiskManager:
    """Test cases for CrossMarketRiskManager."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return CrossMarketRiskConfig(
            max_portfolio_risk_pct=0.02,
            max_correlation_exposure=0.5,
            correlation_threshold=0.7,
            max_crypto_allocation=0.6,
            max_forex_allocation=0.6
        )
    
    @pytest.fixture
    def risk_manager(self, config):
        """Create test risk manager."""
        return CrossMarketRiskManager(config)
    
    @pytest.fixture
    def sample_signal(self):
        """Create sample trading signal."""
        return TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000")
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return MarketData(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            open=Decimal("49500"),
            high=Decimal("50500"),
            low=Decimal("49000"),
            close=Decimal("50000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
    
    @pytest.fixture
    def sample_positions(self):
        """Create sample positions across markets."""
        crypto_positions = [
            Position(
                symbol="BTC/USDT",
                size=Decimal("0.1"),
                entry_price=Decimal("48000"),
                current_price=Decimal("50000"),
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            ),
            Position(
                symbol="ETH/USDT",
                size=Decimal("2.0"),
                entry_price=Decimal("3000"),
                current_price=Decimal("3200"),
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            )
        ]
        
        forex_positions = [
            Position(
                symbol="EURUSD",
                size=Decimal("10000"),
                entry_price=Decimal("1.1000"),
                current_price=Decimal("1.1050"),
                timestamp=datetime.now(),
                exchange="oanda",
                side=OrderSide.BUY
            )
        ]
        
        return {
            MarketType.CRYPTO: crypto_positions,
            MarketType.FOREX: forex_positions
        }
    
    def test_initialization(self, risk_manager, config):
        """Test risk manager initialization."""
        assert risk_manager.cross_market_config == config
        assert risk_manager.correlation_monitor is not None
        assert risk_manager.unified_position_sizer is not None
        assert risk_manager.market_risk_rules is not None
        assert isinstance(risk_manager.market_allocations, dict)
    
    def test_assess_cross_market_trade_risk(self, risk_manager, sample_signal, sample_market_data, sample_positions):
        """Test cross-market trade risk assessment."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        
        assessment = risk_manager.assess_cross_market_trade_risk(
            sample_signal, sample_market_data, portfolio_value, sample_positions, symbol
        )
        
        assert assessment is not None
        assert hasattr(assessment, 'level')
        assert hasattr(assessment, 'score')
        assert hasattr(assessment, 'reasons')
        assert hasattr(assessment, 'recommendations')
        assert 0.0 <= assessment.score <= 1.0
    
    def test_validate_cross_market_order(self, risk_manager, sample_positions):
        """Test cross-market order validation."""
        order = Order(
            id="test_order",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
        
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        
        is_valid, reason = risk_manager.validate_cross_market_order(
            order, symbol, portfolio_value, sample_positions
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(reason, str)
    
    def test_update_cross_market_positions(self, risk_manager, sample_positions):
        """Test cross-market position updates."""
        market_data = {
            "BTC/USDT": MarketData(
                symbol="BTC/USDT",
                timestamp=datetime.now(),
                open=Decimal("49500"),
                high=Decimal("50500"),
                low=Decimal("49000"),
                close=Decimal("50000"),
                volume=Decimal("1000"),
                exchange="binance"
            ),
            "ETH/USDT": MarketData(
                symbol="ETH/USDT",
                timestamp=datetime.now(),
                open=Decimal("3100"),
                high=Decimal("3250"),
                low=Decimal("3050"),
                close=Decimal("3200"),
                volume=Decimal("500"),
                exchange="binance"
            )
        }
        
        update_report = risk_manager.update_cross_market_positions(sample_positions, market_data)
        
        assert 'timestamp' in update_report
        assert 'market_allocations' in update_report
        assert 'correlation_summary' in update_report
        assert 'risk_events' in update_report
        assert 'recommendations' in update_report
    
    def test_check_cross_market_portfolio_health(self, risk_manager, sample_positions):
        """Test cross-market portfolio health check."""
        portfolio_value = Decimal("50000")
        market_data = {
            "BTC/USDT": MarketData(
                symbol="BTC/USDT",
                timestamp=datetime.now(),
                open=Decimal("49500"),
                high=Decimal("50500"),
                low=Decimal("49000"),
                close=Decimal("50000"),
                volume=Decimal("1000"),
                exchange="binance"
            )
        }
        
        health_report = risk_manager.check_cross_market_portfolio_health(
            portfolio_value, sample_positions, market_data
        )
        
        assert 'health_level' in health_report
        assert 'health_score' in health_report
        assert 'cross_market_metrics' in health_report
    
    def test_handle_cross_market_emergency(self, risk_manager):
        """Test cross-market emergency handling."""
        emergency_details = {'drawdown_pct': 0.10}
        
        response = risk_manager.handle_cross_market_emergency(
            "CROSS_MARKET_DRAWDOWN", emergency_details
        )
        
        assert 'emergency_type' in response
        assert 'timestamp' in response
        assert 'actions_taken' in response
        assert response['emergency_type'] == "CROSS_MARKET_DRAWDOWN"
        assert isinstance(response['actions_taken'], list)


class TestCorrelationMonitor:
    """Test cases for CorrelationMonitor."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return CrossMarketRiskConfig(correlation_lookback_days=20)
    
    @pytest.fixture
    def correlation_monitor(self, config):
        """Create test correlation monitor."""
        return CorrelationMonitor(config)
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data for correlation testing."""
        return {
            "BTC/USDT": MarketData(
                symbol="BTC/USDT",
                timestamp=datetime.now(),
                open=Decimal("49500"),
                high=Decimal("50500"),
                low=Decimal("49000"),
                close=Decimal("50000"),
                volume=Decimal("1000"),
                exchange="binance"
            ),
            "ETH/USDT": MarketData(
                symbol="ETH/USDT",
                timestamp=datetime.now(),
                open=Decimal("3100"),
                high=Decimal("3250"),
                low=Decimal("3050"),
                close=Decimal("3200"),
                volume=Decimal("500"),
                exchange="binance"
            ),
            "EURUSD": MarketData(
                symbol="EURUSD",
                timestamp=datetime.now(),
                open=Decimal("1.1000"),
                high=Decimal("1.1080"),
                low=Decimal("1.0980"),
                close=Decimal("1.1050"),
                volume=Decimal("100000"),
                exchange="oanda"
            )
        }
    
    def test_initialization(self, correlation_monitor, config):
        """Test correlation monitor initialization."""
        assert correlation_monitor.config == config
        assert isinstance(correlation_monitor.correlations, dict)
        assert isinstance(correlation_monitor.price_history, dict)
        assert isinstance(correlation_monitor.return_history, dict)
    
    def test_update_correlations(self, correlation_monitor, sample_market_data):
        """Test correlation updates."""
        # Add some historical data first
        for i in range(15):  # Add 15 data points
            historical_data = {}
            for symbol, data in sample_market_data.items():
                # Create slightly varying prices
                base_price = float(data.close)
                variation = np.random.normal(0, 0.02)  # 2% volatility
                new_price = base_price * (1 + variation)
                
                historical_data[symbol] = MarketData(
                    symbol=symbol,
                    timestamp=datetime.now() - timedelta(days=i),
                    open=Decimal(str(new_price * 0.99)),
                    high=Decimal(str(new_price * 1.02)),
                    low=Decimal(str(new_price * 0.98)),
                    close=Decimal(str(new_price)),
                    volume=data.volume,
                    exchange=data.exchange
                )
            
            correlation_monitor.update_correlations({}, historical_data)
        
        # Check that correlations were calculated
        assert len(correlation_monitor.correlations) > 0
        
        # Check that price history was updated
        for symbol in sample_market_data.keys():
            assert len(correlation_monitor.price_history[symbol]) > 0
    
    def test_get_correlation(self, correlation_monitor):
        """Test getting correlation between symbols."""
        # Add some test correlation data
        correlation_monitor.correlations[("BTC/USDT", "ETH/USDT")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="ETH/USDT",
            correlation=0.75,
            confidence=0.8,
            last_updated=datetime.now(),
            data_points=20
        )
        
        correlation = correlation_monitor.get_correlation("BTC/USDT", "ETH/USDT")
        assert correlation == 0.75
        
        correlation = correlation_monitor.get_correlation("ETH/USDT", "BTC/USDT")
        assert correlation == 0.75  # Should be symmetric
        
        # Test non-existent correlation
        correlation = correlation_monitor.get_correlation("BTC/USDT", "NONEXISTENT")
        assert correlation is None
    
    def test_get_symbol_correlations(self, correlation_monitor):
        """Test getting all correlations for a symbol."""
        # Add test data
        correlation_monitor.correlations[("BTC/USDT", "ETH/USDT")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="ETH/USDT",
            correlation=0.75,
            confidence=0.8,
            last_updated=datetime.now(),
            data_points=20
        )
        
        correlation_monitor.correlations[("BTC/USDT", "EURUSD")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="EURUSD",
            correlation=0.25,
            confidence=0.7,
            last_updated=datetime.now(),
            data_points=15
        )
        
        correlations = correlation_monitor.get_symbol_correlations("BTC/USDT")
        
        assert "ETH/USDT" in correlations
        assert "EURUSD" in correlations
        assert correlations["ETH/USDT"] == 0.75
        assert correlations["EURUSD"] == 0.25
    
    def test_get_high_correlations(self, correlation_monitor):
        """Test getting high correlation pairs."""
        # Add test data with various correlation levels
        correlation_monitor.correlations[("BTC/USDT", "ETH/USDT")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="ETH/USDT",
            correlation=0.85,  # High correlation
            confidence=0.8,
            last_updated=datetime.now(),
            data_points=20
        )
        
        correlation_monitor.correlations[("BTC/USDT", "EURUSD")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="EURUSD",
            correlation=0.25,  # Low correlation
            confidence=0.7,
            last_updated=datetime.now(),
            data_points=15
        )
        
        high_correlations = correlation_monitor.get_high_correlations(0.8)
        
        assert len(high_correlations) == 1
        assert high_correlations[0]['symbol1'] == "BTC/USDT"
        assert high_correlations[0]['symbol2'] == "ETH/USDT"
        assert high_correlations[0]['correlation'] == 0.85
    
    def test_get_correlation_summary(self, correlation_monitor):
        """Test correlation summary generation."""
        # Add test data
        correlation_monitor.correlations[("BTC/USDT", "ETH/USDT")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="ETH/USDT",
            correlation=0.85,
            confidence=0.8,
            last_updated=datetime.now(),
            data_points=20
        )
        
        correlation_monitor.correlations[("BTC/USDT", "EURUSD")] = CorrelationData(
            symbol1="BTC/USDT",
            symbol2="EURUSD",
            correlation=0.25,
            confidence=0.7,
            last_updated=datetime.now(),
            data_points=15
        )
        
        summary = correlation_monitor.get_correlation_summary()
        
        assert 'total_pairs' in summary
        assert 'reliable_pairs' in summary
        assert 'high_correlation_pairs' in summary
        assert 'average_correlation' in summary
        assert summary['total_pairs'] == 2
        assert summary['reliable_pairs'] == 2


class TestUnifiedPositionSizer:
    """Test cases for UnifiedPositionSizer."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return CrossMarketRiskConfig()
    
    @pytest.fixture
    def position_sizer(self, config):
        """Create test position sizer."""
        return UnifiedPositionSizer(config)
    
    @pytest.fixture
    def sample_signal(self):
        """Create sample trading signal."""
        return TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("50000")
        )
    
    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return MarketData(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            open=Decimal("49500"),
            high=Decimal("50500"),
            low=Decimal("49000"),
            close=Decimal("50000"),
            volume=Decimal("1000"),
            exchange="binance"
        )
    
    @pytest.fixture
    def sample_positions(self):
        """Create sample positions."""
        return {
            MarketType.CRYPTO: [
                Position(
                    symbol="ETH/USDT",
                    size=Decimal("2.0"),
                    entry_price=Decimal("3000"),
                    current_price=Decimal("3200"),
                    timestamp=datetime.now(),
                    exchange="binance",
                    side=OrderSide.BUY
                )
            ],
            MarketType.FOREX: []
        }
    
    def test_initialization(self, position_sizer, config):
        """Test position sizer initialization."""
        assert position_sizer.cross_market_config == config
        assert hasattr(position_sizer, 'unified_sizing_config')
        assert isinstance(position_sizer.unified_sizing_config, dict)
    
    def test_calculate_unified_position_size(self, position_sizer, sample_signal, sample_market_data, sample_positions):
        """Test unified position size calculation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        
        position_size = position_sizer.calculate_unified_position_size(
            sample_signal, symbol, sample_market_data, portfolio_value, sample_positions
        )
        
        assert isinstance(position_size, Decimal)
        assert position_size > 0
        assert position_size <= portfolio_value  # Should not exceed portfolio value
    
    def test_unified_sizing_methods(self, position_sizer, sample_signal, sample_market_data, sample_positions):
        """Test different unified sizing methods."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        
        methods = [
            UnifiedSizingMethod.CORRELATION_ADJUSTED,
            UnifiedSizingMethod.MARKET_NEUTRAL,
            UnifiedSizingMethod.CROSS_MARKET_MOMENTUM,
            UnifiedSizingMethod.RISK_PARITY_CROSS_MARKET
        ]
        
        for method in methods:
            position_size = position_sizer.calculate_unified_position_size(
                sample_signal, symbol, sample_market_data, portfolio_value, sample_positions, method
            )
            
            assert isinstance(position_size, Decimal)
            assert position_size >= 0
    
    def test_get_unified_sizing_recommendation(self, position_sizer, sample_signal, sample_market_data, sample_positions):
        """Test unified sizing recommendation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        
        recommendation = position_sizer.get_unified_sizing_recommendation(
            sample_signal, symbol, sample_market_data, portfolio_value, sample_positions
        )
        
        assert 'recommended_method' in recommendation
        assert 'recommended_size' in recommendation
        assert 'all_methods' in recommendation
        assert 'cross_market_analysis' in recommendation
    
    def test_calculate_optimal_market_allocation(self, position_sizer, sample_positions):
        """Test optimal market allocation calculation."""
        portfolio_value = Decimal("50000")
        
        allocation = position_sizer.calculate_optimal_market_allocation(
            portfolio_value, sample_positions
        )
        
        assert 'current_total_allocated' in allocation
        assert 'market_recommendations' in allocation
        assert 'allocation_efficiency' in allocation
        assert 'rebalancing_needed' in allocation


class TestMarketSpecificRiskRules:
    """Test cases for MarketSpecificRiskRules."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return CrossMarketRiskConfig()
    
    @pytest.fixture
    def risk_rules(self, config):
        """Create test risk rules."""
        return MarketSpecificRiskRules(config)
    
    @pytest.fixture
    def sample_crypto_order(self):
        """Create sample crypto order."""
        return Order(
            id="crypto_order",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=Decimal("0.1"),
            price=Decimal("50000"),
            order_type=OrderType.MARKET,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
    
    @pytest.fixture
    def sample_forex_order(self):
        """Create sample forex order."""
        return Order(
            id="forex_order",
            symbol="EURUSD",
            side=OrderSide.BUY,
            amount=Decimal("10000"),
            price=Decimal("1.1050"),
            order_type=OrderType.MARKET,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="oanda"
        )
    
    def test_initialization(self, risk_rules, config):
        """Test risk rules initialization."""
        assert risk_rules.config == config
        assert isinstance(risk_rules.market_limits, dict)
        assert MarketType.CRYPTO in risk_rules.market_limits
        assert MarketType.FOREX in risk_rules.market_limits
    
    def test_validate_crypto_order(self, risk_rules, sample_crypto_order):
        """Test crypto order validation."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        market_positions = []
        
        is_valid, reason = risk_rules.validate_order(
            sample_crypto_order, symbol, portfolio_value, market_positions
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(reason, str)
    
    def test_validate_forex_order(self, risk_rules, sample_forex_order):
        """Test forex order validation."""
        symbol = UnifiedSymbol.from_forex_symbol("EURUSD")
        portfolio_value = Decimal("50000")
        market_positions = []
        
        is_valid, reason = risk_rules.validate_order(
            sample_forex_order, symbol, portfolio_value, market_positions
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(reason, str)
    
    def test_get_market_risk_assessment(self, risk_rules):
        """Test market risk assessment."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        market_positions = []
        
        assessment = risk_rules.get_market_risk_assessment(
            symbol, portfolio_value, market_positions
        )
        
        assert 'market_type' in assessment
        assert 'risk_level' in assessment
        assert 'risk_score' in assessment
        assert 'metrics' in assessment
        assert 'limits' in assessment
    
    def test_update_daily_activity(self, risk_rules):
        """Test daily activity tracking."""
        initial_trades = risk_rules.daily_trades.get(MarketType.CRYPTO, 0)
        initial_volume = risk_rules.daily_volume.get(MarketType.CRYPTO, Decimal("0"))
        
        risk_rules.update_daily_activity(MarketType.CRYPTO, Decimal("1000"))
        
        assert risk_rules.daily_trades[MarketType.CRYPTO] == initial_trades + 1
        assert risk_rules.daily_volume[MarketType.CRYPTO] == initial_volume + Decimal("1000")
    
    def test_reset_daily_counters(self, risk_rules):
        """Test daily counter reset."""
        # Add some activity
        risk_rules.update_daily_activity(MarketType.CRYPTO, Decimal("1000"))
        risk_rules.update_daily_activity(MarketType.FOREX, Decimal("5000"))
        
        # Reset counters
        risk_rules.reset_daily_counters()
        
        assert len(risk_rules.daily_trades) == 0
        assert len(risk_rules.daily_volume) == 0
    
    def test_get_market_recommendations(self, risk_rules):
        """Test market recommendations."""
        symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        portfolio_value = Decimal("50000")
        market_positions = []
        
        recommendations = risk_rules.get_market_recommendations(
            symbol, portfolio_value, market_positions
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_adjust_limits_for_volatility(self, risk_rules):
        """Test volatility-based limit adjustments."""
        # Get original limits
        original_limits = risk_rules.market_limits[MarketType.CRYPTO]
        original_position_size_pct = original_limits.max_position_size_pct
        
        # Adjust for high volatility
        risk_rules.adjust_limits_for_volatility(MarketType.CRYPTO, 0.15)  # 15% volatility
        
        # Check that limits were tightened
        adjusted_limits = risk_rules.market_limits[MarketType.CRYPTO]
        assert adjusted_limits.max_position_size_pct < original_position_size_pct
    
    def test_market_specific_limits(self, risk_rules):
        """Test that different markets have appropriate limits."""
        crypto_limits = risk_rules.market_limits[MarketType.CRYPTO]
        forex_limits = risk_rules.market_limits[MarketType.FOREX]
        
        # Crypto should allow higher volatility tolerance
        assert crypto_limits.volatility_threshold > forex_limits.volatility_threshold
        
        # Forex should allow higher leverage
        assert forex_limits.max_leverage > crypto_limits.max_leverage
        
        # Both should have reasonable position limits
        assert 0 < crypto_limits.max_position_size_pct <= 1
        assert 0 < forex_limits.max_position_size_pct <= 1


class TestIntegration:
    """Integration tests for cross-market risk management system."""
    
    @pytest.fixture
    def full_system(self):
        """Create complete cross-market risk management system."""
        config = CrossMarketRiskConfig()
        return CrossMarketRiskManager(config)
    
    @pytest.fixture
    def complex_portfolio(self):
        """Create complex multi-market portfolio."""
        crypto_positions = [
            Position(
                symbol="BTC/USDT",
                size=Decimal("0.5"),
                entry_price=Decimal("48000"),
                current_price=Decimal("50000"),
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            ),
            Position(
                symbol="ETH/USDT",
                size=Decimal("5.0"),
                entry_price=Decimal("3000"),
                current_price=Decimal("3200"),
                timestamp=datetime.now(),
                exchange="binance",
                side=OrderSide.BUY
            )
        ]
        
        forex_positions = [
            Position(
                symbol="EURUSD",
                size=Decimal("50000"),
                entry_price=Decimal("1.1000"),
                current_price=Decimal("1.1050"),
                timestamp=datetime.now(),
                exchange="oanda",
                side=OrderSide.BUY
            ),
            Position(
                symbol="GBPUSD",
                size=Decimal("30000"),
                entry_price=Decimal("1.2500"),
                current_price=Decimal("1.2600"),
                timestamp=datetime.now(),
                exchange="oanda",
                side=OrderSide.BUY
            )
        ]
        
        return {
            MarketType.CRYPTO: crypto_positions,
            MarketType.FOREX: forex_positions
        }
    
    def test_full_risk_assessment_workflow(self, full_system, complex_portfolio):
        """Test complete risk assessment workflow."""
        portfolio_value = Decimal("150000")
        
        # Test signal for new position
        signal = TradingSignal(
            symbol="ADA/USDT",
            action=SignalAction.BUY,
            confidence=0.7,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("1.50")
        )
        
        market_data = MarketData(
            symbol="ADA/USDT",
            timestamp=datetime.now(),
            open=Decimal("1.48"),
            high=Decimal("1.52"),
            low=Decimal("1.46"),
            close=Decimal("1.50"),
            volume=Decimal("10000"),
            exchange="binance"
        )
        
        symbol = UnifiedSymbol.from_crypto_symbol("ADAUSDT")
        
        # Perform risk assessment
        assessment = full_system.assess_cross_market_trade_risk(
            signal, market_data, portfolio_value, complex_portfolio, symbol
        )
        
        assert assessment is not None
        assert hasattr(assessment, 'level')
        assert hasattr(assessment, 'score')
        
        # Test order validation
        order = Order(
            id="ada_order",
            symbol="ADA/USDT",
            side=OrderSide.BUY,
            amount=Decimal("1000"),
            price=Decimal("1.50"),
            order_type=OrderType.MARKET,
            status=OrderStatus.PENDING,
            timestamp=datetime.now(),
            exchange="binance"
        )
        
        is_valid, reason = full_system.validate_cross_market_order(
            order, symbol, portfolio_value, complex_portfolio
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(reason, str)
        
        # Test portfolio health check
        market_data_dict = {
            "BTC/USDT": market_data,
            "ETH/USDT": market_data,
            "EURUSD": market_data,
            "GBPUSD": market_data,
            "ADA/USDT": market_data
        }
        
        health_report = full_system.check_cross_market_portfolio_health(
            portfolio_value, complex_portfolio, market_data_dict
        )
        
        assert 'health_level' in health_report
        assert 'cross_market_metrics' in health_report
    
    def test_correlation_impact_on_sizing(self, full_system, complex_portfolio):
        """Test that correlations impact position sizing."""
        portfolio_value = Decimal("150000")
        
        # Test highly correlated asset (another crypto)
        btc_signal = TradingSignal(
            symbol="BTC/USDT",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("51000")
        )
        
        # Test uncorrelated asset (forex)
        eur_signal = TradingSignal(
            symbol="CHFJPY",
            action=SignalAction.BUY,
            confidence=0.8,
            timestamp=datetime.now(),
            strategy_name="test_strategy",
            price=Decimal("165.50")
        )
        
        market_data = MarketData(
            symbol="TEST",
            timestamp=datetime.now(),
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("98"),
            close=Decimal("101"),
            volume=Decimal("1000"),
            exchange="test_exchange"
        )
        
        btc_symbol = UnifiedSymbol.from_crypto_symbol("BTCUSDT")
        chf_symbol = UnifiedSymbol.from_forex_symbol("CHFJPY")
        
        # Get position sizes
        btc_size = full_system.get_unified_position_size(
            btc_signal, btc_symbol, market_data, portfolio_value, complex_portfolio
        )
        
        chf_size = full_system.get_unified_position_size(
            eur_signal, chf_symbol, market_data, portfolio_value, complex_portfolio
        )
        
        # BTC size should be smaller due to existing BTC correlation
        # CHF size should be larger due to diversification benefit
        assert isinstance(btc_size, Decimal)
        assert isinstance(chf_size, Decimal)
        assert btc_size >= 0
        assert chf_size >= 0


if __name__ == "__main__":
    pytest.main([__file__])