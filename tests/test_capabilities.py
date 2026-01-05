"""
Tests for the Default Capabilities module.
"""

import pytest
from src.lethe import Lethe
from src.capability import Importance
from src.capabilities import register_default_capabilities


class TestDefaultCapabilities:
    """Tests for the default capabilities registration."""
    
    @pytest.fixture
    def lethe(self):
        """Create a Lethe instance with default capabilities.

        Returns:
            Lethe: A fully initialized Lethe instance with default capabilities
                registered and no decay during tests.
        """
        lethe = Lethe(
            decay_interval=1.0,
            decay_probability=0.0,  # No decay during tests
            loop_interval=0.1,
            seed=42,
            log_level=50
        )
        register_default_capabilities(lethe, seed=42)
        lethe.initialize()
        return lethe
    
    def test_capabilities_registered(self, lethe):
        """Test that default capabilities are registered.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        caps = lethe.registry.list_capabilities()
        
        # Should have many capabilities
        assert len(caps) > 15
    
    def test_essential_capabilities_exist(self, lethe):
        """Test that essential capabilities are registered.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        caps = lethe.registry.list_capabilities()
        
        assert "heartbeat" in caps
        assert "self_awareness" in caps
    
    def test_essential_capabilities_protected(self, lethe):
        """Test that essential capabilities have correct importance.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        meta = lethe.registry.get_metadata("heartbeat")
        assert meta.importance == Importance.ESSENTIAL
        
        meta = lethe.registry.get_metadata("self_awareness")
        assert meta.importance == Importance.ESSENTIAL
    
    def test_critical_capabilities_exist(self, lethe):
        """Test that critical capabilities are registered.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        caps = lethe.registry.list_capabilities()
        
        assert "count" in caps
        assert "time_sense" in caps
        assert "basic_arithmetic" in caps
    
    def test_trivial_capabilities_exist(self, lethe):
        """Test that trivial capabilities are registered.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        caps = lethe.registry.list_capabilities()
        
        assert "ascii_art" in caps
        assert "fortune_cookie" in caps
        assert "mood_emoji" in caps
    
    def test_heartbeat_execution(self, lethe):
        """Test heartbeat capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("heartbeat")
        assert result == "pulse"
    
    def test_self_awareness_execution(self, lethe):
        """Test self_awareness capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("self_awareness")
        assert "I think" in result
    
    def test_count_execution(self, lethe):
        """Test count capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result1 = lethe.registry.execute("count")
        result2 = lethe.registry.execute("count")
        
        assert result2 > result1
    
    def test_time_sense_execution(self, lethe):
        """Test time_sense capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("time_sense")
        assert isinstance(result, float)
        assert result > 0
    
    def test_basic_arithmetic_execution(self, lethe):
        """Test basic_arithmetic capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("basic_arithmetic")
        assert isinstance(result, int)
        assert result >= 2  # Minimum sum of two positive integers
    
    def test_remember_name_execution(self, lethe):
        """Test remember_name capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("remember_name")
        assert "Lethe" in result
    
    def test_pattern_recognition_execution(self, lethe):
        """Test pattern_recognition capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("pattern_recognition")
        assert result == 32  # Next in 1,2,4,8,16 sequence
    
    def test_joke_telling_execution(self, lethe):
        """Test joke_telling capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("joke_telling")
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_color_mixing_execution(self, lethe):
        """Test color_mixing capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("color_mixing")
        assert "=" in result
        assert "+" in result
    
    def test_temperature_conversion_execution(self, lethe):
        """Test temperature_conversion capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("temperature_conversion")
        assert "°C" in result
        assert "°F" in result
    
    def test_dice_rolling_execution(self, lethe):
        """Test dice_rolling capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("dice_rolling")
        assert "Rolled" in result
        assert "total" in result
    
    def test_ascii_art_execution(self, lethe):
        """Test ascii_art capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("ascii_art")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_fortune_cookie_execution(self, lethe):
        """Test fortune_cookie capability execution.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        result = lethe.registry.execute("fortune_cookie")
        assert isinstance(result, str)
        assert len(result) > 20
    
    def test_dependencies_set_correctly(self, lethe):
        """Test that dependencies are set correctly.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        meta = lethe.registry.get_metadata("calculate_average")
        assert "basic_arithmetic" in meta.dependencies
        
        meta = lethe.registry.get_metadata("sort_numbers")
        assert "compare" in meta.dependencies
    
    def test_degradation_resistance_varies(self, lethe):
        """Test that degradation resistance varies by importance.

        Args:
            lethe: Lethe instance fixture with default capabilities.
        """
        essential_meta = lethe.registry.get_metadata("heartbeat")
        trivial_meta = lethe.registry.get_metadata("fortune_cookie")
        
        assert essential_meta.degradation_resistance > trivial_meta.degradation_resistance
    
    def test_reproducible_random_results(self):
        """Test that same seed produces same random results.

        Creates two separate Lethe instances with the same seed and verifies
        that the generate_random capability produces identical results.
        """
        def get_random_result():
            l = Lethe(seed=42, log_level=50)
            register_default_capabilities(l, seed=42)
            l.initialize()
            return l.registry.execute("generate_random")
        
        result1 = get_random_result()
        result2 = get_random_result()
        
        assert result1 == result2
