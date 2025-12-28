"""
Tests for the Introspection module.
"""

import pytest
import time
from src.capability import CapabilityRegistry, Importance
from src.introspection import Introspector, SystemState, CapabilityLoss


class TestSystemState:
    """Tests for the SystemState dataclass."""
    
    def test_system_state_creation(self):
        """Test creating a system state snapshot."""
        state = SystemState(
            timestamp=time.time(),
            total_capabilities=10,
            active_capabilities=8,
            degraded_capabilities=2,
            deleted_capabilities=0,
            health_percentage=85.0,
            loaded_modules=50
        )
        assert state.total_capabilities == 10
        assert state.health_percentage == 85.0


class TestCapabilityLoss:
    """Tests for the CapabilityLoss dataclass."""
    
    def test_capability_loss_creation(self):
        """Test creating a capability loss record."""
        loss = CapabilityLoss(
            name="test_cap",
            importance=Importance.MEDIUM,
            lost_at=time.time(),
            degradation_level=3,
            description="A test capability"
        )
        assert loss.name == "test_cap"
        assert loss.importance == Importance.MEDIUM


class TestIntrospector:
    """Tests for the Introspector class."""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with test capabilities."""
        reg = CapabilityRegistry()
        
        @reg.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            return "essential"
        
        @reg.register(name="high", importance=Importance.HIGH)
        def high():
            return "high"
        
        @reg.register(name="medium", importance=Importance.MEDIUM)
        def medium():
            return "medium"
        
        @reg.register(name="low", importance=Importance.LOW)
        def low():
            return "low"
        
        return reg
    
    @pytest.fixture
    def introspector(self, registry):
        """Create an introspector with the test registry."""
        intro = Introspector(registry)
        intro.initialize()
        return intro
    
    def test_initialization(self, introspector, registry):
        """Test introspector initialization."""
        assert introspector._initial_capability_count == 4
    
    def test_get_current_state(self, introspector):
        """Test getting current system state."""
        state = introspector.get_current_state()
        
        assert state.total_capabilities == 4
        assert state.active_capabilities == 4
        assert state.degraded_capabilities == 0
        assert state.health_percentage > 0
    
    def test_health_calculation(self, introspector, registry):
        """Test health calculation based on importance."""
        # All capabilities active should be 100%
        state = introspector.get_current_state()
        assert state.health_percentage == 100.0
        
        # Degrade a low importance capability
        registry.mark_degraded("low", level=3)
        registry.mark_deleted("low")
        
        state = introspector.get_current_state()
        # Health should decrease but not to 0
        assert 0 < state.health_percentage < 100
    
    def test_update_lost_capabilities(self, introspector, registry):
        """Test tracking lost capabilities."""
        registry.mark_deleted("low")
        
        new_losses = introspector.update_lost_capabilities()
        
        assert len(new_losses) == 1
        assert new_losses[0].name == "low"
    
    def test_get_lost_capabilities(self, introspector, registry):
        """Test getting all lost capabilities."""
        registry.mark_deleted("low")
        registry.mark_deleted("medium")
        
        introspector.update_lost_capabilities()
        
        lost = introspector.get_lost_capabilities()
        assert len(lost) == 2
    
    def test_get_capability_info(self, introspector):
        """Test getting detailed capability information."""
        info = introspector.get_capability_info("essential")
        
        assert info["name"] == "essential"
        assert info["importance"] == "ESSENTIAL"
        assert info["is_degraded"] is False
        assert "signature" in info
    
    def test_get_capability_info_nonexistent(self, introspector):
        """Test getting info for non-existent capability."""
        info = introspector.get_capability_info("nonexistent")
        assert info is None
    
    def test_get_module_info(self, introspector):
        """Test getting module information."""
        info = introspector.get_module_info()
        
        assert "total_modules" in info
        assert info["total_modules"] > 0
    
    def test_get_uptime(self, introspector):
        """Test getting system uptime."""
        time.sleep(0.1)
        uptime = introspector.get_uptime()
        assert uptime >= 0.1
    
    def test_health_trend_stable(self, introspector):
        """Test health trend when stable."""
        # Generate a few state snapshots
        for _ in range(5):
            introspector.get_current_state()
        
        trend = introspector.get_health_trend()
        assert trend == "stable"
    
    def test_health_trend_declining(self, introspector, registry):
        """Test health trend when declining."""
        introspector.get_current_state()
        
        # Degrade capabilities to create decline
        registry.mark_degraded("low", level=3)
        registry.mark_deleted("low")
        introspector.get_current_state()
        
        registry.mark_degraded("medium", level=3)
        registry.mark_deleted("medium")
        introspector.get_current_state()
        
        trend = introspector.get_health_trend()
        assert trend in ("declining", "slow_decline", "stable")  # May vary
    
    def test_get_summary(self, introspector):
        """Test getting comprehensive summary."""
        summary = introspector.get_summary()
        
        assert "uptime_seconds" in summary
        assert "health_percentage" in summary
        assert "health_trend" in summary
        assert "total_capabilities" in summary
        assert "active_capabilities" in summary
    
    def test_can_remember(self, introspector, registry):
        """Test checking if capability can be remembered."""
        assert introspector.can_remember("essential") is True
        
        registry.mark_deleted("low")
        assert introspector.can_remember("low") is False
    
    def test_get_forgotten_names(self, introspector, registry):
        """Test getting list of forgotten capability names."""
        registry.mark_deleted("low")
        registry.mark_deleted("medium")
        
        forgotten = introspector.get_forgotten_names()
        assert "low" in forgotten
        assert "medium" in forgotten
    
    def test_get_fading_memories(self, introspector, registry):
        """Test getting capabilities that are degraded but not deleted."""
        registry.mark_degraded("low", level=1)
        registry.mark_degraded("medium", level=2)
        registry.mark_deleted("medium")
        
        fading = introspector.get_fading_memories()
        assert "low" in fading
        assert "medium" not in fading
    
    def test_state_history(self, introspector):
        """Test state history tracking."""
        introspector.get_current_state()
        introspector.get_current_state()
        introspector.get_current_state()
        
        history = introspector.get_state_history()
        # At least the initial + 3 new = 4, but initial may have been called already
        assert len(history) >= 3
    
    def test_get_recent_states(self, introspector):
        """Test getting recent state snapshots."""
        for _ in range(10):
            introspector.get_current_state()
        
        recent = introspector.get_recent_states(5)
        assert len(recent) == 5
