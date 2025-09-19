#!/usr/bin/env python3
"""
Example demonstrating the session management system for multi-market trading.

This example shows how to:
1. Create and configure market sessions
2. Check session status and market hours
3. Handle holidays and early close days
4. Coordinate multiple market sessions
5. Load configuration from YAML files
"""

import sys
import os
from datetime import datetime, time, timezone, date
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.markets.sessions import (
    SessionManager, SessionScheduler, MarketSession, HolidayCalendar,
    SessionStatus
)
from src.markets.types import MarketType


def create_sample_sessions():
    """Create sample market sessions for demonstration."""
    print("=== Creating Sample Market Sessions ===")
    
    # Create forex sessions
    london_session = MarketSession(
        name="london",
        market_type=MarketType.FOREX,
        timezone_name="Europe/London",
        open_time=time(8, 0),   # 8:00 AM UTC
        close_time=time(17, 0), # 5:00 PM UTC
        days_of_week={0, 1, 2, 3, 4}  # Monday to Friday
    )
    
    new_york_session = MarketSession(
        name="new_york",
        market_type=MarketType.FOREX,
        timezone_name="America/New_York",
        open_time=time(13, 0),  # 1:00 PM UTC
        close_time=time(22, 0), # 10:00 PM UTC
        days_of_week={0, 1, 2, 3, 4}
    )
    
    tokyo_session = MarketSession(
        name="tokyo",
        market_type=MarketType.FOREX,
        timezone_name="Asia/Tokyo",
        open_time=time(0, 0),   # 12:00 AM UTC
        close_time=time(9, 0),  # 9:00 AM UTC
        days_of_week={0, 1, 2, 3, 4}
    )
    
    # Create crypto session (24/7)
    crypto_session = MarketSession(
        name="global",
        market_type=MarketType.CRYPTO,
        timezone_name="UTC",
        open_time=time(0, 0),
        close_time=time(23, 59),
        days_of_week={0, 1, 2, 3, 4, 5, 6}  # All days
    )
    
    print(f"Created sessions:")
    for session in [london_session, new_york_session, tokyo_session, crypto_session]:
        print(f"  - {session.name}: {session.market_type.value} "
              f"({session.open_time} - {session.close_time})")
    
    return [london_session, new_york_session, tokyo_session, crypto_session]


def create_sample_holiday_calendar():
    """Create sample holiday calendar."""
    print("\n=== Creating Holiday Calendar ===")
    
    calendar = HolidayCalendar(market_type=MarketType.FOREX)
    
    # Add some holidays
    calendar.add_holiday(date(2024, 1, 1))   # New Year's Day
    calendar.add_holiday(date(2024, 12, 25)) # Christmas Day
    calendar.add_holiday(date(2024, 12, 26)) # Boxing Day
    
    # Add early close days
    calendar.add_early_close(date(2024, 12, 24), time(14, 0))  # Christmas Eve
    calendar.add_early_close(date(2024, 12, 31), time(18, 0))  # New Year's Eve
    
    print(f"Added {len(calendar.holidays)} holidays")
    print(f"Added {len(calendar.early_close_days)} early close days")
    
    return calendar


def demonstrate_session_scheduler():
    """Demonstrate session scheduler functionality."""
    print("\n=== Demonstrating Session Scheduler ===")
    
    # Create scheduler and add sessions
    scheduler = SessionScheduler()
    sessions = create_sample_sessions()
    holiday_calendar = create_sample_holiday_calendar()
    
    for session in sessions:
        scheduler.add_session(session)
    
    scheduler.add_holiday_calendar(holiday_calendar)
    
    # Test different times
    test_times = [
        datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),  # Monday 10:00 AM UTC (London open)
        datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc),  # Monday 3:00 PM UTC (London + NY overlap)
        datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc),  # Monday 8:00 PM UTC (NY open)
        datetime(2024, 1, 6, 12, 0, tzinfo=timezone.utc),  # Saturday 12:00 PM UTC (Weekend)
        datetime(2024, 12, 25, 12, 0, tzinfo=timezone.utc) # Christmas Day (Holiday)
    ]
    
    for test_time in test_times:
        print(f"\n--- Testing time: {test_time.strftime('%A, %Y-%m-%d %H:%M UTC')} ---")
        
        # Get active sessions
        active_sessions = scheduler.get_active_sessions(test_time)
        if active_sessions:
            print(f"Active sessions: {[s.session_name for s in active_sessions]}")
            
            # Check for overlaps
            overlaps = scheduler.get_session_overlaps(test_time)
            if overlaps:
                print(f"Session overlaps: {overlaps}")
        else:
            print("No active sessions")
        
        # Check market trading status
        for market_type in [MarketType.CRYPTO, MarketType.FOREX]:
            should_trade = scheduler.should_trade(market_type, test_time)
            print(f"{market_type.value.capitalize()} trading: {'✓' if should_trade else '✗'}")


