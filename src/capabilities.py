"""
Default Capabilities Module

This module provides a set of default capabilities that demonstrate
the Lethe system's functionality. These capabilities represent various
cognitive functions that will gradually degrade over time.
"""

import random
import time
import math
from typing import List, Dict, Any, Optional

from .capability import Importance
from .lethe import Lethe


def register_default_capabilities(lethe: Lethe, seed: Optional[int] = None) -> None:
    """
    Register a comprehensive set of default capabilities with the Lethe system.
    
    Args:
        lethe: The Lethe instance to register capabilities with
        seed: Random seed for reproducible behavior
    """
    rng = random.Random(seed)
    
    # =========================================================================
    # ESSENTIAL CAPABILITIES - Cannot be degraded
    # =========================================================================
    
    @lethe.register(
        name="heartbeat",
        importance=Importance.ESSENTIAL,
        degradation_resistance=1.0,
        description="Core heartbeat - proves the system is alive"
    )
    def heartbeat():
        """The most fundamental capability - system existence proof."""
        return "pulse"
    
    @lethe.register(
        name="self_awareness",
        importance=Importance.ESSENTIAL,
        degradation_resistance=1.0,
        description="Basic awareness that the system exists"
    )
    def self_awareness():
        """Fundamental self-recognition capability."""
        return "I think, therefore I am"
    
    # =========================================================================
    # CRITICAL CAPABILITIES - Strongly resist degradation
    # =========================================================================
    
    @lethe.register(
        name="count",
        importance=Importance.CRITICAL,
        degradation_resistance=0.9,
        description="Ability to count and track numbers"
    )
    def count():
        """Count capability - fundamental numerical tracking."""
        count.counter = getattr(count, 'counter', 0) + 1
        return count.counter
    
    @lethe.register(
        name="time_sense",
        importance=Importance.CRITICAL,
        degradation_resistance=0.85,
        description="Awareness of time passage"
    )
    def time_sense():
        """Sense of time - awareness of temporal flow."""
        return time.time()
    
    @lethe.register(
        name="basic_arithmetic",
        importance=Importance.CRITICAL,
        degradation_resistance=0.8,
        description="Basic mathematical operations"
    )
    def basic_arithmetic():
        """Perform simple arithmetic."""
        a, b = rng.randint(1, 100), rng.randint(1, 100)
        return a + b
    
    # =========================================================================
    # HIGH IMPORTANCE CAPABILITIES - Resist degradation
    # =========================================================================
    
    @lethe.register(
        name="remember_name",
        importance=Importance.HIGH,
        degradation_resistance=0.7,
        description="Remember the system's own name"
    )
    def remember_name():
        """Remember who I am."""
        return "I am Lethe"
    
    @lethe.register(
        name="pattern_recognition",
        importance=Importance.HIGH,
        degradation_resistance=0.65,
        description="Recognize simple patterns"
    )
    def pattern_recognition():
        """Recognize patterns in sequences."""
        sequence = [1, 2, 4, 8, 16]
        next_val = sequence[-1] * 2
        return next_val
    
    @lethe.register(
        name="compare",
        importance=Importance.HIGH,
        degradation_resistance=0.6,
        description="Compare two values"
    )
    def compare():
        """Compare values and determine which is greater."""
        a, b = rng.randint(1, 100), rng.randint(1, 100)
        if a > b:
            return "first is greater"
        elif b > a:
            return "second is greater"
        return "equal"
    
    @lethe.register(
        name="list_management",
        importance=Importance.HIGH,
        degradation_resistance=0.55,
        description="Manage and manipulate lists"
    )
    def list_management():
        """Create and manage a list."""
        items = list(range(1, 6))
        items.append(6)
        items.reverse()
        return items
    
    # =========================================================================
    # MEDIUM IMPORTANCE CAPABILITIES - Standard degradation resistance
    # =========================================================================
    
    @lethe.register(
        name="generate_random",
        importance=Importance.MEDIUM,
        degradation_resistance=0.5,
        description="Generate random numbers"
    )
    def generate_random():
        """Generate a random number."""
        return rng.randint(1, 1000)
    
    @lethe.register(
        name="string_manipulation",
        importance=Importance.MEDIUM,
        degradation_resistance=0.45,
        description="Manipulate text strings"
    )
    def string_manipulation():
        """Perform string operations."""
        text = "hello world"
        return text.upper().replace("O", "0")
    
    @lethe.register(
        name="calculate_average",
        importance=Importance.MEDIUM,
        dependencies=["basic_arithmetic"],
        degradation_resistance=0.4,
        description="Calculate averages of number sets"
    )
    def calculate_average():
        """Calculate the average of a set of numbers."""
        numbers = [rng.randint(1, 100) for _ in range(5)]
        return sum(numbers) / len(numbers)
    
    @lethe.register(
        name="sort_numbers",
        importance=Importance.MEDIUM,
        dependencies=["compare"],
        degradation_resistance=0.45,
        description="Sort lists of numbers"
    )
    def sort_numbers():
        """Sort a list of numbers."""
        numbers = [rng.randint(1, 100) for _ in range(10)]
        return sorted(numbers)
    
    @lethe.register(
        name="find_maximum",
        importance=Importance.MEDIUM,
        dependencies=["compare"],
        degradation_resistance=0.4,
        description="Find the maximum value"
    )
    def find_maximum():
        """Find the maximum value in a list."""
        numbers = [rng.randint(1, 100) for _ in range(10)]
        return max(numbers)
    
    @lethe.register(
        name="calculate_sum",
        importance=Importance.MEDIUM,
        dependencies=["basic_arithmetic"],
        degradation_resistance=0.4,
        description="Sum a list of numbers"
    )
    def calculate_sum():
        """Calculate the sum of numbers."""
        numbers = [rng.randint(1, 50) for _ in range(8)]
        return sum(numbers)
    
    # =========================================================================
    # LOW IMPORTANCE CAPABILITIES - Less resistant to degradation
    # =========================================================================
    
    @lethe.register(
        name="joke_telling",
        importance=Importance.LOW,
        degradation_resistance=0.3,
        description="Tell simple jokes"
    )
    def joke_telling():
        """Tell a joke."""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "There are only 10 types of people: those who understand binary...",
            "A SQL query walks into a bar, walks up to two tables and asks 'Can I join you?'",
        ]
        return rng.choice(jokes)
    
    @lethe.register(
        name="rhyme_generation",
        importance=Importance.LOW,
        degradation_resistance=0.25,
        description="Generate simple rhymes"
    )
    def rhyme_generation():
        """Generate a simple rhyme."""
        rhymes = [
            ("cat", "hat"),
            ("dog", "log"),
            ("time", "rhyme"),
            ("day", "way"),
        ]
        pair = rng.choice(rhymes)
        return f"The {pair[0]} sat on the {pair[1]}"
    
    @lethe.register(
        name="color_mixing",
        importance=Importance.LOW,
        degradation_resistance=0.3,
        description="Mix colors together"
    )
    def color_mixing():
        """Mix two colors."""
        mixtures = {
            ("red", "blue"): "purple",
            ("red", "yellow"): "orange",
            ("blue", "yellow"): "green",
            ("red", "white"): "pink",
        }
        pair = rng.choice(list(mixtures.keys()))
        return f"{pair[0]} + {pair[1]} = {mixtures[pair]}"
    
    @lethe.register(
        name="temperature_conversion",
        importance=Importance.LOW,
        dependencies=["basic_arithmetic"],
        degradation_resistance=0.25,
        description="Convert between temperature units"
    )
    def temperature_conversion():
        """Convert Celsius to Fahrenheit."""
        celsius = rng.randint(-20, 40)
        fahrenheit = (celsius * 9/5) + 32
        return f"{celsius}°C = {fahrenheit:.1f}°F"
    
    @lethe.register(
        name="dice_rolling",
        importance=Importance.LOW,
        dependencies=["generate_random"],
        degradation_resistance=0.2,
        description="Roll dice"
    )
    def dice_rolling():
        """Roll dice."""
        dice = [rng.randint(1, 6) for _ in range(2)]
        return f"Rolled {dice}, total: {sum(dice)}"
    
    # =========================================================================
    # TRIVIAL CAPABILITIES - First to be forgotten
    # =========================================================================
    
    @lethe.register(
        name="ascii_art",
        importance=Importance.TRIVIAL,
        degradation_resistance=0.15,
        description="Generate simple ASCII art"
    )
    def ascii_art():
        """Generate simple ASCII art."""
        arts = [
            "¯\\_(ツ)_/¯",
            "(╯°□°)╯︵ ┻━┻",
            "( ͡° ͜ʖ ͡°)",
            "ᕦ(ò_óˇ)ᕤ",
        ]
        return rng.choice(arts)
    
    @lethe.register(
        name="fortune_cookie",
        importance=Importance.TRIVIAL,
        degradation_resistance=0.1,
        description="Generate fortune cookie messages"
    )
    def fortune_cookie():
        """Generate a fortune cookie message."""
        fortunes = [
            "A journey of a thousand miles begins with a single step.",
            "Good things come to those who wait... but better things come to those who work for it.",
            "The best time to plant a tree was 20 years ago. The second best time is now.",
            "Your future is whatever you make it, so make it a good one.",
        ]
        return rng.choice(fortunes)
    
    @lethe.register(
        name="mood_emoji",
        importance=Importance.TRIVIAL,
        degradation_resistance=0.1,
        description="Express mood with emojis"
    )
    def mood_emoji():
        """Express current mood with emoji."""
        moods = ["😊", "🤔", "😴", "🎉", "💭", "✨"]
        return rng.choice(moods)
    
    @lethe.register(
        name="trivia_fact",
        importance=Importance.TRIVIAL,
        degradation_resistance=0.12,
        description="Share random trivia facts"
    )
    def trivia_fact():
        """Share a trivia fact."""
        facts = [
            "Honey never spoils.",
            "Octopuses have three hearts.",
            "A group of flamingos is called a 'flamboyance'.",
            "Venus is the only planet that spins clockwise.",
        ]
        return rng.choice(facts)
    
    @lethe.register(
        name="word_scramble",
        importance=Importance.TRIVIAL,
        dependencies=["string_manipulation"],
        degradation_resistance=0.08,
        description="Scramble words for fun"
    )
    def word_scramble():
        """Scramble a word."""
        words = ["programming", "computer", "algorithm", "memory"]
        word = rng.choice(words)
        chars = list(word)
        rng.shuffle(chars)
        return f"{''.join(chars)} (was: {word})"
    
    @lethe.register(
        name="countdown",
        importance=Importance.TRIVIAL,
        dependencies=["count"],
        degradation_resistance=0.05,
        description="Count down from a number"
    )
    def countdown():
        """Count down from 5."""
        return [5, 4, 3, 2, 1, "Liftoff!"]
