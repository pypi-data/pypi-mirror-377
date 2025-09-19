#!/usr/bin/env python3

"""
Comprehensive tests for anti-greed trading mechanisms.

This test suite verifies that:
1. All strategies are properly integrated
2. Anti-greed mechanisms work correctly
3. Immediate profit taking occurs
4. Risk management is effective
5. Position management prevents greediness
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.position_manager import AggressivePositionManager, PositionMetrics, ExitTrigger
from src.trading.portfolio_orchestrator import PortfolioOrchestrator, Position, ExitReason
from src.trading.trading_bot import TradingBot
from src.models.data_models import MarketData, TradingSignal, SignalAction


class TestAntiGreedMechanisms(unittest.TestCase):
    """Test anti-greed mechanisms in the trading system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.position_manager = AggressivePositionManager()
        self.orchestrator = PortfolioOrchestrator(max_positions=3)
        
    def test_immediate_profit_taking(self):
        """Test that profits are taken immediately when targets are reached."""
        # Create a profitable position scenario
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('52000'),  # 4% profit
            max_profit=Decimal('0.04'),
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=2),
            profit_velocity=0.001
        )
        
        market_conditions = {'extreme_volatility': False}
        
        # Test high confidence signal (should take profit at 4%)
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.92, market_conditions
        )
        
        self.assertEqual(recommendation['action'], 'EXIT_FULL')
        self.assertEqual(recommendation['urgency'], 'IMMEDIATE')
        self.assertIn('Take profit target reached', recommendation['reasons'][0])
        self.assertEqual(recommendation['confidence'], 1.0)
    
    def test_stop_loss_immediate_exit(self):
        """Test that stop losses trigger immediate exits."""
        # Create a losing position scenario
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('49200'),  # -1.6% loss
            max_profit=Decimal('0'),
            max_loss=Decimal('-0.016'),
            hold_time=timedelta(hours=1),
            profit_velocity=-0.002
        )
        
        market_conditions = {'extreme_volatility': False}
        
        # Test medium confidence signal (should stop out at -2%)
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.87, market_conditions
        )
        
        self.assertEqual(recommendation['action'], 'EXIT_FULL')
        self.assertEqual(recommendation['urgency'], 'IMMEDIATE')
        self.assertIn('Stop loss triggered', recommendation['reasons'][0])
        self.assertEqual(recommendation['confidence'], 1.0)
    
    def test_profit_drawdown_protection(self):
        """Test that positions are closed when profit declines significantly."""
        # Create a position with declining profit
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('51000'),  # 2% current profit
            max_profit=Decimal('0.05'),      # 5% max profit achieved
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=4),
            profit_velocity=-0.001
        )
        
        market_conditions = {'extreme_volatility': False}
        
        # Should trigger profit protection (3% drawdown from 5% peak)
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.90, market_conditions
        )
        
        self.assertEqual(recommendation['action'], 'EXIT_FULL')
        self.assertEqual(recommendation['urgency'], 'HIGH')
        self.assertIn('Profit drawdown', recommendation['reasons'][0])
        self.assertGreaterEqual(recommendation['confidence'], 0.8)
    
    def test_position_scaling_anti_greed(self):
        """Test that positions are scaled out to prevent greediness."""
        # Create a very profitable position
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('54000'),  # 8% profit
            max_profit=Decimal('0.08'),
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=3),
            profit_velocity=0.002
        )
        
        # Should recommend scaling out at 2x take profit target
        scale_out = self.position_manager.should_scale_out(metrics, 0.90)
        
        self.assertIsNotNone(scale_out)
        self.assertEqual(scale_out[0], 0.5)  # 50% scale out
        self.assertIn('2x target', scale_out[1])
    
    def test_time_based_exits(self):
        """Test that positions are closed based on time limits."""
        # Create a position held too long
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('50500'),  # 1% profit
            max_profit=Decimal('0.015'),
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=25),  # Exceeds 24h limit for low confidence
            profit_velocity=0.0001
        )
        
        market_conditions = {'extreme_volatility': False}
        
        # Should trigger time-based exit
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.82, market_conditions  # Low confidence
        )
        
        self.assertEqual(recommendation['action'], 'EXIT_FULL')
        self.assertIn('Maximum hold time', recommendation['reasons'][0])
    
    def test_extreme_volatility_exit(self):
        """Test that positions are closed during extreme volatility."""
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('50800'),  # 1.6% profit
            max_profit=Decimal('0.02'),
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=2),
            profit_velocity=0.001
        )
        
        market_conditions = {'extreme_volatility': True}
        
        # Should trigger volatility-based exit
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.88, market_conditions
        )
        
        self.assertEqual(recommendation['action'], 'EXIT_FULL')
        self.assertEqual(recommendation['urgency'], 'HIGH')
        self.assertIn('Extreme market volatility', recommendation['reasons'][0])
    
    def test_negative_momentum_scaling(self):
        """Test that positions are scaled when profit momentum turns negative."""
        metrics = PositionMetrics(
            entry_price=Decimal('50000'),
            current_price=Decimal('51200'),  # 2.4% profit
            max_profit=Decimal('0.03'),      # 3% max profit
            max_loss=Decimal('0'),
            hold_time=timedelta(hours=3),
            profit_velocity=-0.002  # Negative momentum
        )
        
        market_conditions = {'extreme_volatility': False}
        
        # Should recommend scaling out due to negative momentum
        recommendation = self.position_manager.get_aggressive_exit_recommendation(
            metrics, 0.88, market_conditions
        )
        
        self.assertEqual(recommendation['action'], 'SCALE_OUT')
        self.assertEqual(recommendation['scale_out_pct'], 0.4)
        self.assertIn('Negative profit momentum', recommendation['reasons'][0])


