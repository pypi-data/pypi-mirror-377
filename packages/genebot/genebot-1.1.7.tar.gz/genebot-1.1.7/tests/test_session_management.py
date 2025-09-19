"""
Unit tests for market session management system.
"""

import pytest
from datetime import datetime, time, timezone, timedelta, date
from unittest.mock import patch, mock_open
import yaml
from pathlib import Path

from src.markets.sessions import (
    SessionManager, SessionScheduler, MarketSession, HolidayCalendar,
    SessionInfo, SessionStatus
)
from src.markets.types import MarketType


class TestMarketSession:
    """Test cases for MarketSession class."""
    
    def test_market_session_creation(self):
        """Test creating a market session."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        assert session.name == "london"
        assert session.market_type == MarketType.FOREX
        assert session.timezone_name == "Europe/London"
        assert session.open_time == time(8, 0)
        assert session.close_time == time(17, 0)
        assert session.days_of_week == {0, 1, 2, 3, 4}
    
    def test_market_session_validation(self):
        """Test market session validation."""
        # Test empty name
        with pytest.raises(ValueError, match="Session name cannot be empty"):
            MarketSession(
                name="",
                market_type=MarketType.FOREX,
                timezone_name="UTC",
                open_time=time(8, 0),
                close_time=time(17, 0)
            )
        
        # Test invalid days of week
        with pytest.raises(ValueError, match="Days of week must be between"):
            MarketSession(
                name="test",
                market_type=MarketType.FOREX,
                timezone_name="UTC",
                open_time=time(8, 0),
                close_time=time(17, 0),
                days_of_week={-1, 7}
            )
    
    def test_is_trading_day(self):
        """Test trading day detection."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Monday (0)
        monday = datetime(2024, 1, 1, tzinfo=timezone.utc)  # This is a Monday
        assert session.is_trading_day(monday)
        
        # Saturday (5)
        saturday = datetime(2024, 1, 6, tzinfo=timezone.utc)  # This is a Saturday
        assert not session.is_trading_day(saturday)
        
        # Sunday (6)
        sunday = datetime(2024, 1, 7, tzinfo=timezone.utc)  # This is a Sunday
        assert not session.is_trading_day(sunday)
    
    def test_get_session_times(self):
        """Test getting session times for a date."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0)
        )
        
        test_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        open_time, close_time = session.get_session_times(test_date)
        
        assert open_time == datetime(2024, 1, 1, 8, 0, tzinfo=timezone.utc)
        assert close_time == datetime(2024, 1, 1, 17, 0, tzinfo=timezone.utc)
    
    def test_get_session_times_overnight(self):
        """Test getting session times for overnight sessions."""
        session = MarketSession(
            name="sydney",
            market_type=MarketType.FOREX,
            timezone_name="Australia/Sydney",
            open_time=time(22, 0),
            close_time=time(7, 0)  # Next day
        )
        
        test_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        open_time, close_time = session.get_session_times(test_date)
        
        assert open_time == datetime(2024, 1, 1, 22, 0, tzinfo=timezone.utc)
        assert close_time == datetime(2024, 1, 2, 7, 0, tzinfo=timezone.utc)  # Next day
    
    def test_is_session_active_open(self):
        """Test session active during trading hours."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Monday at 12:00 (during trading hours)
        current_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday
        session_info = session.is_session_active(current_time)
        
        assert session_info.is_active
        assert session_info.status == SessionStatus.OPEN
        assert session_info.session_name == "london"
        assert session_info.next_close is not None
        assert session_info.time_to_close is not None
    
    def test_is_session_active_closed_before_open(self):
        """Test session closed before opening."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Monday at 6:00 (before opening)
        current_time = datetime(2024, 1, 1, 6, 0, tzinfo=timezone.utc)  # Monday
        session_info = session.is_session_active(current_time)
        
        assert not session_info.is_active
        assert session_info.status == SessionStatus.CLOSED
        assert session_info.next_open is not None
        assert session_info.time_to_open is not None
    
    def test_is_session_active_closed_after_close(self):
        """Test session closed after closing."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Monday at 19:00 (after closing)
        current_time = datetime(2024, 1, 1, 19, 0, tzinfo=timezone.utc)  # Monday
        session_info = session.is_session_active(current_time)
        
        assert not session_info.is_active
        assert session_info.status == SessionStatus.CLOSED
        assert session_info.next_open is not None
        assert session_info.time_to_open is not None
    
    def test_is_session_active_weekend(self):
        """Test session closed on weekend."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Saturday at 12:00
        current_time = datetime(2024, 1, 6, 12, 0, tzinfo=timezone.utc)  # Saturday
        session_info = session.is_session_active(current_time)
        
        assert not session_info.is_active
        assert session_info.status == SessionStatus.CLOSED
        assert session_info.next_open is not None
    
    def test_is_session_active_holiday(self):
        """Test session closed on holiday."""
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        
        # Create holiday calendar
        holiday_calendar = HolidayCalendar(market_type=MarketType.FOREX)
        holiday_calendar.add_holiday(date(2024, 1, 1))
        
        # Monday (holiday) at 12:00
        current_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday, New Year's Day
        session_info = session.is_session_active(current_time, holiday_calendar)
        
        assert not session_info.is_active
        assert session_info.status == SessionStatus.HOLIDAY
        assert session_info.next_open is not None


class TestHolidayCalendar:
    """Test cases for HolidayCalendar class."""
    
    def test_holiday_calendar_creation(self):
        """Test creating a holiday calendar."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        
        assert calendar.market_type == MarketType.FOREX
        assert len(calendar.holidays) == 0
        assert len(calendar.early_close_days) == 0
    
    def test_add_holiday(self):
        """Test adding holidays."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        
        # Add holiday as date
        holiday_date = date(2024, 1, 1)
        calendar.add_holiday(holiday_date)
        
        # Add holiday as datetime
        holiday_datetime = datetime(2024, 12, 25, tzinfo=timezone.utc)
        calendar.add_holiday(holiday_datetime)
        
        assert len(calendar.holidays) == 2
        assert holiday_date in calendar.holidays
        assert holiday_datetime.date() in calendar.holidays
    
    def test_add_early_close(self):
        """Test adding early close days."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        
        early_date = date(2024, 12, 24)
        early_time = time(14, 0)
        calendar.add_early_close(early_date, early_time)
        
        assert len(calendar.early_close_days) == 1
        assert calendar.early_close_days[early_date] == early_time
    
    def test_is_holiday(self):
        """Test holiday detection."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        holiday_date = date(2024, 1, 1)
        calendar.add_holiday(holiday_date)
        
        assert calendar.is_holiday(holiday_date)
        assert calendar.is_holiday(datetime(2024, 1, 1, tzinfo=timezone.utc))
        assert not calendar.is_holiday(date(2024, 1, 2))
    
    def test_is_early_close(self):
        """Test early close detection."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        early_date = date(2024, 12, 24)
        early_time = time(14, 0)
        calendar.add_early_close(early_date, early_time)
        
        assert calendar.is_early_close(early_date)
        assert calendar.is_early_close(datetime(2024, 12, 24, tzinfo=timezone.utc))
        assert not calendar.is_early_close(date(2024, 12, 25))
    
    def test_get_early_close_time(self):
        """Test getting early close time."""
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        early_date = date(2024, 12, 24)
        early_time = time(14, 0)
        calendar.add_early_close(early_date, early_time)
        
        assert calendar.get_early_close_time(early_date) == early_time
        assert calendar.get_early_close_time(datetime(2024, 12, 24, tzinfo=timezone.utc)) == early_time
        assert calendar.get_early_close_time(date(2024, 12, 25)) is None
    
    def test_from_config(self):
        """Test creating holiday calendar from configuration."""
        config = {
            'holidays': ['2024-01-01', '2024-12-25'],
            'early_close': [
                {'date': '2024-12-24', 'time': '14:00'},
                {'date': '2024-12-31', 'time': '18:00'}
            ]
        }
        
        calendar = HolidayCalendar.from_config(MarketType.FOREX, config)
        
        assert calendar.market_type == MarketType.FOREX
        assert len(calendar.holidays) == 2
        assert date(2024, 1, 1) in calendar.holidays
        assert date(2024, 12, 25) in calendar.holidays
        
        assert len(calendar.early_close_days) == 2
        assert calendar.early_close_days[date(2024, 12, 24)] == time(14, 0)
        assert calendar.early_close_days[date(2024, 12, 31)] == time(18, 0)
    
    def test_from_config_invalid_dates(self):
        """Test handling invalid dates in configuration."""
        config = {
            'holidays': ['invalid-date', '2024-01-01'],
            'early_close': [
                {'date': 'invalid-date', 'time': '14:00'},
                {'date': '2024-12-24', 'time': 'invalid-time'}
            ]
        }
        
        # Should not raise exception, but log warnings
        calendar = HolidayCalendar.from_config(MarketType.FOREX, config)
        
        # Only valid entries should be added
        assert len(calendar.holidays) == 1
        assert date(2024, 1, 1) in calendar.holidays
        assert len(calendar.early_close_days) == 0


