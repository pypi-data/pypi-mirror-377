"""Unit tests for database connection utilities."""

import pytest
import os
from unittest.mock import patch
from sqlalchemy.orm import Session

from src.database.connection import (
    get_database_url,
    create_engine_from_url,
    create_session,
    DatabaseManager,
)
from src.models.database_models import MarketDataModel


class TestDatabaseConnection:
    """Test cases for database connection utilities."""

    def test_get_database_url_default(self):
        """Test getting default database URL."""
        with patch.dict(os.environ, {}, clear=True):
            url = get_database_url()
            assert url == "sqlite:///trading_bot.db"

    def test_get_database_url_from_env(self):
        """Test getting database URL from environment variable."""
        test_url = "postgresql://user:pass@localhost/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": test_url}):
            url = get_database_url()
            assert url == test_url

    def test_create_engine_sqlite(self):
        """Test creating SQLite engine."""
        engine = create_engine_from_url("sqlite:///:memory:")
        assert engine is not None
        assert "sqlite" in str(engine.url)

    def test_create_engine_postgresql(self):
        """Test creating PostgreSQL engine."""
        try:
            engine = create_engine_from_url("postgresql://user:pass@localhost/testdb")
            assert engine is not None
            assert "postgresql" in str(engine.url)
        except ImportError:
            pytest.skip("PostgreSQL driver not available")

    def test_create_session(self):
        """Test creating database session."""
        session = create_session("sqlite:///:memory:")
        assert isinstance(session, Session)
        session.close()

    def test_database_manager_init(self):
        """Test DatabaseManager initialization."""
        manager = DatabaseManager("sqlite:///:memory:")
        assert manager.database_url == "sqlite:///:memory:"
        assert manager.engine is not None
        assert manager.SessionLocal is not None
        manager.close()

    def test_database_manager_create_tables(self):
        """Test creating tables with DatabaseManager."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        
        # Verify tables were created by trying to create a record
        session = manager.get_session()
        market_data = MarketDataModel(
            symbol="BTC/USD",
            timestamp=pytest.importorskip("datetime").datetime.now(),
            open=50000.00,
            high=51000.00,
            low=49000.00,
            close=50500.00,
            volume=100.5,
            exchange="binance"
        )
        session.add(market_data)
        session.commit()
        session.close()
        manager.close()

    def test_database_manager_context_manager(self):
        """Test DatabaseManager as context manager."""
        with DatabaseManager("sqlite:///:memory:") as manager:
            assert manager.engine is not None
            session = manager.get_session()
            assert isinstance(session, Session)
            session.close()

    def test_database_manager_drop_tables(self):
        """Test dropping tables with DatabaseManager."""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.create_tables()
        manager.drop_tables()
        manager.close()

    def test_database_manager_with_echo(self):
        """Test DatabaseManager with SQL echo enabled."""
        manager = DatabaseManager("sqlite:///:memory:", echo=True)
        assert manager.echo is True
        manager.close()