"""
Tests for the Capability Registry module.
"""

import pytest
from src.capability import (
    CapabilityRegistry,
    CapabilityMetadata,
    Importance
)


class TestImportance:
    """Tests for the Importance enum."""
    
    def test_importance_ordering(self):
        """Test that importance levels are ordered correctly."""
        assert Importance.TRIVIAL < Importance.LOW
        assert Importance.LOW < Importance.MEDIUM
        assert Importance.MEDIUM < Importance.HIGH
        assert Importance.HIGH < Importance.CRITICAL
        assert Importance.CRITICAL < Importance.ESSENTIAL
    
    def test_importance_values(self):
        """Test importance enum values."""
        assert Importance.TRIVIAL.value == 1
        assert Importance.ESSENTIAL.value == 6


class TestCapabilityMetadata:
    """Tests for the CapabilityMetadata dataclass."""
    
    def test_default_values(self):
        """Test default values for metadata."""
        meta = CapabilityMetadata(name="test")
        assert meta.name == "test"
        assert meta.importance == Importance.MEDIUM
        assert meta.dependencies == []
        assert meta.degradation_resistance == 0.5
        assert meta.is_degraded is False
        assert meta.degradation_level == 0
        assert meta.execution_count == 0
    
    def test_custom_values(self):
        """Test custom values for metadata."""
        meta = CapabilityMetadata(
            name="custom",
            importance=Importance.HIGH,
            dependencies=["dep1", "dep2"],
            degradation_resistance=0.8,
            description="A test capability"
        )
        assert meta.importance == Importance.HIGH
        assert "dep1" in meta.dependencies
        assert meta.degradation_resistance == 0.8


class TestCapabilityRegistry:
    """Tests for the CapabilityRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return CapabilityRegistry()
    
    def test_register_decorator(self, registry):
        """Test registering a capability using decorator."""
        @registry.register(
            name="test_func",
            importance=Importance.HIGH,
            description="Test function"
        )
        def test_func():
            return "result"
        
        assert "test_func" in registry.list_capabilities()
        assert registry.get("test_func") is not None
    
    def test_register_function(self, registry):
        """Test registering a function directly."""
        def my_func():
            return 42
        
        registry.register_function(
            func=my_func,
            name="my_func",
            importance=Importance.MEDIUM
        )
        
        assert "my_func" in registry.list_capabilities()
    
    def test_get_nonexistent(self, registry):
        """Test getting a non-existent capability."""
        assert registry.get("nonexistent") is None
    
    def test_execute_capability(self, registry):
        """Test executing a registered capability."""
        @registry.register(name="add_one")
        def add_one(x):
            return x + 1
        
        result = registry.execute("add_one", 5)
        assert result == 6
    
    def test_execute_nonexistent_raises(self, registry):
        """Test that executing non-existent capability raises KeyError."""
        with pytest.raises(KeyError):
            registry.execute("nonexistent")
    
    def test_execution_count_increments(self, registry):
        """Test that execution count increments on each call."""
        @registry.register(name="counter")
        def counter():
            return 1
        
        registry.execute("counter")
        registry.execute("counter")
        registry.execute("counter")
        
        meta = registry.get_metadata("counter")
        assert meta.execution_count == 3
    
    def test_list_active_capabilities(self, registry):
        """Test listing active (non-degraded) capabilities."""
        @registry.register(name="active1")
        def active1():
            pass
        
        @registry.register(name="active2")
        def active2():
            pass
        
        registry.mark_degraded("active1")
        
        active = registry.list_active_capabilities()
        assert "active2" in active
        assert "active1" not in active
    
    def test_mark_degraded(self, registry):
        """Test marking a capability as degraded."""
        @registry.register(name="to_degrade")
        def to_degrade():
            pass
        
        registry.mark_degraded("to_degrade", level=2)
        
        meta = registry.get_metadata("to_degrade")
        assert meta.is_degraded is True
        assert meta.degradation_level == 2
        assert "to_degrade" in registry.list_degraded_capabilities()
    
    def test_mark_deleted(self, registry):
        """Test marking a capability as deleted."""
        @registry.register(name="to_delete")
        def to_delete():
            pass
        
        registry.mark_deleted("to_delete")
        
        assert "to_delete" in registry.list_deleted_capabilities()
        assert registry.get("to_delete") is None
    
    def test_replace_capability(self, registry):
        """Test replacing a capability's implementation."""
        @registry.register(name="replaceable")
        def replaceable():
            return "original"
        
        def new_impl():
            return "replaced"
        
        registry.replace_capability("replaceable", new_impl)
        result = registry.execute("replaceable")
        assert result == "replaced"
    
    def test_degradation_candidates(self, registry):
        """Test getting degradation candidates."""
        @registry.register(name="essential", importance=Importance.ESSENTIAL)
        def essential():
            pass
        
        @registry.register(name="trivial", importance=Importance.TRIVIAL)
        def trivial():
            pass
        
        @registry.register(name="medium", importance=Importance.MEDIUM)
        def medium():
            pass
        
        candidates = registry.get_degradation_candidates()
        
        # Essential should never be a candidate
        assert "essential" not in candidates
        # Trivial should be first (lower importance)
        assert candidates[0] == "trivial"
    
    def test_capability_count(self, registry):
        """Test capability counting."""
        @registry.register(name="cap1")
        def cap1():
            pass
        
        @registry.register(name="cap2")
        def cap2():
            pass
        
        assert registry.capability_count() == 2
    
    def test_degradation_resistance_clamping(self, registry):
        """Test that degradation resistance is clamped to 0.0-1.0."""
        @registry.register(name="high_resist", degradation_resistance=1.5)
        def high_resist():
            pass
        
        @registry.register(name="low_resist", degradation_resistance=-0.5)
        def low_resist():
            pass
        
        assert registry.get_metadata("high_resist").degradation_resistance == 1.0
        assert registry.get_metadata("low_resist").degradation_resistance == 0.0
    
    def test_dependency_graph(self, registry):
        """Test getting the dependency graph."""
        @registry.register(name="base")
        def base():
            pass
        
        @registry.register(name="dependent", dependencies=["base"])
        def dependent():
            pass
        
        graph = registry.get_dependency_graph()
        assert "base" in graph["dependent"]
    
    def test_get_dependents(self, registry):
        """Test getting capabilities that depend on another."""
        @registry.register(name="base")
        def base():
            pass
        
        @registry.register(name="child1", dependencies=["base"])
        def child1():
            pass
        
        @registry.register(name="child2", dependencies=["base"])
        def child2():
            pass
        
        dependents = registry.get_dependents("base")
        assert "child1" in dependents
        assert "child2" in dependents
