"""
Market closure handling and order queuing system.

This module provides functionality to handle market closures, queue orders
for when markets reopen, and manage order execution across different market
sessions.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from .multi_market_exceptions import (
    MarketClosedException, 
    MarketType, 
    OrderQueueException,
    MarketSessionException
)


class OrderStatus(Enum):
    """Order status in the queue."""
    QUEUED = "queued"
    PENDING_EXECUTION = "pending_execution"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class QueuedOrder:
    """Represents an order in the queue."""
    id: str
    market_type: MarketType
    broker_name: str
    symbol: str
    side: str
    amount: float
    order_type: str
    created_at: datetime
    price: Optional[float] = None
    expires_at: Optional[datetime] = None
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    status: OrderStatus = OrderStatus.QUEUED
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None


class MarketClosureHandler:
    """Handles market closures and order queuing."""
    
    def __init__(self, max_queue_size: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.max_queue_size = max_queue_size
        self.order_queues: Dict[MarketType, deque] = {
            market_type: deque() for market_type in MarketType
        }
        self.market_sessions: Dict[MarketType, Dict[str, Any]] = {}
        self.session_callbacks: Dict[MarketType, List[Callable]] = {
            market_type: [] for market_type in MarketType
        }
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    def register_market_session(
        self,
        market_type: MarketType,
        session_info: Dict[str, Any]
    ) -> None:
        """Register market session information."""
        self.market_sessions[market_type] = session_info
        self.logger.info(f"Registered session for {market_type.value}: {session_info}")
    
    def register_session_callback(
        self,
        market_type: MarketType,
        callback: Callable
    ) -> None:
        """Register callback for market session changes."""
        self.session_callbacks[market_type].append(callback)
    
    def is_market_open(self, market_type: MarketType) -> bool:
        """Check if a market is currently open."""
        if market_type == MarketType.CRYPTO:
            return True  # Crypto markets are always open
        
        session_info = self.market_sessions.get(market_type)
        if not session_info:
            self.logger.warning(f"No session info for {market_type.value}")
            return False
        
        now = datetime.now(timezone.utc)
        
        # Check if current time is within any active session
        for session_name, session_data in session_info.items():
            if self._is_time_in_session(now, session_data):
                return True
        
        return False
    
    def get_next_open_time(self, market_type: MarketType) -> Optional[datetime]:
        """Get the next time the market will open."""
        if market_type == MarketType.CRYPTO:
            return None  # Always open
        
        session_info = self.market_sessions.get(market_type)
        if not session_info:
            return None
        
        now = datetime.now(timezone.utc)
        next_opens = []
        
        for session_name, session_data in session_info.items():
            next_open = self._calculate_next_open(now, session_data)
            if next_open:
                next_opens.append(next_open)
        
        return min(next_opens) if next_opens else None
    
    def queue_order(self, order: QueuedOrder) -> None:
        """Queue an order for execution when market opens."""
        if not self.is_market_open(order.market_type):
            queue = self.order_queues[order.market_type]
            
            if len(queue) >= self.max_queue_size:
                raise OrderQueueException(
                    f"Order queue for {order.market_type.value} is full",
                    order.market_type,
                    queue_size=len(queue),
                    max_queue_size=self.max_queue_size
                )
            
            # Insert order based on priority (higher priority first)
            inserted = False
            for i, queued_order in enumerate(queue):
                if order.priority > queued_order.priority:
                    queue.insert(i, order)
                    inserted = True
                    break
            
            if not inserted:
                queue.append(order)
            
            self.logger.info(
                f"Queued order {order.id} for {order.market_type.value} "
                f"(queue size: {len(queue)})"
            )
        else:
            raise MarketClosedException(
                f"Market {order.market_type.value} is open, order should be executed immediately",
                order.market_type
            )
    
    def cancel_queued_order(self, order_id: str, market_type: MarketType) -> bool:
        """Cancel a queued order."""
        queue = self.order_queues[market_type]
        
        for i, order in enumerate(queue):
            if order.id == order_id:
                order.status = OrderStatus.CANCELLED
                queue.remove(order)
                self.logger.info(f"Cancelled queued order {order_id}")
                return True
        
        return False
    
    def get_queued_orders(
        self,
        market_type: Optional[MarketType] = None
    ) -> List[QueuedOrder]:
        """Get queued orders for a market or all markets."""
        if market_type:
            return list(self.order_queues[market_type])
        
        all_orders = []
        for queue in self.order_queues.values():
            all_orders.extend(queue)
        
        return all_orders
    
    async def start_monitoring(self) -> None:
        """Start monitoring market sessions and processing queued orders."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_sessions())
        self.logger.info("Started market closure monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring market sessions."""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped market closure monitoring")
    
    async def _monitor_sessions(self) -> None:
        """Monitor market sessions and process queued orders."""
        while self._running:
            try:
                for market_type in MarketType:
                    if self.is_market_open(market_type):
                        await self._process_queued_orders(market_type)
                    
                    # Check for session transitions
                    await self._check_session_transitions(market_type)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in session monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _process_queued_orders(self, market_type: MarketType) -> None:
        """Process queued orders for an open market."""
        queue = self.order_queues[market_type]
        
        while queue:
            order = queue.popleft()
            
            # Check if order has expired
            if order.expires_at and datetime.now(timezone.utc) > order.expires_at:
                order.status = OrderStatus.EXPIRED
                self.logger.warning(f"Order {order.id} expired")
                continue
            
            try:
                order.status = OrderStatus.PENDING_EXECUTION
                
                # Execute the order callback if provided
                if order.callback:
                    await order.callback(order)
                    order.status = OrderStatus.EXECUTED
                    self.logger.info(f"Executed queued order {order.id}")
                else:
                    self.logger.warning(f"No callback for order {order.id}")
                    order.status = OrderStatus.FAILED
                
            except Exception as e:
                order.retry_count += 1
                
                if order.retry_count < order.max_retries:
                    order.status = OrderStatus.QUEUED
                    queue.append(order)  # Re-queue for retry
                    self.logger.warning(
                        f"Order {order.id} failed, retry {order.retry_count}/{order.max_retries}: {e}"
                    )
                else:
                    order.status = OrderStatus.FAILED
                    self.logger.error(f"Order {order.id} failed permanently: {e}")
    
    async def _check_session_transitions(self, market_type: MarketType) -> None:
        """Check for market session transitions and notify callbacks."""
        # This would implement logic to detect when markets open/close
        # and call registered callbacks
        pass
    
    def _is_time_in_session(self, time: datetime, session_data: Dict[str, Any]) -> bool:
        """Check if a time falls within a trading session."""
        # Implementation would depend on session_data format
        # This is a simplified version
        start_time = session_data.get('start')
        end_time = session_data.get('end')
        
        if not start_time or not end_time:
            return False
        
        # Convert to UTC if needed and compare
        # This is a simplified implementation
        return start_time <= time.time() <= end_time
    
    def _calculate_next_open(
        self,
        current_time: datetime,
        session_data: Dict[str, Any]
    ) -> Optional[datetime]:
        """Calculate the next opening time for a session."""
        # Implementation would calculate the next opening time
        # based on session schedule and current time
        # This is a placeholder
        return current_time + timedelta(hours=1)


class OrderQueueManager:
    """Manages order queues across multiple markets."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.closure_handler = MarketClosureHandler()
        self.order_callbacks: Dict[str, Callable] = {}
    
    def register_order_callback(self, order_type: str, callback: Callable) -> None:
        """Register callback for order execution."""
        self.order_callbacks[order_type] = callback
    
    async def submit_order(
        self,
        market_type: MarketType,
        broker_name: str,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = "market",
        priority: int = 0,
        expires_in: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit an order, queuing it if market is closed."""
        order_id = f"{market_type.value}_{broker_name}_{symbol}_{datetime.now().timestamp()}"
        
        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc) + expires_in
        
        callback = self.order_callbacks.get(order_type)
        
        order = QueuedOrder(
            id=order_id,
            market_type=market_type,
            broker_name=broker_name,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            order_type=order_type,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            priority=priority,
            metadata=metadata or {},
            callback=callback
        )
        
        if self.closure_handler.is_market_open(market_type):
            # Execute immediately
            try:
                if callback:
                    await callback(order)
                    self.logger.info(f"Executed order {order_id} immediately")
                else:
                    raise OrderQueueException(
                        f"No callback registered for order type {order_type}",
                        market_type
                    )
            except Exception as e:
                self.logger.error(f"Failed to execute order {order_id}: {e}")
                raise
        else:
            # Queue for later execution
            try:
                self.closure_handler.queue_order(order)
                next_open = self.closure_handler.get_next_open_time(market_type)
                
                raise MarketClosedException(
                    f"Market {market_type.value} is closed, order queued",
                    market_type,
                    next_open_time=next_open
                )
            except OrderQueueException:
                raise
        
        return order_id
    
    async def start(self) -> None:
        """Start the order queue manager."""
        await self.closure_handler.start_monitoring()
    
    async def stop(self) -> None:
        """Stop the order queue manager."""
        await self.closure_handler.stop_monitoring()