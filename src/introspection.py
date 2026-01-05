"""
Self-Introspection Module

This module provides the system with the ability to examine its own state,
track lost capabilities, and understand its current level of degradation.
Uses Python's inspect module and sys.modules for deep introspection.
"""

import inspect
import sys
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging

from .capability import CapabilityRegistry, CapabilityMetadata, Importance


@dataclass
class SystemState:
    """
    Snapshot of the system's current state.
    
    Attributes:
        timestamp: When this snapshot was taken
        total_capabilities: Total number of registered capabilities
        active_capabilities: Number of non-degraded capabilities
        degraded_capabilities: Number of degraded capabilities
        deleted_capabilities: Number of deleted capabilities
        health_percentage: Overall system health (0-100)
        loaded_modules: Number of modules in sys.modules
        memory_usage: Approximate memory usage in bytes (if available)
    """
    timestamp: float
    total_capabilities: int
    active_capabilities: int
    degraded_capabilities: int
    deleted_capabilities: int
    health_percentage: float
    loaded_modules: int
    memory_usage: int = 0


@dataclass
class CapabilityLoss:
    """
    Record of a lost capability.
    
    Attributes:
        name: Name of the lost capability
        importance: How important it was
        lost_at: Timestamp of when it was lost
        degradation_level: Final degradation level
        description: What the capability used to do
    """
    name: str
    importance: Importance
    lost_at: float
    degradation_level: int
    description: str


