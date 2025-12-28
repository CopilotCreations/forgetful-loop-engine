"""
Capability Registry Module

This module provides the capability registry system that tracks all registered
functions with their metadata including importance, dependencies, and
degradation resistance scores.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from enum import IntEnum
import functools
import logging


class Importance(IntEnum):
    """
    Importance levels for capabilities.
    Higher values indicate more critical functions that resist degradation longer.
    """
    TRIVIAL = 1      # First to be forgotten
    LOW = 2          # Low priority, easily forgotten
    MEDIUM = 3       # Standard priority
    HIGH = 4         # Important, resists degradation
    CRITICAL = 5     # Core functionality, strongly resists decay
    ESSENTIAL = 6    # Cannot be removed - safety layer protected


@dataclass
class CapabilityMetadata:
    """
    Metadata associated with a registered capability.
    
    Attributes:
        name: Unique identifier for the capability
        importance: How critical this capability is (affects decay order)
        dependencies: List of capability names this function depends on
        degradation_resistance: Float 0.0-1.0, higher means harder to degrade
        description: Human-readable description of what this capability does
        original_function: Reference to the original unmodified function
        is_degraded: Whether this capability has been degraded
        degradation_level: 0=intact, 1=approximated, 2=stubbed, 3=deleted
        execution_count: Number of times this capability has been executed
    """
    name: str
    importance: Importance = Importance.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    degradation_resistance: float = 0.5
    description: str = ""
    original_function: Optional[Callable] = None
    is_degraded: bool = False
    degradation_level: int = 0
    execution_count: int = 0


class CapabilityRegistry:
    """
    Central registry for all system capabilities.
    
    The registry tracks all functions that can be degraded over time,
    maintaining metadata about each capability's importance and current state.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, Callable] = {}
        self._metadata: Dict[str, CapabilityMetadata] = {}
        self._logger = logging.getLogger("lethe.registry")
        self._degraded_capabilities: List[str] = []
        self._deleted_capabilities: List[str] = []
    
    def register(
        self,
        name: str,
        importance: Importance = Importance.MEDIUM,
        dependencies: Optional[List[str]] = None,
        degradation_resistance: float = 0.5,
        description: str = ""
    ) -> Callable:
        """
        Decorator to register a function as a capability.
        
        Args:
            name: Unique identifier for this capability
            importance: How critical this capability is
            dependencies: Other capabilities this one depends on
            degradation_resistance: How much this capability resists decay (0.0-1.0)
            description: Human-readable description
            
        Returns:
            Decorator function that registers the capability
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if name in self._metadata:
                    self._metadata[name].execution_count += 1
                return func(*args, **kwargs)
            
            self._capabilities[name] = wrapper
            self._metadata[name] = CapabilityMetadata(
                name=name,
                importance=importance,
                dependencies=dependencies or [],
                degradation_resistance=max(0.0, min(1.0, degradation_resistance)),
                description=description,
                original_function=func,
                is_degraded=False,
                degradation_level=0
            )
            self._logger.debug(f"Registered capability: {name} (importance={importance.name})")
            return wrapper
        return decorator
    
    def register_function(
        self,
        func: Callable,
        name: str,
        importance: Importance = Importance.MEDIUM,
        dependencies: Optional[List[str]] = None,
        degradation_resistance: float = 0.5,
        description: str = ""
    ) -> None:
        """
        Directly register a function as a capability without using decorator syntax.
        
        Args:
            func: The function to register
            name: Unique identifier for this capability
            importance: How critical this capability is
            dependencies: Other capabilities this one depends on
            degradation_resistance: How much this capability resists decay (0.0-1.0)
            description: Human-readable description
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if name in self._metadata:
                self._metadata[name].execution_count += 1
            return func(*args, **kwargs)
        
        self._capabilities[name] = wrapper
        self._metadata[name] = CapabilityMetadata(
            name=name,
            importance=importance,
            dependencies=dependencies or [],
            degradation_resistance=max(0.0, min(1.0, degradation_resistance)),
            description=description,
            original_function=func,
            is_degraded=False,
            degradation_level=0
        )
        self._logger.debug(f"Registered capability: {name} (importance={importance.name})")
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a capability by name, or None if not found or deleted."""
        if name in self._deleted_capabilities:
            return None
        return self._capabilities.get(name)
    
    def get_metadata(self, name: str) -> Optional[CapabilityMetadata]:
        """Get metadata for a capability by name."""
        return self._metadata.get(name)
    
    def execute(self, name: str, *args, **kwargs) -> Any:
        """
        Execute a capability by name.
        
        Args:
            name: The capability to execute
            *args: Positional arguments to pass
            **kwargs: Keyword arguments to pass
            
        Returns:
            The result of the capability execution, or None if capability is missing
            
        Raises:
            KeyError: If the capability doesn't exist
        """
        if name in self._deleted_capabilities:
            self._logger.warning(f"Attempted to execute deleted capability: {name}")
            return None
        
        if name not in self._capabilities:
            raise KeyError(f"Unknown capability: {name}")
        
        return self._capabilities[name](*args, **kwargs)
    
    def list_capabilities(self) -> List[str]:
        """Get list of all registered capability names (including degraded but not deleted)."""
        return [name for name in self._capabilities.keys() 
                if name not in self._deleted_capabilities]
    
    def list_active_capabilities(self) -> List[str]:
        """Get list of capabilities that haven't been degraded."""
        return [name for name, meta in self._metadata.items()
                if not meta.is_degraded and name not in self._deleted_capabilities]
    
    def list_degraded_capabilities(self) -> List[str]:
        """Get list of capabilities that have been degraded."""
        return self._degraded_capabilities.copy()
    
    def list_deleted_capabilities(self) -> List[str]:
        """Get list of capabilities that have been completely deleted."""
        return self._deleted_capabilities.copy()
    
    def mark_degraded(self, name: str, level: int = 1) -> None:
        """
        Mark a capability as degraded.
        
        Args:
            name: The capability name
            level: Degradation level (1=approximated, 2=stubbed, 3=deleted)
        """
        if name in self._metadata:
            self._metadata[name].is_degraded = True
            self._metadata[name].degradation_level = level
            if name not in self._degraded_capabilities:
                self._degraded_capabilities.append(name)
    
    def mark_deleted(self, name: str) -> None:
        """Mark a capability as completely deleted."""
        if name not in self._deleted_capabilities:
            self._deleted_capabilities.append(name)
        self.mark_degraded(name, level=3)
    
    def replace_capability(self, name: str, new_func: Callable) -> None:
        """
        Replace a capability's implementation with a new function.
        
        Args:
            name: The capability to replace
            new_func: The new implementation
        """
        if name in self._capabilities:
            self._capabilities[name] = new_func
            self._logger.debug(f"Replaced capability implementation: {name}")
    
    def get_degradation_candidates(self) -> List[str]:
        """
        Get list of capabilities sorted by degradation priority.
        
        Returns capabilities sorted by:
        1. Lower importance first
        2. Lower degradation resistance first
        3. Not already degraded
        
        Essential capabilities are never returned.
        """
        candidates = []
        for name, meta in self._metadata.items():
            if (meta.importance != Importance.ESSENTIAL and 
                name not in self._deleted_capabilities and
                meta.degradation_level < 3):
                candidates.append((name, meta))
        
        # Sort by importance (ascending), then by degradation resistance (ascending)
        candidates.sort(key=lambda x: (x[1].importance, x[1].degradation_resistance))
        return [name for name, _ in candidates]
    
    def capability_count(self) -> int:
        """Get the total number of registered capabilities."""
        return len(self._capabilities)
    
    def active_count(self) -> int:
        """Get the number of non-degraded capabilities."""
        return len(self.list_active_capabilities())
    
    def degraded_count(self) -> int:
        """Get the number of degraded capabilities."""
        return len(self._degraded_capabilities)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph for all capabilities."""
        return {name: meta.dependencies for name, meta in self._metadata.items()}
    
    def get_dependents(self, name: str) -> List[str]:
        """Get list of capabilities that depend on the given capability."""
        dependents = []
        for cap_name, meta in self._metadata.items():
            if name in meta.dependencies:
                dependents.append(cap_name)
        return dependents


# Global registry instance
registry = CapabilityRegistry()
