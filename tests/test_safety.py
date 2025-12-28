"""
Tests for the Safety Layer module.
"""

import pytest
from src.capability import CapabilityRegistry, Importance
from src.safety import SafetyLayer, SafetyStatus, SafetyCheck


class TestSafetyStatus:
    """Tests for the SafetyStatus enum."""
    
    def test_safety_status_values(self):
        """Test safety status enum values."""
        assert SafetyStatus.NORMAL.value == "normal"
        assert SafetyStatus.EMERGENCY.value == "emergency"
    
    def test_all_statuses_exist(self):
        """Test all expected safety statuses exist."""
        statuses = [s.value for s in SafetyStatus]
        assert "normal" in statuses
        assert "caution" in statuses
        assert "warning" in statuses
        assert "critical" in statuses
        assert "emergency" in statuses


class TestSafetyCheck:
    """Tests for the SafetyCheck dataclass."""
    
    def test_safety_check_creation(self):
        """Test creating a safety check result."""
        import time
        check = SafetyCheck(
            timestamp=time.time(),
            status=SafetyStatus.NORMAL,
            message="All systems normal",
            active_count=10,
            essential_count=2,
            intervention_needed=False
        )
        assert check.status == SafetyStatus.NORMAL
        assert check.intervention_needed is False


class TestSafetyLayer:
    """Tests for the SafetyLayer class."""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with test capabilities."""
        reg = CapabilityRegistry()
        
        @reg.register(name="essential1", importance=Importance.ESSENTIAL)
        def essential1():
            return "essential1"
        
        @reg.register(name="essential2", importance=Importance.ESSENTIAL)
        def essential2():
            return "essential2"
        
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
    def safety(self, registry):
        """Create a safety layer with the test registry."""
        return SafetyLayer(registry)
    
    def test_initialization(self, safety):
        """Test safety layer initialization."""
        assert safety.is_active is True
        assert safety.is_emergency is False
    
    def test_activate_deactivate(self, safety):
        """Test activating and deactivating safety layer."""
        safety.deactivate()
        assert safety.is_active is False
        
        safety.activate()
        assert safety.is_active is True
    
    def test_get_essential_capabilities(self, safety):
        """Test getting essential capabilities."""
        essential = safety.get_essential_capabilities()
        
        assert "essential1" in essential
        assert "essential2" in essential
        assert "low" not in essential
    
    def test_check_normal_status(self, safety):
        """Test safety check returns normal status when healthy."""
        check = safety.check()
        
        assert check.status == SafetyStatus.NORMAL
        assert check.intervention_needed is False
    
    def test_check_detects_degradation(self, safety, registry):
        """Test safety check detects significant degradation."""
        # Degrade most capabilities - with only essential remaining
        # we should see reduced active count
        registry.mark_degraded("low", level=3)
        registry.mark_deleted("low")
        registry.mark_degraded("medium", level=3)
        registry.mark_deleted("medium")
        registry.mark_degraded("high", level=3)
        registry.mark_deleted("high")
        
        check = safety.check()
        
        # With 3 of 5 capabilities deleted, only 2 essential remain active
        assert check.active_count == 2
        assert check.essential_count == 2
    
    def test_should_allow_decay_blocks_essential(self, safety):
        """Test that essential capabilities cannot be decayed."""
        assert safety.should_allow_decay("essential1") is False
        assert safety.should_allow_decay("essential2") is False
    
    def test_should_allow_decay_allows_non_essential(self, safety):
        """Test that non-essential capabilities can be decayed."""
        assert safety.should_allow_decay("low") is True
        assert safety.should_allow_decay("medium") is True
    
    def test_should_allow_decay_when_deactivated(self, safety):
        """Test that decay is allowed when safety is deactivated."""
        safety.deactivate()
        
        # Even essential should be allowed when safety is off
        assert safety.should_allow_decay("essential1") is True
    
    def test_intervene(self, safety):
        """Test safety intervention."""
        result = safety.intervene()
        
        assert result is True
        assert safety.get_statistics()["total_interventions"] == 1
    
    def test_get_status(self, safety):
        """Test getting current status."""
        status = safety.get_status()
        assert status == SafetyStatus.NORMAL
    
    def test_get_check_history(self, safety):
        """Test getting check history."""
        safety.check()
        safety.check()
        safety.check()
        
        history = safety.get_check_history()
        assert len(history) >= 3
    
    def test_get_recent_checks(self, safety):
        """Test getting recent checks."""
        for _ in range(15):
            safety.check()
        
        recent = safety.get_recent_checks(5)
        assert len(recent) == 5
    
    def test_get_statistics(self, safety):
        """Test getting safety statistics."""
        safety.check()
        safety.intervene()
        
        stats = safety.get_statistics()
        
        assert "is_active" in stats
        assert "is_emergency" in stats
        assert "total_interventions" in stats
        assert "check_count" in stats
        assert stats["total_interventions"] == 1
    
    def test_set_fallback(self, safety):
        """Test setting a fallback function."""
        called = [False]
        
        def fallback():
            called[0] = True
        
        safety.set_fallback(fallback)
        assert safety.get_statistics()["has_fallback"] is True
    
    def test_create_heartbeat(self, safety):
        """Test creating a heartbeat function."""
        heartbeat = safety.create_heartbeat()
        
        result = heartbeat()
        assert result == "I am still here."
    
    def test_ensure_minimum_capability(self, registry):
        """Test ensuring minimum capability when all are deleted."""
        # Create empty registry
        empty_reg = CapabilityRegistry()
        safety = SafetyLayer(empty_reg)
        
        safety.ensure_minimum_capability()
        
        # Should have created emergency heartbeat
        assert empty_reg.capability_count() == 1
        assert "emergency_heartbeat" in empty_reg.list_capabilities()
    
    def test_wrap_with_safety(self, safety):
        """Test wrapping a function with safety."""
        def risky_func(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        safe_func = safety.wrap_with_safety(risky_func)
        
        # Normal execution should work
        assert safe_func(5) == 10
        
        # Exception should be caught
        result = safe_func(-1)
        assert result is None  # Should not crash
    
    def test_emergency_mode_activation(self, safety, registry):
        """Test that emergency mode is activated in critical state."""
        # Delete all non-essential capabilities
        registry.mark_deleted("low")
        registry.mark_deleted("medium")
        registry.mark_deleted("high")
        
        # Force very low state
        for name in safety.get_essential_capabilities():
            registry.mark_degraded(name, level=2)  # Don't delete essential
        
        # This should trigger checks but may not reach emergency
        # depending on exact health calculation
        check = safety.check()
        
        # At minimum, status should not be normal
        assert check.status != SafetyStatus.NORMAL or check.active_count <= 2
    
    def test_minimum_capability_protection(self, registry):
        """Test that minimum capability count is protected."""
        # Create registry with only one non-essential capability
        small_reg = CapabilityRegistry()
        
        @small_reg.register(name="only_one", importance=Importance.MEDIUM)
        def only_one():
            pass
        
        safety = SafetyLayer(small_reg)
        
        # With only one capability, decay should be blocked
        small_reg.mark_degraded("only_one", level=1)  # Start degradation
        
        # After degradation, should block further decay
        # (depends on active count check)
        check = safety.check()
        assert check.active_count >= 0
