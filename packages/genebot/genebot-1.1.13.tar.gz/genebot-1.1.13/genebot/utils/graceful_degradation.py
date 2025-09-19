"""
Graceful degradation manager.

This module provides functionality for graceful degradation when components
fail, allowing the system to continue operating with reduced functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from ..exceptions import TradingBotException, NonRecoverableException


logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Component status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    DISABLED = "disabled"


class ServiceLevel(Enum):
    """Service level enumeration."""
    FULL = "full"           # All features available
    REDUCED = "reduced"     # Some features disabled
    MINIMAL = "minimal"     # Only core features
    EMERGENCY = "emergency" # Emergency stop mode


@dataclass
class ComponentHealth:
    """Component health information."""
    name: str
    status: ComponentStatus
    last_check: datetime
    error_count: int = 0
    last_error: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    fallback_available: bool = False
    
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == ComponentStatus.HEALTHY
    
    def is_available(self) -> bool:
        """Check if component is available (healthy or degraded)."""
        return self.status in [ComponentStatus.HEALTHY, ComponentStatus.DEGRADED]


class GracefulDegradationManager:
    """
    Manages graceful degradation of system components.
    
    This class monitors component health and automatically adjusts
    service levels when components fail.
    """
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
        self.service_level = ServiceLevel.FULL
        self.fallback_handlers: Dict[str, Callable] = {}
        self.degradation_rules: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self.health_check_interval = 30.0  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
    
    def register_component(
        self,
        name: str,
        dependencies: Optional[Set[str]] = None,
        fallback_handler: Optional[Callable] = None,
        critical: bool = False
    ):
        """
        Register a component for health monitoring.
        
        Args:
            name: Component name
            dependencies: Set of component names this component depends on
            fallback_handler: Function to call when component fails
            critical: Whether component failure should trigger emergency mode
        """
        dependencies = dependencies or set()
        
        self.components[name] = ComponentHealth(
            name=name,
            status=ComponentStatus.HEALTHY,
            last_check=datetime.now(timezone.utc),
            dependencies=dependencies,
            fallback_available=fallback_handler is not None
        )
        
        if fallback_handler:
            self.fallback_handlers[name] = fallback_handler
        
        # Update dependent relationships
        for dep in dependencies:
            if dep in self.components:
                self.components[dep].dependents.add(name)
        
        # Set degradation rules
        self.degradation_rules[name] = {
            'critical': critical,
            'max_errors': 5,
            'error_window': timedelta(minutes=5)
        }
        
        logger.info(f"Registered component '{name}' with dependencies: {dependencies}")
    
    async def update_component_status(
        self,
        name: str,
        status: ComponentStatus,
        error: Optional[str] = None
    ):
        """Update component status."""
        async with self._lock:
            if name not in self.components:
                logger.warning(f"Attempted to update unknown component: {name}")
                return
            
            component = self.components[name]
            old_status = component.status
            component.status = status
            component.last_check = datetime.now(timezone.utc)
            
            if error:
                component.error_count += 1
                component.last_error = error
            elif status == ComponentStatus.HEALTHY:
                component.error_count = 0
                component.last_error = None
            
            if old_status != status:
                logger.info(f"Component '{name}' status changed: {old_status.value} -> {status.value}")
                await self._evaluate_service_level()
    
    async def record_component_error(self, name: str, error: Exception):
        """Record an error for a component."""
        error_msg = str(error)
        
        # Determine new status based on error type
        if isinstance(error, NonRecoverableException):
            new_status = ComponentStatus.FAILED
        else:
            # Check if we should degrade or fail the component
            component = self.components.get(name)
            if component and component.fallback_available:
                new_status = ComponentStatus.DEGRADED
            else:
                new_status = ComponentStatus.FAILED
        
        await self.update_component_status(name, new_status, error_msg)
        
        # Trigger fallback if available
        if name in self.fallback_handlers and new_status == ComponentStatus.DEGRADED:
            try:
                await self._execute_fallback(name, error)
            except Exception as fallback_error:
                logger.error(f"Fallback handler for '{name}' failed: {fallback_error}")
                await self.update_component_status(name, ComponentStatus.FAILED)
    
    async def _execute_fallback(self, component_name: str, original_error: Exception):
        """Execute fallback handler for a component."""
        handler = self.fallback_handlers[component_name]
        
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(original_error)
            else:
                handler(original_error)
            
            logger.info(f"Fallback handler executed successfully for component '{component_name}'")
        except Exception as e:
            logger.error(f"Fallback handler failed for component '{component_name}': {e}")
            raise
    
    async def _evaluate_service_level(self):
        """Evaluate and update service level based on component health."""
        failed_components = [
            name for name, comp in self.components.items()
            if comp.status == ComponentStatus.FAILED
        ]
        
        degraded_components = [
            name for name, comp in self.components.items()
            if comp.status == ComponentStatus.DEGRADED
        ]
        
        critical_failed = any(
            self.degradation_rules.get(name, {}).get('critical', False)
            for name in failed_components
        )
        
        # Determine new service level
        if critical_failed:
            new_level = ServiceLevel.EMERGENCY
        elif len(failed_components) > len(self.components) * 0.5:
            new_level = ServiceLevel.MINIMAL
        elif failed_components or len(degraded_components) > 2:
            new_level = ServiceLevel.REDUCED
        else:
            new_level = ServiceLevel.FULL
        
        if new_level != self.service_level:
            old_level = self.service_level
            self.service_level = new_level
            logger.warning(
                f"Service level changed: {old_level.value} -> {new_level.value}. "
                f"Failed: {failed_components}, Degraded: {degraded_components}"
            )
            
            # Notify about service level change
            await self._handle_service_level_change(old_level, new_level)
    
    async def _handle_service_level_change(
        self,
        old_level: ServiceLevel,
        new_level: ServiceLevel
    ):
        """Handle service level changes."""
        if new_level == ServiceLevel.EMERGENCY:
            logger.critical("System entering emergency mode - critical component failed")
            # Could trigger emergency shutdown procedures here
        elif new_level == ServiceLevel.MINIMAL:
            logger.warning("System entering minimal mode - multiple components failed")
        elif new_level == ServiceLevel.REDUCED:
            logger.warning("System entering reduced mode - some components unavailable")
        elif new_level == ServiceLevel.FULL and old_level != ServiceLevel.FULL:
            logger.info("System restored to full service level")
    
    def is_component_available(self, name: str) -> bool:
        """Check if a component is available."""
        component = self.components.get(name)
        return component is not None and component.is_available()
    
    def get_available_components(self) -> List[str]:
        """Get list of available components."""
        return [
            name for name, comp in self.components.items()
            if comp.is_available()
        ]
    
    def get_failed_components(self) -> List[str]:
        """Get list of failed components."""
        return [
            name for name, comp in self.components.items()
            if comp.status == ComponentStatus.FAILED
        ]
    
    def can_execute_operation(self, required_components: List[str]) -> bool:
        """Check if an operation can be executed given required components."""
        return all(self.is_component_available(comp) for comp in required_components)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health information."""
        total_components = len(self.components)
        healthy_count = sum(1 for comp in self.components.values() if comp.is_healthy())
        available_count = sum(1 for comp in self.components.values() if comp.is_available())
        
        return {
            'service_level': self.service_level.value,
            'total_components': total_components,
            'healthy_components': healthy_count,
            'available_components': available_count,
            'health_percentage': (healthy_count / total_components * 100) if total_components > 0 else 0,
            'availability_percentage': (available_count / total_components * 100) if total_components > 0 else 0,
            'components': {
                name: {
                    'status': comp.status.value,
                    'last_check': comp.last_check.isoformat(),
                    'error_count': comp.error_count,
                    'last_error': comp.last_error,
                    'fallback_available': comp.fallback_available
                }
                for name, comp in self.components.items()
            }
        }
    
    async def start_health_monitoring(self):
        """Start periodic health monitoring."""
        if self._health_check_task is not None:
            return
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started health monitoring")
    
    async def stop_health_monitoring(self):
        """Stop periodic health monitoring."""
        if self._health_check_task is not None:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
            logger.info("Stopped health monitoring")
    
    async def _health_check_loop(self):
        """Periodic health check loop."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all components."""
        # This is a basic implementation - in practice, you'd implement
        # specific health checks for each component type
        current_time = datetime.now(timezone.utc)
        
        for name, component in self.components.items():
            # Check if component hasn't been updated recently
            if current_time - component.last_check > timedelta(minutes=2):
                logger.warning(f"Component '{name}' hasn't reported status recently")
                # Could mark as degraded or trigger specific health check


# Global graceful degradation manager instance
graceful_degradation_manager = GracefulDegradationManager()