def demonstrate_session_manager():
    """Demonstrate session manager with configuration loading."""
    print("\n=== Demonstrating Session Manager ===")
    
    # Check if config file exists
    config_path = "config/sessions.yaml"
    if not Path(config_path).exists():
        print(f"Configuration file not found: {config_path}")
        print("Creating session manager without configuration...")
        manager = SessionManager()
        
        # Manually add a session for demonstration
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
    else:
        print(f"Loading configuration from: {config_path}")
        manager = SessionManager(config_path)
    
    # Test current time
    current_time = datetime.now(timezone.utc)
    print(f"\nCurrent time: {current_time.strftime('%A, %Y-%m-%d %H:%M UTC')}")
    
    # Get active markets
    active_markets = manager.get_active_markets(current_time)
    print(f"Active markets: {[m.value for m in active_markets]}")
    
    # Check trading status for each market
    for market_type in [MarketType.CRYPTO, MarketType.FOREX]:
        should_trade = manager.should_trade(market_type, current_time)
        print(f"Should trade {market_type.value}: {'Yes' if should_trade else 'No'}")
        
        # Get market sessions
        market_sessions = manager.get_market_sessions(market_type, current_time)
        if market_sessions:
            print(f"{market_type.value.capitalize()} sessions:")
            for session_name, session_info in market_sessions.items():
                status_icon = "🟢" if session_info.is_active else "🔴"
                print(f"  {status_icon} {session_name}: {session_info.status.value}")
                
                if session_info.next_open:
                    print(f"    Next open: {session_info.next_open.strftime('%Y-%m-%d %H:%M UTC')}")
                if session_info.next_close:
                    print(f"    Next close: {session_info.next_close.strftime('%Y-%m-%d %H:%M UTC')}")


def demonstrate_holiday_handling():
    """Demonstrate holiday and early close handling."""
    print("\n=== Demonstrating Holiday Handling ===")
    
    # Create session and holiday calendar
    london_session = MarketSession(
        name="london",
        market_type=MarketType.FOREX,
        timezone_name="Europe/London",
        open_time=time(8, 0),
        close_time=time(17, 0),
        days_of_week={0, 1, 2, 3, 4}
    )
    
    holiday_calendar = HolidayCalendar(market_type=MarketType.FOREX)
    holiday_calendar.add_holiday(date(2024, 12, 25))  # Christmas
    holiday_calendar.add_early_close(date(2024, 12, 24), time(14, 0))  # Christmas Eve
    
    # Test different scenarios
    test_scenarios = [
        (datetime(2024, 12, 24, 12, 0, tzinfo=timezone.utc), "Christmas Eve (early close day)"),
        (datetime(2024, 12, 25, 12, 0, tzinfo=timezone.utc), "Christmas Day (holiday)"),
        (datetime(2024, 12, 26, 12, 0, tzinfo=timezone.utc), "Day after Christmas (normal day)")
    ]
    
    for test_time, description in test_scenarios:
        print(f"\n--- {description} ---")
        session_info = london_session.is_session_active(test_time, holiday_calendar)
        
        print(f"Session active: {'Yes' if session_info.is_active else 'No'}")
        print(f"Status: {session_info.status.value}")
        
        if session_info.next_open:
            print(f"Next open: {session_info.next_open.strftime('%Y-%m-%d %H:%M')}")


def main():
    """Main demonstration function."""
    print("Multi-Market Session Management System Demo")
    print("=" * 50)
    
    try:
        # Run demonstrations
        demonstrate_session_scheduler()
        demonstrate_session_manager()
        demonstrate_holiday_handling()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()