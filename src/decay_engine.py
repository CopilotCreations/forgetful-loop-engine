"""
Memory Decay Engine

This module implements the core degradation logic that gradually erodes
system capabilities over time. It manages the schedule and execution of
capability degradation while maintaining internal consistency.
"""

import random
import time
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass
import logging

from .capability import CapabilityRegistry, Importance


@dataclass
class DecayEvent:
    """
    Record of a decay event that occurred in the system.
    
    Attributes:
        timestamp: When the decay occurred
        capability_name: Which capability was affected
        decay_type: Type of decay applied (approximate, stub, delete)
        old_level: Previous degradation level
        new_level: New degradation level after decay
    """
    timestamp: float
    capability_name: str
    decay_type: str
    old_level: int
    new_level: int


class DecayEngine:
    """
    Engine responsible for gradually degrading system capabilities.
    
    The decay engine periodically selects capabilities for degradation
    based on their importance and resistance scores. It applies different
    levels of decay:
    
    1. Approximation: Function still works but with reduced accuracy
    2. Stubbing: Function is replaced with a minimal stub
    3. Deletion: Function is completely removed
    """
    
    # Decay type constants
    DECAY_APPROXIMATE = "approximate"
    DECAY_STUB = "stub"
    DECAY_DELETE = "delete"
    
    def __init__(
        self,
        registry: CapabilityRegistry,
        decay_interval: float = 10.0,
        decay_probability: float = 0.3,
        seed: Optional[int] = None
    ):
        """
        Initialize the decay engine.
        
        Args:
            registry: The capability registry to operate on
            decay_interval: Seconds between decay attempts
            decay_probability: Base probability of decay per interval (0.0-1.0)
            seed: Random seed for reproducible decay patterns
        """
        self._registry = registry
        self._decay_interval = decay_interval
        self._decay_probability = decay_probability
        self._logger = logging.getLogger("lethe.decay")
        self._decay_history: List[DecayEvent] = []
        self._last_decay_time: float = time.time()
        self._total_decays: int = 0
        self._is_enabled: bool = True
        
        if seed is not None:
            random.seed(seed)
        
        self._rng = random.Random(seed)
    
    @property
    def decay_interval(self) -> float:
        """Get the current decay interval."""
        return self._decay_interval
    
    @decay_interval.setter
    def decay_interval(self, value: float) -> None:
        """Set the decay interval (minimum 1.0 second)."""
        self._decay_interval = max(1.0, value)
    
    @property
    def decay_probability(self) -> float:
        """Get the current decay probability."""
        return self._decay_probability
    
    @decay_probability.setter
    def decay_probability(self, value: float) -> None:
        """Set the decay probability (0.0-1.0)."""
        self._decay_probability = max(0.0, min(1.0, value))
    
    @property
    def is_enabled(self) -> bool:
        """Check if the decay engine is enabled."""
        return self._is_enabled
    
    def enable(self) -> None:
        """Enable the decay engine."""
        self._is_enabled = True
        self._logger.info("Decay engine enabled")
    
    def disable(self) -> None:
        """Disable the decay engine."""
        self._is_enabled = False
        self._logger.info("Decay engine disabled")
    
    def should_decay(self) -> bool:
        """
        Check if decay should occur based on time and probability.
        
        Returns:
            True if decay should be attempted
        """
        if not self._is_enabled:
            return False
        
        current_time = time.time()
        if current_time - self._last_decay_time < self._decay_interval:
            return False
        
        return self._rng.random() < self._decay_probability
    
    def select_target(self) -> Optional[str]:
        """
        Select a capability to degrade.
        
        Uses weighted random selection based on importance and resistance.
        
        Returns:
            Name of capability to degrade, or None if no candidates
        """
        candidates = self._registry.get_degradation_candidates()
        if not candidates:
            return None
        
        # Weight selection toward less important capabilities
        weights = []
        for name in candidates:
            meta = self._registry.get_metadata(name)
            if meta:
                # Lower importance and lower resistance = higher weight
                importance_weight = (7 - meta.importance) / 6.0
                resistance_weight = 1.0 - meta.degradation_resistance
                weight = importance_weight * resistance_weight
                # Reduce weight for already degraded capabilities
                if meta.is_degraded:
                    weight *= (3 - meta.degradation_level) / 3.0
                weights.append(max(0.01, weight))  # Minimum weight to avoid division by zero
            else:
                weights.append(0.01)
        
        # Weighted random selection
        total_weight = sum(weights)
        r = self._rng.random() * total_weight
        cumulative = 0.0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return candidates[i]
        
        return candidates[-1] if candidates else None
    
    def create_approximation(self, original_func: Callable, error_rate: float = 0.1) -> Callable:
        """
        Create an approximated version of a function that occasionally produces errors.
        
        Args:
            original_func: The original function to approximate
            error_rate: Probability of introducing an error (0.0-1.0)
            
        Returns:
            A wrapper function that may produce approximate results
        """
        def approximated(*args, **kwargs):
            result = original_func(*args, **kwargs)
            
            # Occasionally corrupt the result
            if self._rng.random() < error_rate:
                if isinstance(result, (int, float)):
                    # Add noise to numeric results
                    noise = self._rng.gauss(0, abs(result) * 0.1 + 1)
                    return type(result)(result + noise)
                elif isinstance(result, str):
                    # Corrupt string results
                    if len(result) > 0:
                        chars = list(result)
                        idx = self._rng.randint(0, len(chars) - 1)
                        chars[idx] = '?'
                        return ''.join(chars)
                elif isinstance(result, list):
                    # Shuffle or drop elements
                    if len(result) > 1:
                        result = result.copy()
                        self._rng.shuffle(result)
                        if self._rng.random() < 0.3:
                            result.pop()
                        return result
            
            return result
        
        approximated.__name__ = f"approximated_{original_func.__name__}"
        approximated.__doc__ = f"[DEGRADED] Approximated version of {original_func.__name__}"
        return approximated
    
    def create_stub(self, name: str, return_type: Optional[type] = None) -> Callable:
        """
        Create a stub function that does minimal work.
        
        Args:
            name: Name of the original capability
            return_type: Expected return type to generate default value
            
        Returns:
            A stub function that logs and returns a default value
        """
        def stub(*args, **kwargs):
            self._logger.debug(f"Stub called for: {name}")
            if return_type is None:
                return None
            elif return_type == int:
                return 0
            elif return_type == float:
                return 0.0
            elif return_type == str:
                return ""
            elif return_type == list:
                return []
            elif return_type == dict:
                return {}
            elif return_type == bool:
                return False
            return None
        
        stub.__name__ = f"stub_{name}"
        stub.__doc__ = f"[DELETED] Stub replacement for {name}"
        return stub
    
    def apply_decay(self, name: str) -> Optional[DecayEvent]:
        """
        Apply decay to a specific capability.
        
        The type of decay depends on the capability's current degradation level:
        - Level 0 -> Level 1: Approximation
        - Level 1 -> Level 2: Stub
        - Level 2 -> Level 3: Deletion
        
        Args:
            name: Name of the capability to decay
            
        Returns:
            DecayEvent describing what happened, or None if decay failed
        """
        meta = self._registry.get_metadata(name)
        if meta is None:
            return None
        
        if meta.importance == Importance.ESSENTIAL:
            self._logger.warning(f"Cannot decay essential capability: {name}")
            return None
        
        old_level = meta.degradation_level
        new_level = old_level + 1
        
        if new_level > 3:
            return None  # Already fully degraded
        
        decay_type = ""
        current_time = time.time()
        
        if new_level == 1:
            # Apply approximation
            if meta.original_function:
                approximated = self.create_approximation(meta.original_function)
                self._registry.replace_capability(name, approximated)
                decay_type = self.DECAY_APPROXIMATE
                self._logger.info(f"Approximated capability: {name}")
        
        elif new_level == 2:
            # Apply stub
            stub = self.create_stub(name)
            self._registry.replace_capability(name, stub)
            decay_type = self.DECAY_STUB
            self._logger.info(f"Stubbed capability: {name}")
        
        elif new_level == 3:
            # Mark as deleted
            self._registry.mark_deleted(name)
            decay_type = self.DECAY_DELETE
            self._logger.info(f"Deleted capability: {name}")
        
        self._registry.mark_degraded(name, new_level)
        
        event = DecayEvent(
            timestamp=current_time,
            capability_name=name,
            decay_type=decay_type,
            old_level=old_level,
            new_level=new_level
        )
        self._decay_history.append(event)
        self._total_decays += 1
        self._last_decay_time = current_time
        
        return event
    
    def tick(self) -> Optional[DecayEvent]:
        """
        Perform a decay tick - check if decay should occur and apply it.
        
        Returns:
            DecayEvent if decay occurred, None otherwise
        """
        if not self.should_decay():
            return None
        
        target = self.select_target()
        if target is None:
            self._logger.debug("No decay targets available")
            return None
        
        return self.apply_decay(target)
    
    def force_decay(self, name: Optional[str] = None) -> Optional[DecayEvent]:
        """
        Force an immediate decay on a specific or random capability.
        
        Args:
            name: Specific capability to decay, or None for random selection
            
        Returns:
            DecayEvent if decay occurred, None otherwise
        """
        if name is None:
            name = self.select_target()
        
        if name is None:
            return None
        
        return self.apply_decay(name)
    
    def get_history(self) -> List[DecayEvent]:
        """Get the complete decay history."""
        return self._decay_history.copy()
    
    def get_recent_history(self, count: int = 10) -> List[DecayEvent]:
        """Get the most recent decay events."""
        return self._decay_history[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get decay statistics.
        
        Returns:
            Dictionary with decay statistics
        """
        type_counts = {
            self.DECAY_APPROXIMATE: 0,
            self.DECAY_STUB: 0,
            self.DECAY_DELETE: 0
        }
        
        for event in self._decay_history:
            if event.decay_type in type_counts:
                type_counts[event.decay_type] += 1
        
        return {
            "total_decays": self._total_decays,
            "decay_interval": self._decay_interval,
            "decay_probability": self._decay_probability,
            "is_enabled": self._is_enabled,
            "approximations": type_counts[self.DECAY_APPROXIMATE],
            "stubs": type_counts[self.DECAY_STUB],
            "deletions": type_counts[self.DECAY_DELETE],
            "history_length": len(self._decay_history)
        }
    
    def reset(self) -> None:
        """Reset the decay engine state (does not restore capabilities)."""
        self._decay_history.clear()
        self._total_decays = 0
        self._last_decay_time = time.time()
        self._logger.info("Decay engine reset")
