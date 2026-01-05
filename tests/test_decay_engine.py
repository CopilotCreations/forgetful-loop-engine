"""
Tests for the Decay Engine module.
"""

import pytest
import time
from src.capability import CapabilityRegistry, Importance
from src.decay_engine import DecayEngine, DecayEvent


class TestDecayEvent:
    """Tests for the DecayEvent dataclass."""
    
    def test_decay_event_creation(self):
        """Test creating a decay event.

        Verifies that a DecayEvent can be instantiated with all required
        fields and that the values are correctly stored.
        """
        event = DecayEvent(
            timestamp=time.time(),
            capability_name="test",
            decay_type="approximate",
            old_level=0,
            new_level=1
        )
        assert event.capability_name == "test"
        assert event.decay_type == "approximate"
        assert event.new_level > event.old_level


class TestDecayEngine:
    """Tests for the DecayEngine class."""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with test capabilities.

        Returns:
            CapabilityRegistry: A registry populated with trivial, medium,
                and essential test capabilities.
        """
        reg = CapabilityRegistry()
        
        @reg.register(name="trivial1", importance=Importance.TRIVIAL, degradation_resistance=0.1)
        def trivial1():
            return "trivial1"
        
        @reg.register(name="medium1", importance=Importance.MEDIUM, degradation_resistance=0.5)
        def medium1():
            return "medium1"
        
        @reg.register(name="essential1", importance=Importance.ESSENTIAL, degradation_resistance=1.0)
        def essential1():
            return "essential1"
        
        return reg
    
    @pytest.fixture
    def engine(self, registry):
        """Create a decay engine with the test registry.

        Args:
            registry: The test capability registry fixture.

        Returns:
            DecayEngine: A configured decay engine with short intervals
                for testing purposes.
        """
        return DecayEngine(registry, decay_interval=0.1, decay_probability=0.5, seed=42)
    
    def test_engine_initialization(self, engine):
        """Test engine initializes correctly.

        Args:
            engine: The decay engine fixture.
        """
        assert engine.decay_interval == 0.1
        assert engine.decay_probability == 0.5
        assert engine.is_enabled is True
    
    def test_enable_disable(self, engine):
        """Test enabling and disabling the engine.

        Args:
            engine: The decay engine fixture.
        """
        engine.disable()
        assert engine.is_enabled is False
        
        engine.enable()
        assert engine.is_enabled is True
    
    def test_should_decay_when_disabled(self, engine):
        """Test that decay doesn't occur when disabled.

        Args:
            engine: The decay engine fixture.
        """
        engine.disable()
        # Wait past the interval
        time.sleep(0.15)
        assert engine.should_decay() is False
    
    def test_select_target_prefers_trivial(self, engine):
        """Test that target selection prefers lower importance.

        Runs multiple selections and verifies that trivial capabilities
        are selected more frequently than higher importance ones.

        Args:
            engine: The decay engine fixture.
        """
        # Run multiple selections and count
        trivial_count = 0
        total = 100
        
        for _ in range(total):
            target = engine.select_target()
            if target == "trivial1":
                trivial_count += 1
        
        # Trivial should be selected more often
        assert trivial_count > total * 0.4
    
    def test_select_target_excludes_essential(self, engine):
        """Test that essential capabilities are never selected.

        Args:
            engine: The decay engine fixture.
        """
        for _ in range(100):
            target = engine.select_target()
            assert target != "essential1"
    
    def test_create_approximation(self, engine, registry):
        """Test creating an approximated function.

        Verifies that an approximated function produces varied results
        when configured with a 100% error rate.

        Args:
            engine: The decay engine fixture.
            registry: The capability registry fixture.
        """
        original = lambda: 100
        approx = engine.create_approximation(original, error_rate=1.0)  # Always error
        
        # With 100% error rate, result should differ
        results = set()
        for _ in range(10):
            results.add(approx())
        
        # Should have some variation
        assert len(results) > 1 or 100 not in results
    
    def test_create_stub(self, engine):
        """Test creating stub functions.

        Verifies that stubs return appropriate default values for
        different return types (int, str, list, None).

        Args:
            engine: The decay engine fixture.
        """
        stub_int = engine.create_stub("test", int)
        stub_str = engine.create_stub("test", str)
        stub_list = engine.create_stub("test", list)
        stub_none = engine.create_stub("test", None)
        
        assert stub_int() == 0
        assert stub_str() == ""
        assert stub_list() == []
        assert stub_none() is None
    
    def test_apply_decay_progression(self, engine, registry):
        """Test decay progression through levels.

        Verifies the decay sequence: approximate -> stub -> delete -> None.

        Args:
            engine: The decay engine fixture.
            registry: The capability registry fixture.
        """
        # First decay - should approximate
        event1 = engine.apply_decay("trivial1")
        assert event1.decay_type == "approximate"
        assert event1.new_level == 1
        
        # Second decay - should stub
        event2 = engine.apply_decay("trivial1")
        assert event2.decay_type == "stub"
        assert event2.new_level == 2
        
        # Third decay - should delete
        event3 = engine.apply_decay("trivial1")
        assert event3.decay_type == "delete"
        assert event3.new_level == 3
        
        # Fourth decay - should return None (already deleted)
        event4 = engine.apply_decay("trivial1")
        assert event4 is None
    
    def test_apply_decay_blocks_essential(self, engine):
        """Test that essential capabilities cannot be decayed.

        Args:
            engine: The decay engine fixture.
        """
        event = engine.apply_decay("essential1")
        assert event is None
    
    def test_get_history(self, engine):
        """Test getting decay history.

        Args:
            engine: The decay engine fixture.
        """
        engine.apply_decay("trivial1")
        engine.apply_decay("medium1")
        
        history = engine.get_history()
        assert len(history) == 2
    
    def test_get_recent_history(self, engine):
        """Test getting recent decay history.

        Args:
            engine: The decay engine fixture.
        """
        engine.apply_decay("trivial1")
        engine.apply_decay("trivial1")
        engine.apply_decay("medium1")
        
        recent = engine.get_recent_history(2)
        assert len(recent) == 2
    
    def test_get_statistics(self, engine):
        """Test getting decay statistics.

        Args:
            engine: The decay engine fixture.
        """
        engine.apply_decay("trivial1")  # approximate
        engine.apply_decay("trivial1")  # stub
        
        stats = engine.get_statistics()
        assert stats["total_decays"] == 2
        assert stats["approximations"] == 1
        assert stats["stubs"] == 1
    
    def test_force_decay(self, engine):
        """Test forcing an immediate decay.

        Args:
            engine: The decay engine fixture.
        """
        event = engine.force_decay("medium1")
        assert event is not None
        assert event.capability_name == "medium1"
    
    def test_force_decay_random(self, engine):
        """Test forcing decay on random target.

        Verifies that when no target is specified, a random non-essential
        capability is selected for decay.

        Args:
            engine: The decay engine fixture.
        """
        event = engine.force_decay()
        assert event is not None
        assert event.capability_name != "essential1"
    
    def test_reset(self, engine):
        """Test resetting the engine.

        Verifies that reset clears all decay history and statistics.

        Args:
            engine: The decay engine fixture.
        """
        engine.apply_decay("trivial1")
        engine.apply_decay("medium1")
        
        engine.reset()
        
        stats = engine.get_statistics()
        assert stats["total_decays"] == 0
        assert stats["history_length"] == 0
    
    def test_decay_interval_setter(self, engine):
        """Test setting decay interval with minimum.

        Verifies that the interval cannot be set below the minimum value.

        Args:
            engine: The decay engine fixture.
        """
        engine.decay_interval = 5.0
        assert engine.decay_interval == 5.0
        
        engine.decay_interval = 0.5  # Below minimum (1.0)
        assert engine.decay_interval == 1.0
    
    def test_decay_probability_setter(self, engine):
        """Test setting decay probability with clamping.

        Verifies that probability values are clamped to the range [0.0, 1.0].

        Args:
            engine: The decay engine fixture.
        """
        engine.decay_probability = 0.75
        assert engine.decay_probability == 0.75
        
        engine.decay_probability = 1.5
        assert engine.decay_probability == 1.0
        
        engine.decay_probability = -0.5
        assert engine.decay_probability == 0.0
    
    def test_tick_with_decay(self, registry):
        """Test tick method triggering decay.

        Uses a high probability engine to verify tick can trigger decay.

        Args:
            registry: The capability registry fixture.
        """
        engine = DecayEngine(registry, decay_interval=0.01, decay_probability=1.0, seed=42)
        time.sleep(0.02)
        
        event = engine.tick()
        # High probability should trigger decay
        assert event is not None or engine.select_target() is None
    
    def test_tick_no_decay_when_disabled(self, engine):
        """Test tick doesn't decay when engine disabled.

        Args:
            engine: The decay engine fixture.
        """
        engine.disable()
        time.sleep(0.15)
        
        event = engine.tick()
        assert event is None