class TestPortfolioOrchestrator(unittest.TestCase):
    """Test portfolio orchestrator anti-greed mechanisms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.orchestrator = PortfolioOrchestrator(
            max_positions=3,
            profit_target_multiplier=2.0,
            trailing_stop_activation=0.01
        )
    
    def test_immediate_exit_on_profit_target(self):
        """Test that positions are immediately closed when profit targets are hit."""
        # Create a position that hits profit target
        position = Position(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            entry_price=Decimal('50000'),
            quantity=Decimal('0.1'),
            entry_time=datetime.now() - timedelta(hours=2),
            strategy_name='test_strategy',
            confidence=0.90,
            take_profit=Decimal('51000')  # 2% take profit
        )
        
        # Add position to orchestrator
        self.orchestrator.active_positions['test_pos'] = position
        
        # Simulate market data hitting take profit
        current_price = 51000.0
        current_time = datetime.now()
        
        # Check for immediate exits
        exit_actions = self.orchestrator._check_immediate_exits(
            current_price, current_time, 'BTCUSD'
        )
        
        self.assertEqual(len(exit_actions), 1)
        self.assertEqual(exit_actions[0]['action'], 'EXIT')
        self.assertEqual(exit_actions[0]['reason'], 'take_profit')
    
    def test_anti_greed_profit_decline_exit(self):
        """Test that positions are closed when profit declines from peak."""
        # Create a position with declining profit
        position = Position(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            entry_price=Decimal('50000'),
            quantity=Decimal('0.1'),
            entry_time=datetime.now() - timedelta(hours=3),
            strategy_name='test_strategy',
            confidence=0.88,
            max_profit=Decimal('2000')  # Had $2000 profit at peak
        )
        
        # Current profit is much lower (30% decline from peak)
        position.current_pnl = Decimal('1400')  # $1400 current profit
        
        self.orchestrator.active_positions['test_pos'] = position
        
        # Should trigger anti-greed exit
        exit_actions = self.orchestrator._check_immediate_exits(
            51400.0, datetime.now(), 'BTCUSD'
        )
        
        self.assertEqual(len(exit_actions), 1)
        self.assertEqual(exit_actions[0]['reason'], 'risk_management')


class TestTradingBotIntegration(unittest.TestCase):
    """Test complete trading bot integration with anti-greed mechanisms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trading_bot = TradingBot(
            symbols=['BTCUSD'],
            enable_paper_trading=True,
            max_positions=2
        )
    
    def test_anti_greed_mode_enabled(self):
        """Test that anti-greed mode is properly enabled."""
        self.trading_bot.enable_anti_greed_mode()
        
        self.assertTrue(self.trading_bot.profit_taking_enabled)
        self.assertTrue(self.trading_bot.immediate_exit_on_target)
        self.assertEqual(self.trading_bot.orchestrator.profit_target_multiplier, 1.5)
    
    def test_immediate_execution_no_delays(self):
        """Test that trading actions are executed immediately without delays."""
        # Mock action for immediate execution
        action = {
            'action': 'ENTER',
            'symbol': 'BTCUSD',
            'side': 'BUY',
            'quantity': 0.1,
            'price': 50000.0,
            'strategy': 'test_strategy',
            'confidence': 0.90
        }
        
        # Execute action and verify immediate execution
        start_time = datetime.now()
        self.trading_bot._execute_action_immediately(action)
        execution_time = datetime.now() - start_time
        
        # Should execute in less than 100ms
        self.assertLess(execution_time.total_seconds(), 0.1)
        
        # Verify action was logged
        self.assertEqual(len(self.trading_bot.execution_log), 1)
        self.assertTrue(self.trading_bot.execution_log[0]['executed'])
    
    def test_force_exit_all_positions(self):
        """Test that all positions can be force-closed immediately."""
        # Add mock positions to orchestrator
        position1 = Position(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            entry_price=Decimal('50000'),
            quantity=Decimal('0.1'),
            entry_time=datetime.now(),
            strategy_name='test_strategy1',
            confidence=0.90
        )
        
        position2 = Position(
            symbol='ETHUSD',
            action=SignalAction.SELL,
            entry_price=Decimal('3000'),
            quantity=Decimal('1.0'),
            entry_time=datetime.now(),
            strategy_name='test_strategy2',
            confidence=0.85
        )
        
        self.trading_bot.orchestrator.active_positions['pos1'] = position1
        self.trading_bot.orchestrator.active_positions['pos2'] = position2
        
        # Force exit all positions
        initial_log_count = len(self.trading_bot.execution_log)
        self.trading_bot.force_exit_all_positions("test_exit")
        
        # Verify all positions were closed
        self.assertEqual(len(self.trading_bot.orchestrator.active_positions), 0)
        
        # Verify exit actions were logged
        new_log_entries = len(self.trading_bot.execution_log) - initial_log_count
        self.assertEqual(new_log_entries, 2)  # Two exit actions


