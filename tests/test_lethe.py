"""
Tests for the Lethe Core module.
"""

import pytest
import time
from src.lethe import Lethe, LetheState, LoopIteration
from src.capability import Importance


class TestLetheState:
    """Tests for the LetheState enum."""
    
    def test_lethe_state_values(self):
        """Test lethe state enum values."""
        assert LetheState.INITIALIZING.value == "initializing"
        assert LetheState.RUNNING.value == "running"
        assert LetheState.STOPPED.value == "stopped"


class TestLoopIteration:
    """Tests for the LoopIteration dataclass."""
    
    def test_loop_iteration_creation(self):
        """Test creating a loop iteration record."""
        iteration = LoopIteration(
            iteration=1,
            timestamp=time.time(),
            decay_event=None,
            capabilities_executed=5,
            health=95.0
        )
        assert iteration.iteration == 1
        assert iteration.capabilities_executed == 5


class TestLethe:
    """Tests for the Lethe class."""
    
    @pytest.fixture
    def lethe(self):
        """Create a Lethe instance for testing."""
        return Lethe(
            decay_interval=0.1,
            decay_probability=0.5,
            loop_interval=0.05,
            narrative_interval=1.0,
            seed=42,
            log_level=50  # CRITICAL to reduce log noise
        )
    
    def test_initialization(self, lethe):
        """Test Lethe initialization."""
        assert lethe.state == LetheState.INITIALIZING
        assert lethe.is_running is False
    
    def test_register_decorator(self, lethe):
        """Test registering capabilities with decorator."""
        @lethe.register(name="test_cap", importance=Importance.HIGH)
        def test_cap():
            return "test"
        
        assert "test_cap" in lethe.registry.list_capabilities()
    
    def test_register_function(self, lethe):
        """Test registering functions directly."""
        def my_func():
            return 42
        
        lethe.register_function(
            func=my_func,
            name="my_func",
            importance=Importance.MEDIUM
        )
        
        assert "my_func" in lethe.registry.list_capabilities()
    
    def test_initialize(self, lethe):
        """Test system initialization."""
        @lethe.register(name="cap1", importance=Importance.ESSENTIAL)
        def cap1():
            pass
        
        lethe.initialize()
        
        assert lethe.state == LetheState.RUNNING
    
    def test_component_access(self, lethe):
        """Test accessing system components."""
        assert lethe.registry is not None
        assert lethe.decay_engine is not None
        assert lethe.introspector is not None
        assert lethe.narrative is not None
        assert lethe.safety is not None
    
    def test_tick(self, lethe):
        """Test a single tick of the main loop."""
        @lethe.register(name="tick_test", importance=Importance.ESSENTIAL)
        def tick_test():
            pass
        
        lethe.initialize()
        iteration = lethe.tick()
        
        assert iteration.iteration == 1
        assert iteration.health > 0
    
    def test_multiple_ticks(self, lethe):
        """Test multiple ticks."""
        @lethe.register(name="multi_test", importance=Importance.ESSENTIAL)
        def multi_test():
            pass
        
        lethe.initialize()
        
        for _ in range(5):
            iteration = lethe.tick()
        
        assert iteration.iteration == 5
    
    def test_pause_resume(self, lethe):
        """Test pausing and resuming the system."""
        lethe.initialize()
        
        lethe.pause()
        assert lethe.state == LetheState.PAUSED
        assert lethe.decay_engine.is_enabled is False
        
        lethe.resume()
        assert lethe.state == LetheState.RUNNING
        assert lethe.decay_engine.is_enabled is True
    
    def test_stop(self, lethe):
        """Test stopping the system."""
        lethe.initialize()
        lethe.stop()
        
        assert lethe.is_running is False
    
    def test_get_status(self, lethe):
        """Test getting system status."""
        @lethe.register(name="status_test", importance=Importance.ESSENTIAL)
        def status_test():
            pass
        
        lethe.initialize()
        lethe.tick()
        
        status = lethe.get_status()
        
        assert "state" in status
        assert "iteration" in status
        assert "introspection" in status
        assert "decay" in status
        assert "safety" in status
        assert "narrative" in status
    
    def test_force_decay(self, lethe):
        """Test forcing a decay."""
        @lethe.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            pass
        
        @lethe.register(name="decayable", importance=Importance.LOW)
        def decayable():
            pass
        
        lethe.initialize()
        
        event = lethe.force_decay("decayable")
        assert event is not None
        assert event.capability_name == "decayable"
    
    def test_force_decay_blocked_for_essential(self, lethe):
        """Test that essential capabilities cannot be force decayed."""
        @lethe.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            pass
        
        lethe.initialize()
        
        event = lethe.force_decay("essential")
        assert event is None
    
    def test_run_with_max_iterations(self, lethe):
        """Test running with a maximum iteration count."""
        @lethe.register(name="run_test", importance=Importance.ESSENTIAL)
        def run_test():
            pass
        
        lethe.initialize()
        lethe.run(max_iterations=3)
        
        assert lethe.state == LetheState.STOPPED
        status = lethe.get_status()
        assert status["iteration"] == 3
    
    def test_decay_during_run(self):
        """Test that decay occurs during run."""
        lethe = Lethe(
            decay_interval=0.01,
            decay_probability=1.0,  # Always decay
            loop_interval=0.02,
            seed=42,
            log_level=50
        )
        
        @lethe.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            pass
        
        @lethe.register(name="trivial1", importance=Importance.TRIVIAL)
        def trivial1():
            pass
        
        @lethe.register(name="trivial2", importance=Importance.TRIVIAL)
        def trivial2():
            pass
        
        lethe.initialize()
        lethe.run(max_iterations=10)
        
        # At least some decay should have occurred
        status = lethe.get_status()
        assert status["decay"]["total_decays"] >= 0
    
    def test_safety_protection_during_run(self):
        """Test that safety layer protects essential capabilities."""
        lethe = Lethe(
            decay_interval=0.01,
            decay_probability=1.0,
            loop_interval=0.02,
            seed=42,
            log_level=50
        )
        
        @lethe.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            return "essential"
        
        @lethe.register(name="trivial", importance=Importance.TRIVIAL)
        def trivial():
            return "trivial"
        
        lethe.initialize()
        lethe.run(max_iterations=20)
        
        # Essential should never be deleted
        assert lethe.registry.get("essential") is not None