class TestSessionScheduler:
    """Test cases for SessionScheduler class."""
    
    def test_session_scheduler_creation(self):
        """Test creating a session scheduler."""
        scheduler = SessionScheduler()
        
        assert len(scheduler.sessions) == 0
        assert len(scheduler.holiday_calendars) == 0
    
    def test_add_session(self):
        """Test adding sessions to scheduler."""
        scheduler = SessionScheduler()
        
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0)
        )
        
        scheduler.add_session(session)
        
        assert len(scheduler.sessions) == 1
        assert "london" in scheduler.sessions
        assert scheduler.sessions["london"] == session
    
    def test_add_holiday_calendar(self):
        """Test adding holiday calendar to scheduler."""
        scheduler = SessionScheduler()
        
        calendar = HolidayCalendar(market_type=MarketType.FOREX)
        scheduler.add_holiday_calendar(calendar)
        
        assert len(scheduler.holiday_calendars) == 1
        assert MarketType.FOREX in scheduler.holiday_calendars
        assert scheduler.holiday_calendars[MarketType.FOREX] == calendar
    
    def test_get_session_status(self):
        """Test getting session status."""
        scheduler = SessionScheduler()
        
        session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}  # Mon-Fri
        )
        scheduler.add_session(session)
        
        # Test during trading hours
        current_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        session_info = scheduler.get_session_status("london", current_time)
        
        assert session_info is not None
        assert session_info.is_active
        assert session_info.session_name == "london"
        
        # Test non-existent session
        assert scheduler.get_session_status("nonexistent") is None
    
    def test_get_active_sessions(self):
        """Test getting active sessions."""
        scheduler = SessionScheduler()
        
        # Add London session (8-17 UTC)
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(london_session)
        
        # Add New York session (13-22 UTC)
        ny_session = MarketSession(
            name="new_york",
            market_type=MarketType.FOREX,
            timezone_name="America/New_York",
            open_time=time(13, 0),
            close_time=time(22, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(ny_session)
        
        # Test during overlap (15:00 UTC on Monday)
        current_time = datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc)  # Monday at 15:00
        active_sessions = scheduler.get_active_sessions(current_time)
        
        assert len(active_sessions) == 2
        session_names = [info.session_name for info in active_sessions]
        assert "london" in session_names
        assert "new_york" in session_names
    
    def test_get_session_overlaps(self):
        """Test getting session overlaps."""
        scheduler = SessionScheduler()
        
        # Add overlapping sessions
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(london_session)
        
        ny_session = MarketSession(
            name="new_york",
            market_type=MarketType.FOREX,
            timezone_name="America/New_York",
            open_time=time(13, 0),
            close_time=time(22, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(ny_session)
        
        # Test during overlap
        current_time = datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc)  # Monday at 15:00
        overlaps = scheduler.get_session_overlaps(current_time)
        
        assert len(overlaps) == 1
        assert ("london", "new_york") in overlaps or ("new_york", "london") in overlaps
    
    def test_get_market_status(self):
        """Test getting market status."""
        scheduler = SessionScheduler()
        
        # Add forex sessions
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(london_session)
        
        # Add crypto session
        crypto_session = MarketSession(
            name="global",
            market_type=MarketType.CRYPTO,
            timezone_name="UTC",
            open_time=time(0, 0),
            close_time=time(23, 59),
            days_of_week={0, 1, 2, 3, 4, 5, 6}
        )
        scheduler.add_session(crypto_session)
        
        current_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        
        # Test forex market status
        forex_status = scheduler.get_market_status(MarketType.FOREX, current_time)
        assert len(forex_status) == 1
        assert "london" in forex_status
        
        # Test crypto market status
        crypto_status = scheduler.get_market_status(MarketType.CRYPTO, current_time)
        assert len(crypto_status) == 1
        assert "global" in crypto_status
    
    def test_should_trade_crypto(self):
        """Test should_trade for crypto (always true)."""
        scheduler = SessionScheduler()
        
        # Crypto should always be tradeable
        assert scheduler.should_trade(MarketType.CRYPTO)
        
        # Even on weekends
        weekend_time = datetime(2024, 1, 6, 12, 0, tzinfo=timezone.utc)  # Saturday
        assert scheduler.should_trade(MarketType.CRYPTO, weekend_time)
    
    def test_should_trade_forex(self):
        """Test should_trade for forex."""
        scheduler = SessionScheduler()
        
        # Add forex session
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        scheduler.add_session(london_session)
        
        # During trading hours
        trading_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        assert scheduler.should_trade(MarketType.FOREX, trading_time)
        
        # Outside trading hours
        non_trading_time = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)  # Monday at 20:00
        assert not scheduler.should_trade(MarketType.FOREX, non_trading_time)
        
        # Weekend
        weekend_time = datetime(2024, 1, 6, 12, 0, tzinfo=timezone.utc)  # Saturday
        assert not scheduler.should_trade(MarketType.FOREX, weekend_time)


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def test_session_manager_creation(self):
        """Test creating a session manager."""
        manager = SessionManager()
        
        assert manager.scheduler is not None
        assert manager._config_path is None
    
    def test_session_manager_with_config(self):
        """Test creating session manager with config path."""
        config_path = "test_config.yaml"
        
        with patch.object(SessionManager, 'load_configuration') as mock_load:
            manager = SessionManager(config_path)
            mock_load.assert_called_once_with(config_path)
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists")
    @patch("yaml.safe_load")
    def test_load_configuration(self, mock_yaml_load, mock_exists, mock_file):
        """Test loading configuration from YAML file."""
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            'sessions': {
                'forex': {
                    'london': {
                        'open': '08:00',
                        'close': '17:00',
                        'timezone': 'Europe/London',
                        'days': [0, 1, 2, 3, 4]
                    }
                }
            },
            'holidays': {
                'forex': {
                    'holidays': ['2024-01-01'],
                    'early_close': []
                }
            }
        }
        
        manager = SessionManager()
        manager.load_configuration("test_config.yaml")
        
        # Check that session was loaded
        assert len(manager.scheduler.sessions) == 1
        assert "london" in manager.scheduler.sessions
        
        # Check that holiday calendar was loaded
        assert MarketType.FOREX in manager.scheduler.holiday_calendars
    
    @patch("pathlib.Path.exists")
    def test_load_configuration_file_not_found(self, mock_exists):
        """Test loading configuration when file doesn't exist."""
        mock_exists.return_value = False
        
        manager = SessionManager()
        # Should not raise exception, just log warning
        manager.load_configuration("nonexistent.yaml")
        
        assert len(manager.scheduler.sessions) == 0
    
    def test_get_active_markets(self):
        """Test getting active markets."""
        manager = SessionManager()
        
        # Add forex session
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
        
        # During forex trading hours
        trading_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        active_markets = manager.get_active_markets(trading_time)
        
        # Should include both crypto (always active) and forex
        assert MarketType.CRYPTO in active_markets
        assert MarketType.FOREX in active_markets
        
        # Outside forex trading hours
        non_trading_time = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)  # Monday at 20:00
        active_markets = manager.get_active_markets(non_trading_time)
        
        # Should only include crypto
        assert MarketType.CRYPTO in active_markets
        assert MarketType.FOREX not in active_markets
    
    def test_should_trade(self):
        """Test should_trade method."""
        manager = SessionManager()
        
        # Add forex session
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
        
        trading_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        
        # Crypto should always be tradeable
        assert manager.should_trade(MarketType.CRYPTO, trading_time)
        
        # Forex should be tradeable during session hours
        assert manager.should_trade(MarketType.FOREX, trading_time)
        
        # Forex should not be tradeable outside session hours
        non_trading_time = datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc)  # Monday at 20:00
        assert not manager.should_trade(MarketType.FOREX, non_trading_time)
    
    def test_get_session_info(self):
        """Test getting session information."""
        manager = SessionManager()
        
        # Add session
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
        
        trading_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        session_info = manager.get_session_info("london", trading_time)
        
        assert session_info is not None
        assert session_info.session_name == "london"
        assert session_info.is_active
        
        # Test non-existent session
        assert manager.get_session_info("nonexistent") is None
    
    def test_get_market_sessions(self):
        """Test getting market sessions."""
        manager = SessionManager()
        
        # Add forex sessions
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
        
        ny_session = MarketSession(
            name="new_york",
            market_type=MarketType.FOREX,
            timezone_name="America/New_York",
            open_time=time(13, 0),
            close_time=time(22, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(ny_session)
        
        trading_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)  # Monday at 12:00
        forex_sessions = manager.get_market_sessions(MarketType.FOREX, trading_time)
        
        assert len(forex_sessions) == 2
        assert "london" in forex_sessions
        assert "new_york" in forex_sessions
    
    def test_get_session_overlaps(self):
        """Test getting session overlaps."""
        manager = SessionManager()
        
        # Add overlapping sessions
        london_session = MarketSession(
            name="london",
            market_type=MarketType.FOREX,
            timezone_name="Europe/London",
            open_time=time(8, 0),
            close_time=time(17, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(london_session)
        
        ny_session = MarketSession(
            name="new_york",
            market_type=MarketType.FOREX,
            timezone_name="America/New_York",
            open_time=time(13, 0),
            close_time=time(22, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        manager.scheduler.add_session(ny_session)
        
        # During overlap
        overlap_time = datetime(2024, 1, 1, 15, 0, tzinfo=timezone.utc)  # Monday at 15:00
        overlaps = manager.get_session_overlaps(overlap_time)
        
        assert len(overlaps) == 1
        assert ("london", "new_york") in overlaps or ("new_york", "london") in overlaps


if __name__ == "__main__":
    pytest.main([__file__])