"""
Broker failover and reconnection mechanisms.

This module provides functionality for handling broker failures, implementing
failover to backup brokers, and managing reconnection attempts with exponential
backoff and circuit breaker patterns.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import random

from .multi_market_exceptions import (
    MarketType,
    BrokerConnectionException,
    BrokerUnavailableException,
    FailoverException,
    ReconnectionException
)


class BrokerStatus(Enum):
    """Broker connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    FAILED = "failed"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class FailoverStrategy(Enum):
    """Failover strategy types."""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    RANDOM = "random"


@dataclass
class BrokerConfig:
    """Broker configuration for failover."""
    name: str
    market_type: MarketType
    priority: int = 0
    max_connections: int = 10
    health_check_interval: int = 30
    connection_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_retry_delay: float = 300.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionAttempt:
    """Represents a connection attempt."""
    broker_name: str
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    duration: Optional[float] = None


class BrokerHealthMonitor:
    """Monitors broker health and connection status."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.broker_status: Dict[str, BrokerStatus] = {}
        self.last_health_check: Dict[str, datetime] = {}
        self.connection_attempts: Dict[str, List[ConnectionAttempt]] = {}
        self.circuit_breaker_state: Dict[str, bool] = {}
        self.circuit_breaker_opened_at: Dict[str, datetime] = {}
        self.health_check_callbacks: Dict[str, Callable] = {}
    
    def register_broker(self, broker_config: BrokerConfig) -> None:
        """Register a broker for monitoring."""
        self.broker_status[broker_config.name] = BrokerStatus.DISCONNECTED
        self.connection_attempts[broker_config.name] = []
        self.circuit_breaker_state[broker_config.name] = False
        self.logger.info(f"Registered broker {broker_config.name} for monitoring")
    
    def register_health_check_callback(
        self,
        broker_name: str,
        callback: Callable
    ) -> None:
        """Register health check callback for a broker."""
        self.health_check_callbacks[broker_name] = callback
    
    def update_broker_status(
        self,
        broker_name: str,
        status: BrokerStatus,
        error: Optional[str] = None
    ) -> None:
        """Update broker status."""
        old_status = self.broker_status.get(broker_name)
        self.broker_status[broker_name] = status
        
        if old_status != status:
            self.logger.info(f"Broker {broker_name} status changed: {old_status} -> {status}")
            if error:
                self.logger.error(f"Broker {broker_name} error: {error}")
    
    def record_connection_attempt(
        self,
        broker_name: str,
        success: bool,
        error: Optional[str] = None,
        duration: Optional[float] = None
    ) -> None:
        """Record a connection attempt."""
        attempt = ConnectionAttempt(
            broker_name=broker_name,
            timestamp=datetime.now(timezone.utc),
            success=success,
            error=error,
            duration=duration
        )
        
        attempts = self.connection_attempts.setdefault(broker_name, [])
        attempts.append(attempt)
        
        # Keep only last 100 attempts
        if len(attempts) > 100:
            attempts.pop(0)
        
        # Update circuit breaker state
        self._update_circuit_breaker(broker_name)
    
    def is_broker_healthy(self, broker_name: str) -> bool:
        """Check if broker is healthy."""
        status = self.broker_status.get(broker_name, BrokerStatus.DISCONNECTED)
        circuit_open = self.circuit_breaker_state.get(broker_name, False)
        
        return status == BrokerStatus.CONNECTED and not circuit_open
    
    def is_circuit_breaker_open(self, broker_name: str) -> bool:
        """Check if circuit breaker is open for broker."""
        return self.circuit_breaker_state.get(broker_name, False)
    
    def get_failure_rate(self, broker_name: str, window_minutes: int = 10) -> float:
        """Get failure rate for broker in the specified time window."""
        attempts = self.connection_attempts.get(broker_name, [])
        if not attempts:
            return 0.0
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        recent_attempts = [a for a in attempts if a.timestamp >= cutoff_time]
        
        if not recent_attempts:
            return 0.0
        
        failures = sum(1 for a in recent_attempts if not a.success)
        return failures / len(recent_attempts)
    
    def _update_circuit_breaker(self, broker_name: str) -> None:
        """Update circuit breaker state based on recent failures."""
        attempts = self.connection_attempts.get(broker_name, [])
        if len(attempts) < 5:
            return
        
        # Check last 5 attempts
        recent_attempts = attempts[-5:]
        failures = sum(1 for a in recent_attempts if not a.success)
        
        if failures >= 5:  # All last 5 attempts failed
            if not self.circuit_breaker_state.get(broker_name, False):
                self.circuit_breaker_state[broker_name] = True
                self.circuit_breaker_opened_at[broker_name] = datetime.now(timezone.utc)
                self.logger.warning(f"Circuit breaker opened for broker {broker_name}")
        else:
            # Check if circuit breaker should be closed
            if self.circuit_breaker_state.get(broker_name, False):
                opened_at = self.circuit_breaker_opened_at.get(broker_name)
                if opened_at and datetime.now(timezone.utc) - opened_at > timedelta(minutes=5):
                    self.circuit_breaker_state[broker_name] = False
                    self.logger.info(f"Circuit breaker closed for broker {broker_name}")


class BrokerFailoverManager:
    """Manages broker failover and reconnection."""
    
    def __init__(self, failover_strategy: FailoverStrategy = FailoverStrategy.PRIORITY_BASED):
        self.logger = logging.getLogger(__name__)
        self.failover_strategy = failover_strategy
        self.broker_configs: Dict[str, BrokerConfig] = {}
        self.primary_brokers: Dict[MarketType, str] = {}
        self.backup_brokers: Dict[MarketType, List[str]] = {}
        self.active_brokers: Dict[MarketType, str] = {}
        self.health_monitor = BrokerHealthMonitor()
        self.reconnection_tasks: Dict[str, asyncio.Task] = {}
        self.failover_callbacks: List[Callable] = []
        self._running = False
    
    def register_broker(self, broker_config: BrokerConfig) -> None:
        """Register a broker configuration."""
        self.broker_configs[broker_config.name] = broker_config
        self.health_monitor.register_broker(broker_config)
        
        # Set as primary if it's the first broker for this market type
        if broker_config.market_type not in self.primary_brokers:
            self.primary_brokers[broker_config.market_type] = broker_config.name
            self.active_brokers[broker_config.market_type] = broker_config.name
        else:
            # Add to backup brokers
            backups = self.backup_brokers.setdefault(broker_config.market_type, [])
            backups.append(broker_config.name)
            # Sort by priority (higher priority first)
            backups.sort(key=lambda name: self.broker_configs[name].priority, reverse=True)
        
        self.logger.info(f"Registered broker {broker_config.name} for {broker_config.market_type.value}")
    
    def register_failover_callback(self, callback: Callable) -> None:
        """Register callback to be called on failover events."""
        self.failover_callbacks.append(callback)
    
    def get_active_broker(self, market_type: MarketType) -> Optional[str]:
        """Get the currently active broker for a market type."""
        return self.active_brokers.get(market_type)
    
    def get_available_brokers(self, market_type: MarketType) -> List[str]:
        """Get list of available brokers for a market type."""
        brokers = []
        
        # Add primary broker if healthy
        primary = self.primary_brokers.get(market_type)
        if primary and self.health_monitor.is_broker_healthy(primary):
            brokers.append(primary)
        
        # Add healthy backup brokers
        backups = self.backup_brokers.get(market_type, [])
        for broker_name in backups:
            if self.health_monitor.is_broker_healthy(broker_name):
                brokers.append(broker_name)
        
        return brokers
    
    async def handle_broker_failure(
        self,
        broker_name: str,
        error: Exception,
        market_type: MarketType
    ) -> Optional[str]:
        """Handle broker failure and attempt failover."""
        self.logger.error(f"Broker {broker_name} failed: {error}")
        
        # Update broker status
        self.health_monitor.update_broker_status(
            broker_name,
            BrokerStatus.FAILED,
            str(error)
        )
        
        # Record failure
        self.health_monitor.record_connection_attempt(
            broker_name,
            success=False,
            error=str(error)
        )
        
        # Attempt failover
        new_broker = await self._attempt_failover(market_type, broker_name)
        
        # Start reconnection task for failed broker
        if broker_name not in self.reconnection_tasks:
            task = asyncio.create_task(self._reconnect_broker(broker_name))
            self.reconnection_tasks[broker_name] = task
        
        return new_broker
    
    async def _attempt_failover(
        self,
        market_type: MarketType,
        failed_broker: str
    ) -> Optional[str]:
        """Attempt to failover to a backup broker."""
        available_brokers = self.get_available_brokers(market_type)
        
        # Remove the failed broker from available list
        if failed_broker in available_brokers:
            available_brokers.remove(failed_broker)
        
        if not available_brokers:
            raise FailoverException(
                f"No available backup brokers for {market_type.value}",
                primary_broker=failed_broker,
                backup_brokers=self.backup_brokers.get(market_type, []),
                failover_reason="no_healthy_backups"
            )
        
        # Select backup broker based on strategy
        backup_broker = self._select_backup_broker(available_brokers)
        
        try:
            # Attempt to connect to backup broker
            await self._connect_to_broker(backup_broker)
            
            # Update active broker
            old_active = self.active_brokers.get(market_type)
            self.active_brokers[market_type] = backup_broker
            
            self.logger.info(
                f"Successfully failed over from {failed_broker} to {backup_broker} "
                f"for {market_type.value}"
            )
            
            # Notify callbacks
            for callback in self.failover_callbacks:
                try:
                    await callback(market_type, old_active, backup_broker)
                except Exception as e:
                    self.logger.error(f"Failover callback error: {e}")
            
            return backup_broker
            
        except Exception as e:
            self.logger.error(f"Failed to connect to backup broker {backup_broker}: {e}")
            
            # Mark backup broker as failed and try next one
            self.health_monitor.record_connection_attempt(
                backup_broker,
                success=False,
                error=str(e)
            )
            
            # Recursively try next backup
            return await self._attempt_failover(market_type, failed_broker)
    
    def _select_backup_broker(self, available_brokers: List[str]) -> str:
        """Select backup broker based on failover strategy."""
        if not available_brokers:
            raise ValueError("No available brokers")
        
        if self.failover_strategy == FailoverStrategy.PRIORITY_BASED:
            # Select broker with highest priority
            return max(
                available_brokers,
                key=lambda name: self.broker_configs[name].priority
            )
        
        elif self.failover_strategy == FailoverStrategy.LOAD_BALANCED:
            # Select broker with lowest failure rate
            return min(
                available_brokers,
                key=lambda name: self.health_monitor.get_failure_rate(name)
            )
        
        elif self.failover_strategy == FailoverStrategy.RANDOM:
            return random.choice(available_brokers)
        
        else:  # ROUND_ROBIN
            # Simple round-robin (could be improved with state tracking)
            return available_brokers[0]
    
    async def _connect_to_broker(self, broker_name: str) -> None:
        """Attempt to connect to a broker."""
        config = self.broker_configs[broker_name]
        start_time = datetime.now(timezone.utc)
        
        try:
            self.health_monitor.update_broker_status(broker_name, BrokerStatus.CONNECTING)
            
            # Simulate connection attempt (replace with actual connection logic)
            await asyncio.sleep(0.1)  # Placeholder
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.health_monitor.update_broker_status(broker_name, BrokerStatus.CONNECTED)
            self.health_monitor.record_connection_attempt(
                broker_name,
                success=True,
                duration=duration
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            self.health_monitor.update_broker_status(
                broker_name,
                BrokerStatus.FAILED,
                str(e)
            )
            self.health_monitor.record_connection_attempt(
                broker_name,
                success=False,
                error=str(e),
                duration=duration
            )
            raise
    
    async def _reconnect_broker(self, broker_name: str) -> None:
        """Attempt to reconnect to a failed broker with exponential backoff."""
        config = self.broker_configs[broker_name]
        retry_count = 0
        delay = config.retry_delay
        
        while retry_count < config.max_retries:
            try:
                # Check if circuit breaker is open
                if self.health_monitor.is_circuit_breaker_open(broker_name):
                    self.logger.info(f"Circuit breaker open for {broker_name}, skipping reconnection")
                    await asyncio.sleep(delay)
                    delay = min(delay * config.backoff_multiplier, config.max_retry_delay)
                    continue
                
                self.logger.info(f"Attempting to reconnect to {broker_name} (attempt {retry_count + 1})")
                
                await self._connect_to_broker(broker_name)
                
                self.logger.info(f"Successfully reconnected to {broker_name}")
                
                # Remove from reconnection tasks
                if broker_name in self.reconnection_tasks:
                    del self.reconnection_tasks[broker_name]
                
                return
                
            except Exception as e:
                retry_count += 1
                
                if retry_count < config.max_retries:
                    self.logger.warning(
                        f"Reconnection attempt {retry_count} failed for {broker_name}: {e}. "
                        f"Retrying in {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * config.backoff_multiplier, config.max_retry_delay)
                else:
                    self.logger.error(
                        f"All reconnection attempts failed for {broker_name}: {e}"
                    )
                    
                    raise ReconnectionException(
                        f"Failed to reconnect to {broker_name} after {config.max_retries} attempts",
                        service_name=broker_name,
                        attempt_count=retry_count,
                        max_attempts=config.max_retries,
                        last_error=str(e)
                    )
        
        # Remove from reconnection tasks
        if broker_name in self.reconnection_tasks:
            del self.reconnection_tasks[broker_name]
    
    async def start(self) -> None:
        """Start the failover manager."""
        self._running = True
        self.logger.info("Started broker failover manager")
    
    async def stop(self) -> None:
        """Stop the failover manager."""
        self._running = False
        
        # Cancel all reconnection tasks
        for task in self.reconnection_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.reconnection_tasks:
            await asyncio.gather(*self.reconnection_tasks.values(), return_exceptions=True)
        
        self.reconnection_tasks.clear()
        self.logger.info("Stopped broker failover manager")