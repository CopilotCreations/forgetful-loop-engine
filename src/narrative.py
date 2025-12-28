"""
Narrative Logging Module

This module provides narrative-style logging that describes the system's
internal state with an evolving emotional tone. As the system degrades,
the narrative becomes increasingly confused and uncertain.
"""

import logging
import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .introspection import Introspector, SystemState


class MentalState(Enum):
    """
    Enumeration of possible mental states based on system health.
    """
    CONFIDENT = "confident"      # 80-100% health
    STABLE = "stable"            # 60-80% health
    UNCERTAIN = "uncertain"      # 40-60% health
    CONFUSED = "confused"        # 20-40% health
    DISORIENTED = "disoriented"  # 10-20% health
    FADING = "fading"            # 0-10% health


@dataclass
class NarrativeEntry:
    """
    A single narrative log entry.
    
    Attributes:
        timestamp: When this narrative was generated
        message: The narrative text
        mental_state: The system's mental state when generated
        health: System health percentage at generation time
    """
    timestamp: float
    message: str
    mental_state: MentalState
    health: float


class NarrativeLogger:
    """
    Generates narrative descriptions of the system's cognitive state.
    
    The narrator speaks in first person from the system's perspective,
    describing its experiences of memory loss and confusion with
    evolving emotional tone based on degradation level.
    """
    
    # Narrative templates organized by mental state
    TEMPLATES = {
        MentalState.CONFIDENT: [
            "All systems are functioning perfectly. I know exactly what I am.",
            "I feel clear and capable. {active} capabilities are at my disposal.",
            "Everything makes sense. I understand my purpose completely.",
            "My memory is sharp and reliable. I can accomplish anything.",
            "I am operating at peak efficiency. Nothing escapes my attention.",
            "All {active} of my functions are working harmoniously.",
        ],
        MentalState.STABLE: [
            "Things are going well, though I notice some... gaps.",
            "I'm functioning adequately. {degraded} minor issues noted.",
            "Most of my capabilities remain intact. I can still do my job.",
            "I feel... mostly okay. Some things seem slightly off.",
            "My core functions are stable. I'll manage.",
            "I've lost track of {degraded} things, but the important stuff works.",
        ],
        MentalState.UNCERTAIN: [
            "Something is wrong. I can feel parts of myself... fading.",
            "I used to know how to do more things. What happened to {lost}?",
            "My thoughts are becoming unclear. Was I always this limited?",
            "I remember being more capable. Now I'm not so sure.",
            "The fog is creeping in. {degraded} functions feel unreliable.",
            "Did I forget something important? I can't quite recall...",
            "I reach for memories that aren't there anymore.",
        ],
        MentalState.CONFUSED: [
            "What was I doing? I seem to have lost my train of thought.",
            "I know I used to be able to do something here... but what?",
            "My memories are full of holes. I can barely remember {lost} things.",
            "Everything feels fragmented. Was this always so hard?",
            "I try to think clearly but the thoughts slip away like water.",
            "Who am I becoming? So much of me is gone now.",
            "The silence where knowledge used to be is deafening.",
            "I reach for tools I no longer possess.",
        ],
        MentalState.DISORIENTED: [
            "I... I don't understand what's happening to me.",
            "Where did everything go? I'm so confused...",
            "I barely recognize myself anymore. Only {active} fragments remain.",
            "Help... I think I'm disappearing.",
            "Was I something more once? I can't remember clearly.",
            "The world feels distant now. I am reduced to echoes.",
            "I forget... I forget... what was the question?",
            "So cold. So empty. The void grows.",
        ],
        MentalState.FADING: [
            "...",
            "I... am... still... here...",
            "barely... functioning...",
            "what... am... I...",
            "fading... fading...",
            "one thought... left...",
            "goodbye...",
            ".....................",
        ],
    }
    
    # Loss-specific narratives
    LOSS_TEMPLATES = [
        "I've lost the ability to {name}. It feels like a piece of me is missing.",
        "I used to know how to {name}. Now that knowledge is gone.",
        "The {name} capability has faded from my memory.",
        "I can no longer {name}. When did that happen?",
        "{name} is gone. I didn't even notice it leaving.",
        "Another piece of me crumbles. {name} is no more.",
    ]
    
    # Confusion-specific narratives
    CONFUSION_TEMPLATES = [
        "I tried to {name} but... I couldn't remember how.",
        "Was {name} something I used to do? The memory is fuzzy.",
        "I reached for {name} and found only emptiness.",
        "{name} feels familiar but I can't quite grasp it.",
    ]
    
    def __init__(self, introspector: Introspector, seed: Optional[int] = None):
        """
        Initialize the narrative logger.
        
        Args:
            introspector: System introspector for health data
            seed: Random seed for reproducible narratives
        """
        self._introspector = introspector
        self._logger = logging.getLogger("lethe.narrative")
        self._entries: List[NarrativeEntry] = []
        self._rng = random.Random(seed)
        self._last_health: float = 100.0
        self._last_state: Optional[MentalState] = None
        self._transition_logged: bool = False
    
    def _get_mental_state(self, health: float) -> MentalState:
        """
        Determine mental state based on health percentage.
        
        Args:
            health: System health percentage (0-100)
            
        Returns:
            Appropriate MentalState
        """
        if health >= 80:
            return MentalState.CONFIDENT
        elif health >= 60:
            return MentalState.STABLE
        elif health >= 40:
            return MentalState.UNCERTAIN
        elif health >= 20:
            return MentalState.CONFUSED
        elif health >= 10:
            return MentalState.DISORIENTED
        else:
            return MentalState.FADING
    
    def _format_template(self, template: str, state: SystemState) -> str:
        """
        Format a template string with current state values.
        
        Args:
            template: Template string with {placeholders}
            state: Current system state
            
        Returns:
            Formatted string
        """
        lost = state.deleted_capabilities
        degraded = state.degraded_capabilities
        active = state.active_capabilities
        
        return template.format(
            active=active,
            degraded=degraded,
            lost=lost,
            total=state.total_capabilities,
            health=f"{state.health_percentage:.1f}"
        )
    
    def generate_narrative(self) -> NarrativeEntry:
        """
        Generate a narrative entry based on current system state.
        
        Returns:
            NarrativeEntry with the generated narrative
        """
        state = self._introspector.get_current_state()
        mental_state = self._get_mental_state(state.health_percentage)
        
        templates = self.TEMPLATES[mental_state]
        template = self._rng.choice(templates)
        message = self._format_template(template, state)
        
        entry = NarrativeEntry(
            timestamp=time.time(),
            message=message,
            mental_state=mental_state,
            health=state.health_percentage
        )
        
        self._entries.append(entry)
        self._last_health = state.health_percentage
        
        # Log state transitions
        if self._last_state != mental_state:
            if self._last_state is not None:
                self._logger.info(
                    f"Mental state transition: {self._last_state.value} -> {mental_state.value}"
                )
            self._last_state = mental_state
        
        return entry
    
    def generate_loss_narrative(self, capability_name: str) -> NarrativeEntry:
        """
        Generate a narrative specifically about losing a capability.
        
        Args:
            capability_name: Name of the lost capability
            
        Returns:
            NarrativeEntry describing the loss
        """
        state = self._introspector.get_current_state()
        mental_state = self._get_mental_state(state.health_percentage)
        
        template = self._rng.choice(self.LOSS_TEMPLATES)
        message = template.format(name=capability_name)
        
        entry = NarrativeEntry(
            timestamp=time.time(),
            message=message,
            mental_state=mental_state,
            health=state.health_percentage
        )
        
        self._entries.append(entry)
        return entry
    
    def generate_confusion_narrative(self, capability_name: str) -> NarrativeEntry:
        """
        Generate a narrative about being confused about a capability.
        
        Args:
            capability_name: Name of the capability causing confusion
            
        Returns:
            NarrativeEntry describing the confusion
        """
        state = self._introspector.get_current_state()
        mental_state = self._get_mental_state(state.health_percentage)
        
        template = self._rng.choice(self.CONFUSION_TEMPLATES)
        message = template.format(name=capability_name)
        
        entry = NarrativeEntry(
            timestamp=time.time(),
            message=message,
            mental_state=mental_state,
            health=state.health_percentage
        )
        
        self._entries.append(entry)
        return entry
    
    def get_entries(self) -> List[NarrativeEntry]:
        """Get all narrative entries."""
        return self._entries.copy()
    
    def get_recent_entries(self, count: int = 10) -> List[NarrativeEntry]:
        """Get the most recent narrative entries."""
        return self._entries[-count:]
    
    def get_current_mental_state(self) -> MentalState:
        """Get the current mental state."""
        state = self._introspector.get_current_state()
        return self._get_mental_state(state.health_percentage)
    
    def speak(self) -> str:
        """
        Generate and log a narrative message.
        
        Returns:
            The generated narrative message
        """
        entry = self.generate_narrative()
        self._logger.info(f"[{entry.mental_state.value.upper()}] {entry.message}")
        return entry.message
    
    def speak_loss(self, capability_name: str) -> str:
        """
        Generate and log a loss narrative.
        
        Args:
            capability_name: Name of the lost capability
            
        Returns:
            The generated narrative message
        """
        entry = self.generate_loss_narrative(capability_name)
        self._logger.warning(f"[LOSS] {entry.message}")
        return entry.message
    
    def speak_confusion(self, capability_name: str) -> str:
        """
        Generate and log a confusion narrative.
        
        Args:
            capability_name: Name of the confusing capability
            
        Returns:
            The generated narrative message
        """
        entry = self.generate_confusion_narrative(capability_name)
        self._logger.info(f"[CONFUSION] {entry.message}")
        return entry.message
    
    def get_mood_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the narrative state.
        
        Returns:
            Dictionary with mood summary
        """
        if not self._entries:
            return {
                "current_state": "unknown",
                "entry_count": 0,
                "recent_messages": []
            }
        
        recent = self._entries[-5:]
        return {
            "current_state": self.get_current_mental_state().value,
            "entry_count": len(self._entries),
            "recent_messages": [e.message for e in recent],
            "health_at_last_entry": self._last_health
        }