class Introspector:
    """
    System introspection engine that monitors and reports on system health.
    
    The introspector tracks the state of all capabilities, maintains a history
    of lost functionality, and provides insights into the system's degradation.
    """
    
    def __init__(self, registry: CapabilityRegistry):
        """
        Initialize the introspector.
        
        Args:
            registry: The capability registry to introspect
        """
        self._registry = registry
        self._logger = logging.getLogger("lethe.introspection")
        self._state_history: List[SystemState] = []
        self._lost_capabilities: List[CapabilityLoss] = []
        self._known_capabilities: Set[str] = set()
        self._last_snapshot_time: float = 0
        self._initial_capability_count: int = 0
        self._startup_time: float = time.time()
    
    def initialize(self) -> None:
        """
        Initialize introspection by capturing initial state.
        
        Should be called after all capabilities are registered.
        """
        self._known_capabilities = set(self._registry.list_capabilities())
        self._initial_capability_count = len(self._known_capabilities)
        self._capture_state()
        self._logger.info(
            f"Introspection initialized with {self._initial_capability_count} capabilities"
        )
    
    def _capture_state(self) -> SystemState:
        """
        Capture the current system state.
        
        Returns:
            SystemState snapshot
        """
        active = self._registry.list_active_capabilities()
        degraded = self._registry.list_degraded_capabilities()
        deleted = self._registry.list_deleted_capabilities()
        total = self._registry.capability_count()
        
        if total > 0:
            # Health is based on active capabilities weighted by importance
            health = self._calculate_health()
        else:
            health = 0.0
        
        # Try to get memory usage
        memory = 0
        try:
            import tracemalloc
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                memory = current
        except Exception:
            pass
        
        state = SystemState(
            timestamp=time.time(),
            total_capabilities=total,
            active_capabilities=len(active),
            degraded_capabilities=len(degraded),
            deleted_capabilities=len(deleted),
            health_percentage=health,
            loaded_modules=len(sys.modules),
            memory_usage=memory
        )
        
        self._state_history.append(state)
        self._last_snapshot_time = state.timestamp
        return state
    
    def _calculate_health(self) -> float:
        """
        Calculate overall system health based on capability states.
        
        Returns:
            Health percentage (0-100)
        """
        if self._initial_capability_count == 0:
            return 100.0
        
        total_weight = 0.0
        current_weight = 0.0
        
        for name in self._known_capabilities:
            meta = self._registry.get_metadata(name)
            if meta:
                weight = float(meta.importance)
                total_weight += weight
                
                # Calculate capability contribution based on degradation level
                if meta.degradation_level == 0:
                    current_weight += weight
                elif meta.degradation_level == 1:
                    current_weight += weight * 0.7  # Approximated
                elif meta.degradation_level == 2:
                    current_weight += weight * 0.3  # Stubbed
                # Level 3 (deleted) contributes 0
        
        if total_weight == 0:
            return 100.0
        
        return (current_weight / total_weight) * 100.0
    
    def get_current_state(self) -> SystemState:
        """Get the current system state.

        Returns:
            SystemState: A snapshot of the current system state.
        """
        return self._capture_state()
    
    def get_state_history(self) -> List[SystemState]:
        """Get the complete state history.

        Returns:
            List[SystemState]: A copy of all recorded state snapshots.
        """
        return self._state_history.copy()
    
    def get_recent_states(self, count: int = 10) -> List[SystemState]:
        """Get the most recent state snapshots.

        Args:
            count: Maximum number of recent states to return. Defaults to 10.

        Returns:
            List[SystemState]: The most recent state snapshots, up to count.
        """
        return self._state_history[-count:]
    
    def update_lost_capabilities(self) -> List[CapabilityLoss]:
        """
        Check for newly lost capabilities and record them.
        
        Returns:
            List of newly detected lost capabilities
        """
        new_losses: List[CapabilityLoss] = []
        current_time = time.time()
        
        deleted = set(self._registry.list_deleted_capabilities())
        for name in deleted:
            # Check if we already recorded this loss
            if not any(loss.name == name for loss in self._lost_capabilities):
                meta = self._registry.get_metadata(name)
                if meta:
                    loss = CapabilityLoss(
                        name=name,
                        importance=meta.importance,
                        lost_at=current_time,
                        degradation_level=meta.degradation_level,
                        description=meta.description
                    )
                    self._lost_capabilities.append(loss)
                    new_losses.append(loss)
                    self._logger.info(f"Recorded capability loss: {name}")
        
        return new_losses
    
    def get_lost_capabilities(self) -> List[CapabilityLoss]:
        """Get all recorded capability losses.

        Returns:
            List[CapabilityLoss]: A copy of all recorded capability losses.
        """
        return self._lost_capabilities.copy()
    
    def get_lost_count(self) -> int:
        """Get the count of lost capabilities.

        Returns:
            int: The number of capabilities that have been lost.
        """
        return len(self._lost_capabilities)
    
    def get_capability_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific capability.
        
        Args:
            name: The capability name
            
        Returns:
            Dictionary with capability details, or None if not found
        """
        meta = self._registry.get_metadata(name)
        if meta is None:
            return None
        
        func = self._registry.get(name)
        
        info = {
            "name": meta.name,
            "importance": meta.importance.name,
            "dependencies": meta.dependencies,
            "degradation_resistance": meta.degradation_resistance,
            "description": meta.description,
            "is_degraded": meta.is_degraded,
            "degradation_level": meta.degradation_level,
            "execution_count": meta.execution_count,
            "is_deleted": name in self._registry.list_deleted_capabilities(),
        }
        
        # Add function introspection if available
        if func is not None:
            try:
                info["function_name"] = func.__name__
                info["function_doc"] = func.__doc__
                sig = inspect.signature(func)
                info["signature"] = str(sig)
                info["parameters"] = list(sig.parameters.keys())
            except (ValueError, TypeError):
                pass
        
        return info
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get information about loaded modules.
        
        Returns:
            Dictionary with module information
        """
        lethe_modules = [
            name for name in sys.modules.keys()
            if name.startswith('src') or name.startswith('lethe')
        ]
        
        return {
            "total_modules": len(sys.modules),
            "lethe_modules": lethe_modules,
            "lethe_module_count": len(lethe_modules)
        }
    
    def get_function_source(self, name: str) -> Optional[str]:
        """
        Attempt to get the source code of a capability's original function.
        
        Args:
            name: The capability name
            
        Returns:
            Source code string, or None if unavailable
        """
        meta = self._registry.get_metadata(name)
        if meta is None or meta.original_function is None:
            return None
        
        try:
            return inspect.getsource(meta.original_function)
        except (OSError, TypeError):
            return None
    
    def get_uptime(self) -> float:
        """Get the system uptime in seconds.

        Returns:
            float: The number of seconds since the system started.
        """
        return time.time() - self._startup_time
    
    def get_health_trend(self) -> str:
        """
        Analyze the health trend over recent history.
        
        Returns:
            String describing the trend: "stable", "declining", "critical"
        """
        if len(self._state_history) < 2:
            return "stable"
        
        recent = self._state_history[-5:]
        if len(recent) < 2:
            return "stable"
        
        health_values = [s.health_percentage for s in recent]
        avg_change = (health_values[-1] - health_values[0]) / len(recent)
        
        current_health = health_values[-1]
        
        if current_health < 20:
            return "critical"
        elif avg_change < -5:
            return "declining"
        elif avg_change < -1:
            return "slow_decline"
        else:
            return "stable"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the system state.
        
        Returns:
            Dictionary with system summary
        """
        state = self.get_current_state()
        trend = self.get_health_trend()
        
        return {
            "uptime_seconds": self.get_uptime(),
            "health_percentage": state.health_percentage,
            "health_trend": trend,
            "total_capabilities": state.total_capabilities,
            "active_capabilities": state.active_capabilities,
            "degraded_capabilities": state.degraded_capabilities,
            "deleted_capabilities": state.deleted_capabilities,
            "lost_capability_count": self.get_lost_count(),
            "loaded_modules": state.loaded_modules,
            "state_history_length": len(self._state_history)
        }
    
    def can_remember(self, name: str) -> bool:
        """
        Check if the system can still remember a capability.
        
        Args:
            name: The capability name
            
        Returns:
            True if the capability still exists and is functional
        """
        if name in self._registry.list_deleted_capabilities():
            return False
        
        meta = self._registry.get_metadata(name)
        if meta is None:
            return False
        
        return meta.degradation_level < 3
    
    def get_forgotten_names(self) -> List[str]:
        """Get list of capability names that have been forgotten (deleted).

        Returns:
            List[str]: Names of capabilities that have been deleted.
        """
        return self._registry.list_deleted_capabilities()
    
    def get_fading_memories(self) -> List[str]:
        """Get list of capabilities that are degraded but not yet deleted.

        Returns:
            List[str]: Names of capabilities that are degrading but still exist.
        """
        degraded = self._registry.list_degraded_capabilities()
        deleted = set(self._registry.list_deleted_capabilities())
        return [name for name in degraded if name not in deleted]