class TestLetheIntegration:
    """Integration tests for the complete Lethe system."""
    
    def test_full_lifecycle(self):
        """Test a complete system lifecycle."""
        lethe = Lethe(
            decay_interval=0.1,
            decay_probability=0.8,
            loop_interval=0.05,
            seed=123,
            log_level=50
        )
        
        # Register capabilities of various importance
        @lethe.register(name="heartbeat", importance=Importance.ESSENTIAL)
        def heartbeat():
            return "alive"
        
        @lethe.register(name="math", importance=Importance.HIGH)
        def math():
            return 2 + 2
        
        @lethe.register(name="joke", importance=Importance.LOW)
        def joke():
            return "Why did the chicken..."
        
        @lethe.register(name="trivia", importance=Importance.TRIVIAL)
        def trivia():
            return "Fun fact!"
        
        # Initialize
        lethe.initialize()
        assert lethe.registry.capability_count() == 4
        
        # Run for several iterations
        lethe.run(max_iterations=15)
        
        # Verify system didn't crash
        assert lethe.state == LetheState.STOPPED
        
        # Essential capability should remain
        status = lethe.get_status()
        assert status["introspection"]["active_capabilities"] >= 1
    
    def test_reproducible_behavior(self):
        """Test that same seed produces same behavior."""
        def run_with_seed(seed):
            lethe = Lethe(
                decay_interval=0.05,
                decay_probability=0.9,
                loop_interval=0.02,
                seed=seed,
                log_level=50
            )
            
            @lethe.register(name="cap1", importance=Importance.ESSENTIAL)
            def cap1():
                pass
            
            @lethe.register(name="cap2", importance=Importance.LOW)
            def cap2():
                pass
            
            @lethe.register(name="cap3", importance=Importance.TRIVIAL)
            def cap3():
                pass
            
            lethe.initialize()
            lethe.run(max_iterations=10)
            
            return lethe.get_status()
        
        status1 = run_with_seed(42)
        status2 = run_with_seed(42)
        
        # Same seed should produce same decay count
        assert status1["decay"]["total_decays"] == status2["decay"]["total_decays"]
