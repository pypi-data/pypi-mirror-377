#!/usr/bin/env python3
"""
Risk Management System Example

This example demonstrates how to use the comprehensive risk management system
including RiskManager, PositionSizer, StopLossManager, and DrawdownMonitor.
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.risk.risk_manager import RiskManager, RiskConfig
from src.risk.position_sizer import SizingMethod
from src.risk.stop_loss_manager import StopLossType
from src.models.data_models import (
    MarketData, TradingSignal, Position, Order,
    SignalAction, OrderSide, OrderType, OrderStatus
)


def main():
    """Demonstrate risk management system usage."""
    print("=== Risk Management System Example ===\n")
    
    # 1. Initialize Risk Manager
    print("1. Initializing Risk Manager...")
    risk_config = RiskConfig(
        max_portfolio_risk_pct=0.02,  # 2% max risk per trade
        max_daily_loss_pct=0.05,      # 5% max daily loss
        max_drawdown_pct=0.10,        # 10% max drawdown
        max_position_size_pct=0.20,   # 20% max position size
        max_positions=10,             # Max 10 positions
        default_stop_loss_pct=0.02    # 2% default stop loss
    )
    
    risk_manager = RiskManager(risk_config)
    print(f"✓ Risk Manager initialized with config: {risk_config.__dict__}")
    
    # 2. Create sample data
    print("\n2. Creating sample market data and trading signal...")
    
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
    
    signal = TradingSignal(
        symbol="BTCUSDT",
        action=SignalAction.BUY,
        confidence=0.85,
        timestamp=datetime.now(),
        strategy_name="momentum_strategy",
        price=Decimal("50000")
    )
    
    portfolio_value = Decimal("100000")  # $100k portfolio
    current_positions = []
    
    print(f"✓ Market Data: {signal.symbol} @ ${market_data.close}")
    print(f"✓ Signal: {signal.action.value} with {signal.confidence:.1%} confidence")
    print(f"✓ Portfolio Value: ${portfolio_value:,}")
    
    # 3. Assess Trade Risk
    print("\n3. Assessing trade risk...")
    
    risk_assessment = risk_manager.assess_trade_risk(
        signal, market_data, portfolio_value, current_positions
    )
    
    print(f"✓ Risk Level: {risk_assessment.level.value}")
    print(f"✓ Risk Score: {risk_assessment.score:.3f}")
    print(f"✓ Max Position Size: ${risk_assessment.max_position_size:,.2f}")
    print(f"✓ Reasons: {risk_assessment.reasons}")
    print(f"✓ Recommendations: {risk_assessment.recommendations}")
    
    # 4. Position Sizing
    print("\n4. Calculating position sizes with different methods...")
    
    sizing_recommendation = risk_manager.position_sizer.get_sizing_recommendation(
        signal, market_data, portfolio_value, current_positions
    )
    
    print(f"✓ Recommended Method: {sizing_recommendation['recommended_method']}")
    print("✓ Position sizes by method:")
    for method, details in sizing_recommendation['all_methods'].items():
        if 'size' in details:
            size_pct = details['size_pct'] * 100
            print(f"   - {method}: ${details['size']:,.2f} ({size_pct:.2f}%)")
    
    # 5. Create and validate order
    print("\n5. Creating and validating order...")
    
    position_size = risk_assessment.max_position_size
    shares = position_size / market_data.close
    
    order = Order(
        id="example_order_1",
        symbol=signal.symbol,
        side=OrderSide.BUY,
        amount=shares,
        price=market_data.close,
        order_type=OrderType.LIMIT,
        status=OrderStatus.PENDING,
        timestamp=datetime.now(),
        exchange="binance"
    )
    
    is_valid, validation_reason = risk_manager.validate_order(
        order, portfolio_value, current_positions
    )
    
    print(f"✓ Order Valid: {is_valid}")
    print(f"✓ Validation Reason: {validation_reason}")
    print(f"✓ Order Details: {shares:.6f} shares @ ${order.price}")
    
    # 6. Simulate position and stop loss management
    print("\n6. Simulating position and stop loss management...")
    
    # Create a position (simulate order execution)
    position = Position(
        symbol=signal.symbol,
        size=shares,
        entry_price=market_data.close,
        current_price=market_data.close,
        timestamp=datetime.now(),
        exchange="binance",
        side=OrderSide.BUY
    )
    
    # Create stop loss
    stop_loss_order = risk_manager.stop_loss_manager.create_stop_loss(
        position, market_data, StopLossType.TRAILING
    )
    
    print(f"✓ Position Created: {position.size:.6f} {position.symbol}")
    print(f"✓ Stop Loss Created: {stop_loss_order.stop_type.value} @ ${stop_loss_order.stop_price}")
    
    # 7. Simulate price movement and risk updates
    print("\n7. Simulating price movement and risk updates...")
    
    # Simulate price increase
    new_market_data = MarketData(
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        open=Decimal("50000"),
        high=Decimal("52000"),
        low=Decimal("49500"),
        close=Decimal("51500"),  # 3% increase
        volume=Decimal("1200"),
        exchange="binance"
    )
    
    # Update position price
    position.current_price = new_market_data.close
    
    # Update stop loss
    stop_update = risk_manager.stop_loss_manager.update_stop_loss(position, new_market_data)
    print(f"✓ Stop Loss Update: {stop_update['action']}")
    print(f"✓ New Stop Price: ${stop_update['new_stop_price']:.2f}")
    
    # Update position risk
    position_risk = risk_manager.update_position_risk(position, new_market_data)
    print(f"✓ Position Risk Score: {position_risk['risk_score']:.3f}")
    print(f"✓ Position Recommendations: {position_risk['recommendations']}")
    
    # 8. Portfolio health check
    print("\n8. Checking portfolio health...")
    
    current_positions = [position]
    health = risk_manager.check_portfolio_health(portfolio_value, current_positions)
    
    print(f"✓ Health Level: {health['health_level']}")
    print(f"✓ Health Score: {health['health_score']:.3f}")
    print(f"✓ Portfolio Utilization: {health['portfolio_utilization_pct']:.2%}")
    print(f"✓ Unrealized P&L: ${health['total_unrealized_pnl']:,.2f}")
    print(f"✓ Warnings: {health['warnings']}")
    
    # 9. Drawdown monitoring
    print("\n9. Testing drawdown monitoring...")
    
    # Simulate a drawdown scenario
    drawdown_portfolio_value = Decimal("92000")  # 8% drawdown
    drawdown_status = risk_manager.drawdown_monitor.update_portfolio_value(drawdown_portfolio_value)
    
    print(f"✓ Drawdown Detected: {drawdown_status['current_drawdown_pct']:.2%}")
    print(f"✓ Drawdown Severity: {drawdown_status['severity']}")
    print(f"✓ Position Size Adjustment: {risk_manager.drawdown_monitor.get_position_size_adjustment(drawdown_status['current_drawdown_pct']):.2f}x")
    print(f"✓ Recommendations: {drawdown_status['recommendations']}")
    
    # 10. Risk summary
    print("\n10. Risk Management Summary...")
    
    risk_summary = risk_manager.get_risk_summary()
    print(f"✓ Configuration: {risk_summary['config']}")
    print(f"✓ Status: {risk_summary['status']}")
    print(f"✓ Components: {risk_summary['components']}")
    
    print("\n=== Risk Management Example Complete ===")
    print("\nKey Features Demonstrated:")
    print("• Comprehensive risk assessment")
    print("• Multiple position sizing methods")
    print("• Order validation")
    print("• Dynamic stop loss management")
    print("• Portfolio health monitoring")
    print("• Drawdown protection")
    print("• Real-time risk updates")


if __name__ == "__main__":
    main()