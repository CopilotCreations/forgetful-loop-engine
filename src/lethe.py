"""
Lethe Core Module

This module provides the main orchestrator that ties together all components
of the Lethe system: capability registry, decay engine, introspection,
narrative logging, and safety layer.
"""

import logging
import time
import signal
import sys
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

from .capability import CapabilityRegistry, Importance
from .decay_engine import DecayEngine, DecayEvent
from .introspection import Introspector
from .narrative import NarrativeLogger
from .safety import SafetyLayer


class LetheState(Enum):
    """Possible states of the Lethe system."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    DEGRADING = "degrading"
    CRITICAL = "critical"
    STOPPED = "stopped"


@dataclass
class LoopIteration:
    """
    Record of a single main loop iteration.
    
    Attributes:
        iteration: Iteration number
        timestamp: When the iteration occurred
        decay_event: Any decay that happened, or None
        capabilities_executed: Number of capabilities run
        health: System health at end of iteration
    """
    iteration: int
    timestamp: float
    decay_event: Optional[DecayEvent]
    capabilities_executed: int
    health: float


class Lethe:
    """
    The Lethe system - a self-degrading cognitive simulation.
    
    Lethe orchestrates all components to create a system that gradually
    forgets its own functionality while maintaining stability and
    narrating its own cognitive decline.
    """
    
    def __init__(
        self,
        decay_interval: float = 5.0,
        decay_probability: float = 0.4,
        loop_interval: float = 2.0,
        narrative_interval: float = 10.0,
        seed: Optional[int] = None,
        log_level: int = logging.INFO
    ):
        """
        Initialize the Lethe system.
        
        Args:
            decay_interval: Seconds between decay attempts
            decay_probability: Probability of decay per interval
            loop_interval: Seconds between main loop iterations
            narrative_interval: Seconds between narrative outputs
            seed: Random seed for reproducible behavior
            log_level: Logging level
        """
        # Configure logging
        self._setup_logging(log_level)
        self._logger = logging.getLogger("lethe.core")
        
        # Initialize components
        self._registry = CapabilityRegistry()
        self._decay_engine = DecayEngine(
            self._registry,
            decay_interval=decay_interval,
            decay_probability=decay_probability,
            seed=seed
        )
        self._introspector = Introspector(self._registry)
        self._narrative = NarrativeLogger(self._introspector, seed=seed)
        self._safety = SafetyLayer(self._registry)
        
        # Configuration
        self._loop_interval = loop_interval
        self._narrative_interval = narrative_interval
        
        # State tracking
        self._state = LetheState.INITIALIZING
        self._iteration_count = 0
        self._last_narrative_time = 0.0
        self._iterations: List[LoopIteration] = []
        self._running = False
        self._start_time: float = 0.0
        
        # Set up signal handlers for graceful shutdown
        self._setup_signals()
        
        self._logger.info("Lethe system initialized")
    
    def _setup_logging(self, level: int) -> None:
        """Configure logging for the Lethe system."""
        logging.basicConfig(
            level=level,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _setup_signals(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self._logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._running = False
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except (ValueError, OSError):
            # Signal handling may not work in all contexts
            pass
    
    @property
    def registry(self) -> CapabilityRegistry:
        """Get the capability registry."""
        return self._registry
    
    @property
    def decay_engine(self) -> DecayEngine:
        """Get the decay engine."""
        return self._decay_engine
    
    @property
    def introspector(self) -> Introspector:
        """Get the introspector."""
        return self._introspector
    
    @property
    def narrative(self) -> NarrativeLogger:
        """Get the narrative logger."""
        return self._narrative
    
    @property
    def safety(self) -> SafetyLayer:
        """Get the safety layer."""
        return self._safety
    
    @property
    def state(self) -> LetheState:
        """Get the current system state."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Check if the system is running."""
        return self._running
    
    def register(
        self,
        name: str,
        importance: Importance = Importance.MEDIUM,
        dependencies: Optional[List[str]] = None,
        degradation_resistance: float = 0.5,
        description: str = ""
    ) -> Callable:
        """
        Decorator to register a capability with Lethe.
        
        Args:
            name: Unique identifier for this capability
            importance: How critical this capability is
            dependencies: Other capabilities this one depends on
            degradation_resistance: How much this resists decay (0.0-1.0)
            description: Human-readable description
            
        Returns:
            Decorator function
        """
        return self._registry.register(
            name=name,
            importance=importance,
            dependencies=dependencies,
            degradation_resistance=degradation_resistance,
            description=description
        )
    
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
        Register a function as a capability.
        
        Args:
            func: The function to register
            name: Unique identifier
            importance: How critical this capability is
            dependencies: Other capabilities this one depends on
            degradation_resistance: How much this resists decay
            description: Human-readable description
        """
        self._registry.register_function(
            func=func,
            name=name,
            importance=importance,
            dependencies=dependencies,
            degradation_resistance=degradation_resistance,
            description=description
        )
    
    def initialize(self) -> None:
        """
        Initialize the system after all capabilities are registered.
        
        This sets up the introspector and safety layer for operation.
        """
        self._introspector.initialize()
        self._safety.ensure_minimum_capability()
        
        # Create emergency fallback
        def emergency_fallback():
            self._logger.critical("Emergency fallback activated!")
            print("LETHE: I am still here, even if barely...")
        
        self._safety.set_fallback(emergency_fallback)
        
        self._state = LetheState.RUNNING
        self._logger.info(
            f"System initialized with {self._registry.capability_count()} capabilities"
        )
    
    def _should_narrate(self) -> bool:
        """Check if it's time for a narrative output."""
        return time.time() - self._last_narrative_time >= self._narrative_interval
    
    def _execute_capabilities(self) -> int:
        """
        Execute all active capabilities once.
        
        Returns:
            Number of capabilities executed
        """
        executed = 0
        active = self._registry.list_active_capabilities()
        
        for name in active:
            try:
                func = self._registry.get(name)
                if func:
                    # Wrap with safety and execute
                    safe_func = self._safety.wrap_with_safety(func)
                    safe_func()
                    executed += 1
            except Exception as e:
                self._logger.error(f"Error executing {name}: {e}")
        
        return executed
    
    def _perform_decay(self) -> Optional[DecayEvent]:
        """
        Attempt to perform a decay operation.
        
        Returns:
            DecayEvent if decay occurred, None otherwise
        """
        # Check if decay is allowed
        target = self._decay_engine.select_target()
        if target and not self._safety.should_allow_decay(target):
            self._logger.debug(f"Safety blocked decay of: {target}")
            return None
        
        event = self._decay_engine.tick()
        
        if event:
            self._state = LetheState.DEGRADING
            # Notify narrative about the loss
            self._narrative.speak_loss(event.capability_name)
            # Update lost capabilities tracking
            self._introspector.update_lost_capabilities()
        
        return event
    
    def _check_safety(self) -> None:
        """Perform safety checks and interventions if needed."""
        check = self._safety.check()
        
        if check.intervention_needed:
            self._state = LetheState.CRITICAL
            self._safety.intervene()
    
    def tick(self) -> LoopIteration:
        """
        Perform a single main loop iteration.
        
        Returns:
            LoopIteration record
        """
        self._iteration_count += 1
        current_time = time.time()
        
        # Execute capabilities
        executed = self._execute_capabilities()
        
        # Attempt decay
        decay_event = self._perform_decay()
        
        # Check safety
        self._check_safety()
        
        # Generate narrative if needed
        if self._should_narrate():
            self._narrative.speak()
            self._last_narrative_time = current_time
        
        # Get current health
        state = self._introspector.get_current_state()
        
        iteration = LoopIteration(
            iteration=self._iteration_count,
            timestamp=current_time,
            decay_event=decay_event,
            capabilities_executed=executed,
            health=state.health_percentage
        )
        
        self._iterations.append(iteration)
        return iteration
    
    def run(self, max_iterations: Optional[int] = None) -> None:
        """
        Run the main loop indefinitely or for a set number of iterations.
        
        Args:
            max_iterations: Maximum iterations to run, or None for indefinite
        """
        self._running = True
        self._start_time = time.time()
        
        self._logger.info("Starting main loop...")
        self._narrative.speak()  # Initial narrative
        
        try:
            while self._running:
                iteration = self.tick()
                
                # Log periodic status
                if iteration.iteration % 10 == 0:
                    summary = self._introspector.get_summary()
                    self._logger.info(
                        f"Iteration {iteration.iteration}: "
                        f"Health={summary['health_percentage']:.1f}%, "
                        f"Active={summary['active_capabilities']}, "
                        f"Lost={summary['deleted_capabilities']}"
                    )
                
                # Check for max iterations
                if max_iterations and iteration.iteration >= max_iterations:
                    self._logger.info(f"Reached max iterations ({max_iterations})")
                    break
                
                # Sleep until next iteration
                time.sleep(self._loop_interval)
        
        except KeyboardInterrupt:
            self._logger.info("Interrupted by user")
        
        finally:
            self._running = False
            self._state = LetheState.STOPPED
            self._shutdown()
    
    def _shutdown(self) -> None:
        """Perform graceful shutdown."""
        self._logger.info("Shutting down Lethe system...")
        
        # Final narrative
        self._narrative.speak()
        
        # Log final statistics
        summary = self._introspector.get_summary()
        decay_stats = self._decay_engine.get_statistics()
        
        self._logger.info("=== Final System State ===")
        self._logger.info(f"Uptime: {summary['uptime_seconds']:.1f} seconds")
        self._logger.info(f"Total iterations: {self._iteration_count}")
        self._logger.info(f"Final health: {summary['health_percentage']:.1f}%")
        self._logger.info(f"Capabilities lost: {summary['deleted_capabilities']}")
        self._logger.info(f"Total decay events: {decay_stats['total_decays']}")
        
        self._logger.info("Goodbye.")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dictionary with system status
        """
        summary = self._introspector.get_summary()
        decay_stats = self._decay_engine.get_statistics()
        safety_stats = self._safety.get_statistics()
        mood = self._narrative.get_mood_summary()
        
        return {
            "state": self._state.value,
            "iteration": self._iteration_count,
            "running": self._running,
            "uptime": time.time() - self._start_time if self._start_time else 0,
            "introspection": summary,
            "decay": decay_stats,
            "safety": safety_stats,
            "narrative": mood
        }
    
    def pause(self) -> None:
        """Pause the decay engine."""
        self._decay_engine.disable()
        self._state = LetheState.PAUSED
        self._logger.info("System paused")
    
    def resume(self) -> None:
        """Resume the decay engine."""
        self._decay_engine.enable()
        self._state = LetheState.RUNNING
        self._logger.info("System resumed")
    
    def stop(self) -> None:
        """Stop the system."""
        self._running = False
    
    def force_decay(self, name: Optional[str] = None) -> Optional[DecayEvent]:
        """
        Force an immediate decay.
        
        Args:
            name: Specific capability to decay, or None for random
            
        Returns:
            DecayEvent if decay occurred
        """
        if name and not self._safety.should_allow_decay(name):
            self._logger.warning(f"Safety blocked forced decay of: {name}")
            return None
        
        return self._decay_engine.force_decay(name)
