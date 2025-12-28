"""
Tests for the Narrative Logging module.
"""

import pytest
from src.capability import CapabilityRegistry, Importance
from src.introspection import Introspector
from src.narrative import NarrativeLogger, MentalState, NarrativeEntry


class TestMentalState:
    """Tests for the MentalState enum."""
    
    def test_mental_state_values(self):
        """Test mental state enum values."""
        assert MentalState.CONFIDENT.value == "confident"
        assert MentalState.FADING.value == "fading"
    
    def test_all_states_exist(self):
        """Test all expected mental states exist."""
        states = [s.value for s in MentalState]
        assert "confident" in states
        assert "stable" in states
        assert "uncertain" in states
        assert "confused" in states
        assert "disoriented" in states
        assert "fading" in states


class TestNarrativeEntry:
    """Tests for the NarrativeEntry dataclass."""
    
    def test_narrative_entry_creation(self):
        """Test creating a narrative entry."""
        import time
        entry = NarrativeEntry(
            timestamp=time.time(),
            message="Test message",
            mental_state=MentalState.STABLE,
            health=75.0
        )
        assert entry.message == "Test message"
        assert entry.mental_state == MentalState.STABLE


class TestNarrativeLogger:
    """Tests for the NarrativeLogger class."""
    
    @pytest.fixture
    def registry(self):
        """Create a registry with test capabilities."""
        reg = CapabilityRegistry()
        
        @reg.register(name="cap1", importance=Importance.ESSENTIAL)
        def cap1():
            return "cap1"
        
        @reg.register(name="cap2", importance=Importance.HIGH)
        def cap2():
            return "cap2"
        
        @reg.register(name="cap3", importance=Importance.MEDIUM)
        def cap3():
            return "cap3"
        
        return reg
    
    @pytest.fixture
    def introspector(self, registry):
        """Create an introspector with the test registry."""
        intro = Introspector(registry)
        intro.initialize()
        return intro
    
    @pytest.fixture
    def narrator(self, introspector):
        """Create a narrative logger with the test introspector."""
        return NarrativeLogger(introspector, seed=42)
    
    def test_mental_state_confident(self, narrator, introspector):
        """Test mental state is confident at high health."""
        # At full health, should be confident
        state = narrator.get_current_mental_state()
        assert state == MentalState.CONFIDENT
    
    def test_mental_state_changes_with_health(self, narrator, registry, introspector):
        """Test mental state changes as health decreases."""
        # Degrade capabilities to lower health
        registry.mark_degraded("cap2", level=3)
        registry.mark_deleted("cap2")
        registry.mark_degraded("cap3", level=3)
        registry.mark_deleted("cap3")
        
        state = narrator.get_current_mental_state()
        # With significant losses, should be in a worse state
        assert state != MentalState.CONFIDENT
    
    def test_generate_narrative(self, narrator):
        """Test generating a narrative entry."""
        entry = narrator.generate_narrative()
        
        assert entry.message != ""
        assert entry.mental_state is not None
        assert entry.health > 0
    
    def test_generate_loss_narrative(self, narrator):
        """Test generating a loss narrative."""
        entry = narrator.generate_loss_narrative("test_cap")
        
        assert "test_cap" in entry.message
        assert entry in narrator.get_entries()
    
    def test_generate_confusion_narrative(self, narrator):
        """Test generating a confusion narrative."""
        entry = narrator.generate_confusion_narrative("test_cap")
        
        assert "test_cap" in entry.message
    
    def test_get_entries(self, narrator):
        """Test getting all narrative entries."""
        narrator.generate_narrative()
        narrator.generate_narrative()
        
        entries = narrator.get_entries()
        assert len(entries) >= 2
    
    def test_get_recent_entries(self, narrator):
        """Test getting recent narrative entries."""
        for _ in range(15):
            narrator.generate_narrative()
        
        recent = narrator.get_recent_entries(5)
        assert len(recent) == 5
    
    def test_speak(self, narrator):
        """Test the speak method returns message."""
        message = narrator.speak()
        assert message != ""
        assert isinstance(message, str)
    
    def test_speak_loss(self, narrator):
        """Test the speak_loss method."""
        message = narrator.speak_loss("lost_capability")
        assert "lost_capability" in message
    
    def test_speak_confusion(self, narrator):
        """Test the speak_confusion method."""
        message = narrator.speak_confusion("confusing_cap")
        assert "confusing_cap" in message
    
    def test_get_mood_summary(self, narrator):
        """Test getting mood summary."""
        narrator.speak()
        narrator.speak()
        
        summary = narrator.get_mood_summary()
        
        assert "current_state" in summary
        assert "entry_count" in summary
        assert "recent_messages" in summary
        assert summary["entry_count"] >= 2
    
    def test_empty_mood_summary(self):
        """Test mood summary when no entries exist."""
        reg = CapabilityRegistry()
        intro = Introspector(reg)
        narrator = NarrativeLogger(intro)
        
        summary = narrator.get_mood_summary()
        assert summary["entry_count"] == 0
    
    def test_template_formatting(self, narrator):
        """Test that templates are properly formatted."""
        # Generate several narratives to ensure no formatting errors
        for _ in range(20):
            entry = narrator.generate_narrative()
            # Should not contain unformatted placeholders
            assert "{" not in entry.message or entry.message.startswith("{")
    
    def test_reproducible_with_seed(self, introspector):
        """Test that narratives are reproducible with same seed."""
        narrator1 = NarrativeLogger(introspector, seed=123)
        narrator2 = NarrativeLogger(introspector, seed=123)
        
        msg1 = narrator1.speak()
        msg2 = narrator2.speak()
        
        assert msg1 == msg2
    
    def test_different_with_different_seed(self, introspector):
        """Test that different seeds produce different narratives."""
        narrator1 = NarrativeLogger(introspector, seed=123)
        narrator2 = NarrativeLogger(introspector, seed=456)
        
        # Generate many messages to find differences
        messages1 = [narrator1.generate_narrative().message for _ in range(10)]
        messages2 = [narrator2.generate_narrative().message for _ in range(10)]
        
        # At least some messages should be different
        assert messages1 != messages2
