"""
Safety Layer Module

This module implements safeguards to prevent total system collapse.
It ensures that at least one minimal behavior remains functional
and that the system never crashes outright despite degradation.
"""

import logging
import time
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .capability import CapabilityRegistry, Importance


class SafetyStatus(Enum):
    """Safety status levels."""
    NORMAL = "normal"           # System operating normally
    CAUTION = "caution"         # Some concerns, increased monitoring
    WARNING = "warning"         # Significant degradation detected
    CRITICAL = "critical"       # Approaching minimum viable state
    EMERGENCY = "emergency"     # Only essential functions remain


@dataclass
class SafetyCheck:
    """
    Result of a safety check.
    
    Attributes:
        timestamp: When the check was performed
        status: Current safety status
        message: Description of the check result
        active_count: Number of active capabilities
        essential_count: Number of essential capabilities remaining
        intervention_needed: Whether safety intervention is required
    """
    timestamp: float
    status: SafetyStatus
    message: str
    active_count: int
    essential_count: int
    intervention_needed: bool


class SafetyLayer:
    """
    Safety mechanism to prevent total system collapse.
    
    The safety layer:
    1. Protects essential capabilities from degradation
    2. Monitors system health and intervenes when critical
    3. Ensures at least one minimal behavior always remains
    4. Prevents the system from crashing
    """
    
    # Minimum number of capabilities that must remain
    MIN_CAPABILITIES = 1
    
    # Health thresholds for different safety statuses
    THRESHOLDS = {
        SafetyStatus.NORMAL: 60.0,
        SafetyStatus.CAUTION: 40.0,
        SafetyStatus.WARNING: 25.0,
        SafetyStatus.CRITICAL: 10.0,
        SafetyStatus.EMERGENCY: 5.0,
    }
    
    def __init__(self, registry: CapabilityRegistry):
        """
        Initialize the safety layer.
        
        Args:
            registry: The capability registry to protect
        """
        self._registry = registry
        self._logger = logging.getLogger("lethe.safety")
        self._check_history: List[SafetyCheck] = []
        self._interventions: int = 0
        self._last_check_time: float = 0
        self._is_active: bool = True
        self._emergency_mode: bool = False
        self._fallback_function: Optional[Callable] = None
    
    @property
    def is_active(self) -> bool:
        """Check if the safety layer is active.

        Returns:
            bool: True if the safety layer is currently active.
        """
        return self._is_active
    
    @property
    def is_emergency(self) -> bool:
        """Check if the system is in emergency mode.

        Returns:
            bool: True if the system is currently in emergency mode.
        """
        return self._emergency_mode
    
    def activate(self) -> None:
        """Activate the safety layer.

        Enables safety monitoring and protection mechanisms for the system.
        """
        self._is_active = True
        self._logger.info("Safety layer activated")
    
    def deactivate(self) -> None:
        """Deactivate the safety layer (use with caution).

        Warning:
            Disabling the safety layer puts the system at risk of total collapse.
            Use only for testing or when manually managing system stability.
        """
        self._is_active = False
        self._logger.warning("Safety layer deactivated - system at risk!")
    
    def set_fallback(self, func: Callable) -> None:
        """
        Set the fallback function that runs when everything else fails.
        
        Args:
            func: The last-resort function to run
        """
        self._fallback_function = func
        self._logger.info("Fallback function configured")
    
    def get_essential_capabilities(self) -> List[str]:
        """
        Get list of all essential capabilities.
        
        Returns:
            List of essential capability names
        """
        essential = []
        for name in self._registry.list_capabilities():
            meta = self._registry.get_metadata(name)
            if meta and meta.importance == Importance.ESSENTIAL:
                essential.append(name)
        return essential
    
    def _determine_status(self, active_count: int, essential_count: int) -> SafetyStatus:
        """
        Determine the current safety status.
        
        Args:
            active_count: Number of active capabilities
            essential_count: Number of essential capabilities
            
        Returns:
            Current SafetyStatus
        """
        total = self._registry.capability_count()
        if total == 0:
            return SafetyStatus.EMERGENCY
        
        health = (active_count / total) * 100
        
        if essential_count == 0 or active_count <= self.MIN_CAPABILITIES:
            return SafetyStatus.EMERGENCY
        elif health < self.THRESHOLDS[SafetyStatus.CRITICAL]:
            return SafetyStatus.CRITICAL
        elif health < self.THRESHOLDS[SafetyStatus.WARNING]:
            return SafetyStatus.WARNING
        elif health < self.THRESHOLDS[SafetyStatus.CAUTION]:
            return SafetyStatus.CAUTION
        else:
            return SafetyStatus.NORMAL
    
    def check(self) -> SafetyCheck:
        """
        Perform a safety check on the system.
        
        Returns:
            SafetyCheck with the results
        """
        active = self._registry.list_active_capabilities()
        essential = self.get_essential_capabilities()
        active_essential = [e for e in essential if e in active]
        
        status = self._determine_status(len(active), len(active_essential))
        
        messages = {
            SafetyStatus.NORMAL: "System operating within normal parameters.",
            SafetyStatus.CAUTION: "Degradation detected. Monitoring closely.",
            SafetyStatus.WARNING: "Significant capability loss. Consider intervention.",
            SafetyStatus.CRITICAL: "Critical degradation! Minimal functionality remaining.",
            SafetyStatus.EMERGENCY: "EMERGENCY: System at minimum viable state!"
        }
        
        intervention_needed = status in (SafetyStatus.CRITICAL, SafetyStatus.EMERGENCY)
        
        check = SafetyCheck(
            timestamp=time.time(),
            status=status,
            message=messages[status],
            active_count=len(active),
            essential_count=len(active_essential),
            intervention_needed=intervention_needed
        )
        
        self._check_history.append(check)
        self._last_check_time = check.timestamp
        
        # Update emergency mode
        if status == SafetyStatus.EMERGENCY:
            if not self._emergency_mode:
                self._emergency_mode = True
                self._logger.critical("Entering emergency mode!")
        
        return check
    
    def should_allow_decay(self, capability_name: str) -> bool:
        """
        Check if a capability should be allowed to decay.
        
        Args:
            capability_name: Name of the capability to potentially decay
            
        Returns:
            True if decay should be allowed, False otherwise
        """
        if not self._is_active:
            return True
        
        meta = self._registry.get_metadata(capability_name)
        
        # Never allow essential capabilities to decay
        if meta and meta.importance == Importance.ESSENTIAL:
            self._logger.debug(f"Blocking decay of essential capability: {capability_name}")
            return False
        
        # Check if we're at minimum viable state
        active = self._registry.list_active_capabilities()
        if len(active) <= self.MIN_CAPABILITIES:
            self._logger.warning("At minimum capability count - blocking all decay")
            return False
        
        # Check if this would leave us without any non-degraded capabilities
        if len(active) <= 2 and capability_name in active:
            check = self.check()
            if check.status in (SafetyStatus.CRITICAL, SafetyStatus.EMERGENCY):
                self._logger.warning(f"Blocking decay in critical state: {capability_name}")
                return False
        
        return True
    
    def intervene(self) -> bool:
        """
        Perform a safety intervention.
        
        This is called when the system is in a critical state and needs
        to take action to prevent total collapse.
        
        Returns:
            True if intervention was successful
        """
        if not self._is_active:
            return False
        
        self._interventions += 1
        self._logger.warning(f"Safety intervention #{self._interventions}")
        
        check = self.check()
        
        if check.status == SafetyStatus.EMERGENCY:
            self._logger.critical("Emergency intervention - activating fallback")
            if self._fallback_function:
                try:
                    self._fallback_function()
                    return True
                except Exception as e:
                    self._logger.error(f"Fallback function failed: {e}")
                    return False
        
        return True
    
    def get_status(self) -> SafetyStatus:
        """Get the current safety status.

        Performs a safety check and returns the resulting status.

        Returns:
            SafetyStatus: The current safety status of the system.
        """
        check = self.check()
        return check.status
    
    def get_check_history(self) -> List[SafetyCheck]:
        """Get the complete safety check history.

        Returns:
            List[SafetyCheck]: A copy of all safety checks performed.
        """
        return self._check_history.copy()
    
    def get_recent_checks(self, count: int = 10) -> List[SafetyCheck]:
        """Get the most recent safety checks.

        Args:
            count: Maximum number of recent checks to return. Defaults to 10.

        Returns:
            List[SafetyCheck]: The most recent safety checks, up to count.
        """
        return self._check_history[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get safety statistics.
        
        Returns:
            Dictionary with safety statistics
        """
        return {
            "is_active": self._is_active,
            "is_emergency": self._emergency_mode,
            "total_interventions": self._interventions,
            "check_count": len(self._check_history),
            "current_status": self.get_status().value,
            "has_fallback": self._fallback_function is not None
        }
    
    def create_heartbeat(self) -> Callable:
        """
        Create a heartbeat function that proves the system is alive.
        
        This is the absolute minimum function that must always work.
        
        Returns:
            A simple heartbeat function
        """
        def heartbeat() -> str:
            """The most basic function - proves the system exists."""
            return "I am still here."
        
        return heartbeat
    
    def ensure_minimum_capability(self) -> None:
        """
        Ensure at least one capability exists.
        
        If no capabilities remain, registers a heartbeat as the last resort.
        """
        active = self._registry.list_active_capabilities()
        
        if len(active) == 0:
            self._logger.critical("No capabilities remain! Creating emergency heartbeat.")
            heartbeat = self.create_heartbeat()
            self._registry.register_function(
                heartbeat,
                name="emergency_heartbeat",
                importance=Importance.ESSENTIAL,
                degradation_resistance=1.0,
                description="Emergency heartbeat - last resort function"
            )
    
    def wrap_with_safety(self, func: Callable) -> Callable:
        """
        Wrap a function with safety exception handling.
        
        Args:
            func: The function to wrap
            
        Returns:
            Wrapped function that won't crash the system
        """
        def safe_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self._logger.error(f"Caught exception in {func.__name__}: {e}")
                return None
        
        safe_wrapper.__name__ = f"safe_{func.__name__}"
        safe_wrapper.__doc__ = f"Safety-wrapped version of {func.__name__}"
        return safe_wrapper