class TestExitLevelCalculation(unittest.TestCase):
    """Test exit level calculations for different confidence levels."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.position_manager = AggressivePositionManager()
    
    def test_high_confidence_exit_levels(self):
        """Test exit levels for high confidence signals."""
        signal = TradingSignal(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            confidence=0.95,
            strategy_name='test_strategy',
            timestamp=datetime.now(),
            metadata={}
        )
        
        entry_price = Decimal('50000')
        exit_levels = self.position_manager.calculate_exit_levels(signal, entry_price)
        
        # Should have stop loss, take profit, and trailing stop levels
        self.assertGreaterEqual(len(exit_levels), 3)
        
        # Find stop loss level
        stop_loss = next(level for level in exit_levels if level.trigger_type == ExitTrigger.STOP_LOSS)
        expected_stop = entry_price * Decimal('0.985')  # 1.5% stop for high confidence
        self.assertAlmostEqual(float(stop_loss.price), float(expected_stop), places=0)
        
        # Find take profit level
        take_profit = next(level for level in exit_levels if level.trigger_type == ExitTrigger.TAKE_PROFIT)
        expected_tp = entry_price * Decimal('1.04')  # 4% take profit for high confidence
        self.assertAlmostEqual(float(take_profit.price), float(expected_tp), places=0)
    
    def test_low_confidence_exit_levels(self):
        """Test exit levels for low confidence signals."""
        signal = TradingSignal(
            symbol='BTCUSD',
            action=SignalAction.BUY,
            confidence=0.82,
            strategy_name='test_strategy',
            timestamp=datetime.now(),
            metadata={}
        )
        
        entry_price = Decimal('50000')
        exit_levels = self.position_manager.calculate_exit_levels(signal, entry_price)
        
        # Find stop loss level
        stop_loss = next(level for level in exit_levels if level.trigger_type == ExitTrigger.STOP_LOSS)
        expected_stop = entry_price * Decimal('0.975')  # 2.5% stop for low confidence
        self.assertAlmostEqual(float(stop_loss.price), float(expected_stop), places=0)
        
        # Find take profit level
        take_profit = next(level for level in exit_levels if level.trigger_type == ExitTrigger.TAKE_PROFIT)
        expected_tp = entry_price * Decimal('1.06')  # 6% take profit for low confidence
        self.assertAlmostEqual(float(take_profit.price), float(expected_tp), places=0)


def run_anti_greed_tests():
    """Run all anti-greed mechanism tests."""
    print("Running Anti-Greed Trading System Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAntiGreedMechanisms))
    test_suite.addTest(unittest.makeSuite(TestPortfolioOrchestrator))
    test_suite.addTest(unittest.makeSuite(TestTradingBotIntegration))
    test_suite.addTest(unittest.makeSuite(TestExitLevelCalculation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("ANTI-GREED TEST RESULTS")
    print("=" * 50)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL ANTI-GREED MECHANISMS WORKING CORRECTLY!")
        print("🚫 NO GREEDINESS DETECTED IN SYSTEM")
    else:
        print("❌ Some anti-greed mechanisms need attention")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_anti_greed_tests()
    sys.exit(0 if success else 1)