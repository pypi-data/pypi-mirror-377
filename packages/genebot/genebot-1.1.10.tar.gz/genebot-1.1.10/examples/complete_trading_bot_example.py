#!/usr/bin/env python3
"""
Complete Trading Bot Example - All Strategies with Aggressive Exit Management

This example demonstrates the complete trading bot orchestrator that:
1. Uses ALL available strategies simultaneously
2. Implements aggressive exit strategies to avoid greediness
3. Manages risk and position sizing automatically
4. Provides comprehensive performance tracking
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trading_bot_orchestrator import TradingBotOrchestrator
from src.models.data_models import MarketData


def create_realistic_trading_data(symbol: str = "BTCUSD", num_points: int = 300) -> list[MarketData]:
    """
    Create realistic market data for comprehensive trading bot testing.
    
    Args:
        symbol: Trading symbol
        num_points: Number of data points to generate
        
    Returns:
        List of MarketData objects with realistic trading patterns
    """
    market_data = []
    base_time = datetime.now() - timedelta(minutes=num_points)
    base_price = 50000.0
    
    # Create multiple market phases for comprehensive testing
    trend_up_phase = num_points // 5      # Strong uptrend
    consolidation_phase = num_points // 5  # Sideways consolidation
    trend_down_phase = num_points // 5     # Strong downtrend
    volatile_phase = num_points // 5       # High volatility
    recovery_phase = num_points - (trend_up_phase + consolidation_phase + trend_down_phase + volatile_phase)
    
    prices = []
    volumes = []
    
    # Phase 1: Strong uptrend (momentum strategies should trigger)
    current_price = base_price
    for i in range(trend_up_phase):
        # Strong upward momentum with increasing volume
        momentum = 15 + (i * 0.5)  # Accelerating momentum
        noise = np.random.normal(0, 20)
        current_price += momentum + noise
        
        volume = 1200 + (i * 10) + np.random.normal(0, 100)  # Increasing volume
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Phase 2: Consolidation (mean reversion should trigger)
    consolidation_center = current_price
    for i in range(consolidation_phase):
        # Tight range with mean reversion opportunities
        range_size = 200 - (i * 2)  # Tightening range
        oscillation = np.sin(i * 0.4) * range_size
        noise = np.random.normal(0, 15)
        
        current_price = consolidation_center + oscillation + noise
        volume = 800 + np.random.normal(0, 80)  # Lower volume in consolidation
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Phase 3: Strong downtrend (reversal strategies should trigger)
    for i in range(trend_down_phase):
        # Strong downward momentum
        momentum = -(12 + (i * 0.3))  # Accelerating downward momentum
        noise = np.random.normal(0, 25)
        current_price += momentum + noise
        
        volume = 1400 + (i * 8) + np.random.normal(0, 120)  # High volume on decline
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Phase 4: High volatility (ATR strategies should trigger)
    volatile_center = current_price
    for i in range(volatile_phase):
        # Extreme volatility with large swings
        direction = np.random.choice([-1, 1])
        volatility = np.random.exponential(80) * direction
        noise = np.random.normal(0, 40)
        
        current_price = volatile_center + volatility + noise
        volume = 1800 + np.random.normal(0, 200)  # Very high volume
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
        
        # Update center occasionally
        if i % 10 == 0:
            volatile_center = current_price
    
    # Phase 5: Recovery (multi-indicator confluence should trigger)
    for i in range(recovery_phase):
        # Gradual recovery with good momentum
        recovery_momentum = 8 + np.sin(i * 0.2) * 5
        noise = np.random.normal(0, 18)
        current_price += recovery_momentum + noise
        
        volume = 1000 + (i * 3) + np.random.normal(0, 90)
        
        prices.append(current_price)
        volumes.append(max(volume, 100))
    
    # Create MarketData objects with realistic OHLC
    for i, (price, volume) in enumerate(zip(prices, volumes)):
        # Determine volatility based on phase
        if i < trend_up_phase:
            volatility_factor = 0.008  # 0.8% volatility in uptrend
        elif i < trend_up_phase + consolidation_phase:
            volatility_factor = 0.004  # 0.4% volatility in consolidation
        elif i < trend_up_phase + consolidation_phase + trend_down_phase:
            volatility_factor = 0.012  # 1.2% volatility in downtrend
        elif i < trend_up_phase + consolidation_phase + trend_down_phase + volatile_phase:
            volatility_factor = 0.025  # 2.5% volatility in volatile phase
        else:
            volatility_factor = 0.010  # 1.0% volatility in recovery
        
        # Create realistic OHLC
        open_price = price + np.random.normal(0, price * volatility_factor * 0.2)
        
        high_offset = abs(np.random.normal(0, price * volatility_factor))
        low_offset = abs(np.random.normal(0, price * volatility_factor))
        
        high_price = max(open_price, price) + high_offset
        low_price = min(open_price, price) - low_offset
        
        data = MarketData(
            symbol=symbol,
            timestamp=base_time + timedelta(minutes=i),
            open=Decimal(str(round(open_price, 2))),
            high=Decimal(str(round(high_price, 2))),
            low=Decimal(str(round(low_price, 2))),
            close=Decimal(str(round(price, 2))),
            volume=Decimal(str(round(volume, 2))),
            exchange="complete_trading_bot"
        )
        market_data.append(data)
    
    return market_data


def demonstrate_complete_trading_bot():
    """Demonstrate the complete trading bot with all strategies."""
    print("=== Complete Trading Bot Demonstration ===")
    print("This bot uses ALL strategies simultaneously with aggressive exit management")
    print()
    
    # Initialize trading bot with $100,000 capital
    bot = TradingBotOrchestrator(initial_capital=Decimal('100000'))
    
    print(f"Initial Capital: ${float(bot.initial_capital):,.2f}")
    print(f"Risk Limits:")
    print(f"  - Max Portfolio Risk: {bot.risk_limits.max_portfolio_risk*100:.1f}% per trade")
    print(f"  - Max Daily Loss: {bot.risk_limits.max_daily_loss*100:.1f}%")
    print(f"  - Max Positions: {bot.risk_limits.max_positions}")
    print(f"  - Max Position Size: {bot.risk_limits.max_position_size*100:.1f}%")
    print()
    
    # Start trading bot
    bot.start_trading()
    
    # Get strategy status
    strategy_status = bot.strategy_engine.get_strategy_status()
    print(f"Active Strategies: {len(strategy_status)}")
    for name, status in strategy_status.items():
        print(f"  - {name}: {'ACTIVE' if status['active'] else 'INACTIVE'}")
    print()
    
    # Create comprehensive market data
    print("Generating realistic market data with multiple phases...")
    market_data = create_realistic_trading_data("BTCUSD", 400)
    print(f"Created {len(market_data)} data points")
    print(f"Price range: ${float(market_data[0].close):,.2f} - ${float(market_data[-1].close):,.2f}")
    print(f"Time range: {market_data[0].timestamp} to {market_data[-1].timestamp}")
    print()
    
    # Process market data in real-time simulation
    print("Starting real-time trading simulation...")
    print("=" * 80)
    
    total_signals = 0
    total_entries = 0
    total_exits = 0
    
    # Process data in chunks to simulate real-time trading
    chunk_size = 20
    for chunk_start in range(100, len(market_data), chunk_size):  # Start after warmup period
        chunk_end = min(chunk_start + chunk_size, len(market_data))
        data_slice = market_data[:chunk_end]
        
        # Process through trading bot
        result = bot.process_market_data(data_slice)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            continue
        
        # Display results if there's activity
        current_time = result['timestamp']
        current_price = result['current_price']
        
        if (result['signals_received'] > 0 or result['entry_actions'] or 
            result['exit_actions'] or result['risk_actions']):
            
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Price: ${current_price:,.2f}")
            
            if result['signals_received'] > 0:
                print(f"  📊 Signals received: {result['signals_received']}")
                total_signals += result['signals_received']
            
            if result['entry_actions']:
                for action in result['entry_actions']:
                    print(f"  🟢 ENTRY: {action['side']} {action['symbol']} @ ${action['price']:,.2f}")
                    print(f"      Strategy: {action['strategy']} | Confidence: {action['confidence']:.1%}")
                    print(f"      Size: {action['size']:.4f} | Stop: ${action['stop_loss']:,.2f} | Target: ${action['take_profit']:,.2f}")
                total_entries += len(result['entry_actions'])
            
            if result['exit_actions']:
                for action in result['exit_actions']:
                    pnl_color = "🟢" if action['pnl'] > 0 else "🔴"
                    print(f"  {pnl_color} EXIT: {action['side']} {action['symbol']} @ ${action['exit_price']:,.2f}")
                    print(f"      Reason: {action['reason']} | P&L: ${action['pnl']:,.2f}")
                    print(f"      Hold time: {action['hold_time']} | Strategy: {action['strategy']}")
                total_exits += len(result['exit_actions'])
            
            if result['risk_actions']:
                for action in result['risk_actions']:
                    print(f"  ⚠️  RISK: {action['action']}")
            
            # Show current status
            print(f"  💼 Portfolio: ${result['portfolio_value']:,.2f} | Daily P&L: ${result['daily_pnl']:,.2f}")
            print(f"  📈 Open Positions: {result['open_positions']} | Total P&L: ${result['total_pnl']:,.2f}")
        
        # Brief pause to simulate real-time
        time.sleep(0.1)
    
    print("\n" + "=" * 80)
    print("Trading simulation completed!")
    print()
    
    # Get final performance summary
    performance = bot.get_performance_summary()
    
    print("=== FINAL PERFORMANCE SUMMARY ===")
    print(f"Total Trades: {performance['total_trades']}")
    print(f"Winning Trades: {performance['winning_trades']}")
    print(f"Losing Trades: {performance['losing_trades']}")
    print(f"Win Rate: {performance['win_rate']:.1%}")
    print(f"Profit Factor: {performance['profit_factor']:.2f}")
    print()
    
    print(f"Average Win: ${performance['average_win']:,.2f}")
    print(f"Average Loss: ${performance['average_loss']:,.2f}")
    print(f"Total P&L: ${performance['total_pnl']:,.2f}")
    print(f"Return: {performance['return_percentage']:.2f}%")
    print()
    
    print(f"Final Capital: ${performance['current_capital']:,.2f}")
    print(f"Open Positions: {performance['open_positions']}")
    print()
    
    # Strategy performance breakdown
    print("=== STRATEGY PERFORMANCE ===")
    strategy_perf = performance['strategy_performance']
    if strategy_perf:
        for strategy, stats in strategy_perf.items():
            print(f"{strategy}:")
            print(f"  Trades: {stats['trades']} | Win Rate: {stats['win_rate']:.1%}")
            print(f"  P&L: ${stats['total_pnl']:,.2f}")
    else:
        print("No completed trades to analyze")
    print()
    
    # Simulation summary
    print("=== SIMULATION SUMMARY ===")
    print(f"Total Signals Generated: {total_signals}")
    print(f"Total Entries: {total_entries}")
    print(f"Total Exits: {total_exits}")
    print(f"Signal-to-Entry Ratio: {(total_entries/total_signals*100):.1f}%" if total_signals > 0 else "N/A")
    print()
    
    # Stop trading bot
    bot.stop_trading()
    
    print("🎯 Key Features Demonstrated:")
    print("✓ All 7 strategies running simultaneously")
    print("✓ Aggressive exit management (no greediness)")
    print("✓ Dynamic position sizing based on confidence")
    print("✓ Multiple exit conditions (stop loss, take profit, trailing stop)")
    print("✓ Profit protection (exits when profit drops from peak)")
    print("✓ Time-based exits (no holding positions too long)")
    print("✓ Risk management (daily loss limits, portfolio heat)")
    print("✓ Real-time performance tracking")
    print()
    
    return bot, performance


def demonstrate_aggressive_exit_features():
    """Demonstrate the aggressive exit features in detail."""
    print("=== AGGRESSIVE EXIT STRATEGY FEATURES ===")
    print()
    
    print("1. IMMEDIATE EXITS (No Greediness):")
    print("   • Stop Loss: Immediate exit when loss threshold hit")
    print("   • Take Profit: Immediate exit when profit target reached")
    print("   • Trailing Stop: Protects profits as they grow")
    print()
    
    print("2. PROFIT PROTECTION (Anti-Greed Mechanism):")
    print("   • Tracks maximum profit achieved during trade")
    print("   • Exits if profit drops 50% from peak")
    print("   • Prevents giving back large gains")
    print()
    
    print("3. TIME-BASED EXITS:")
    print("   • High confidence trades: Max 12 hours")
    print("   • Normal confidence trades: Max 24 hours")
    print("   • Prevents indefinite holding")
    print()
    
    print("4. RISK MANAGEMENT EXITS:")
    print("   • Emergency exit at 4% loss")
    print("   • Daily loss limit: 5% of capital")
    print("   • Portfolio heat management")
    print()
    
    print("5. DYNAMIC POSITION SIZING:")
    print("   • Higher confidence = Larger position")
    print("   • Risk-based sizing (2% portfolio risk per trade)")
    print("   • Maximum 10% of capital per position")
    print()


def main():
    """Main demonstration function."""
    print("Complete Trading Bot with All Strategies")
    print("=" * 60)
    print()
    
    # Demonstrate aggressive exit features
    demonstrate_aggressive_exit_features()
    
    # Run complete trading bot demonstration
    bot, performance = demonstrate_complete_trading_bot()
    
    print("=" * 60)
    print("COMPLETE TRADING BOT DEMONSTRATION FINISHED!")
    print()
    print("This trading bot demonstrates:")
    print("• Simultaneous use of ALL 7 advanced strategies")
    print("• Aggressive exit management to avoid greediness")
    print("• Comprehensive risk management")
    print("• Real-time performance tracking")
    print("• High-probability signal filtering")
    print()
    print("The bot is designed to:")
    print("• Enter positions only on high-confidence signals (80%+)")
    print("• Exit quickly to protect profits (no greediness)")
    print("• Manage risk aggressively (2% max risk per trade)")
    print("• Adapt position sizes based on signal confidence")
    print("• Track performance across all strategies")


if __name__ == "__main__":
    main()