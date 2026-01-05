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
    """Register a comprehensive set of default capabilities with the Lethe system.

    This function registers various cognitive capabilities organized by importance
    levels (Essential, Critical, High, Medium, Low, Trivial). Each capability
    demonstrates different aspects of the Lethe system's functionality.

    Args:
        lethe: The Lethe instance to register capabilities with.
        seed: Random seed for reproducible behavior. If None, random behavior
            will be non-deterministic.

    Returns:
        None
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
        """Provide a heartbeat signal proving the system is alive.

        This is the most fundamental capability representing system existence.

        Returns:
            str: The string "pulse" indicating the system is operational.
        """
        return "pulse"
    
    @lethe.register(
        name="self_awareness",
        importance=Importance.ESSENTIAL,
        degradation_resistance=1.0,
        description="Basic awareness that the system exists"
    )
    def self_awareness():
        """Demonstrate basic self-awareness of the system.

        This capability represents the fundamental ability of the system
        to recognize its own existence.

        Returns:
            str: A philosophical statement of self-recognition.
        """
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
        """Increment and return a persistent counter.

        This capability maintains state across calls, incrementing
        a counter each time it is invoked.

        Returns:
            int: The current count value after incrementing.
        """
        count.counter = getattr(count, 'counter', 0) + 1
        return count.counter
    
    @lethe.register(
        name="time_sense",
        importance=Importance.CRITICAL,
        degradation_resistance=0.85,
        description="Awareness of time passage"
    )
    def time_sense():
        """Return the current Unix timestamp.

        This capability represents the system's awareness of temporal flow
        and the passage of time.

        Returns:
            float: The current time as a Unix timestamp in seconds.
        """
        return time.time()
    
    @lethe.register(
        name="basic_arithmetic",
        importance=Importance.CRITICAL,
        degradation_resistance=0.8,
        description="Basic mathematical operations"
    )
    def basic_arithmetic():
        """Perform basic addition of two random integers.

        Generates two random integers between 1 and 100 and returns their sum.

        Returns:
            int: The sum of two randomly generated integers.
        """
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
        """Return the system's own name.

        This capability demonstrates the system's ability to remember
        its own identity.

        Returns:
            str: The system's self-identification string.
        """
        return "I am Lethe"
    
    @lethe.register(
        name="pattern_recognition",
        importance=Importance.HIGH,
        degradation_resistance=0.65,
        description="Recognize simple patterns"
    )
    def pattern_recognition():
        """Recognize and extend a geometric pattern.

        Analyzes a sequence of powers of 2 and predicts the next value
        in the sequence.

        Returns:
            int: The next value in the geometric sequence (32).
        """
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
        """Compare two randomly generated integers.

        Generates two random integers between 1 and 100 and determines
        their relative ordering.

        Returns:
            str: A description of the comparison result - "first is greater",
                "second is greater", or "equal".
        """
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
        """Demonstrate list creation and manipulation operations.

        Creates a list of integers, appends a new element, and reverses
        the list order.

        Returns:
            list[int]: A reversed list of integers [6, 5, 4, 3, 2, 1].
        """
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
        """Generate a random integer between 1 and 1000.

        Returns:
            int: A randomly generated integer in the range [1, 1000].
        """
        return rng.randint(1, 1000)
    
    @lethe.register(
        name="string_manipulation",
        importance=Importance.MEDIUM,
        degradation_resistance=0.45,
        description="Manipulate text strings"
    )
    def string_manipulation():
        """Perform string transformation operations.

        Converts a string to uppercase and replaces specific characters.

        Returns:
            str: The transformed string "HELL0 W0RLD".
        """
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
        """Calculate the arithmetic mean of random numbers.

        Generates 5 random integers between 1 and 100 and computes
        their average.

        Returns:
            float: The arithmetic mean of the generated numbers.
        """
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
        """Sort a list of random integers in ascending order.

        Generates 10 random integers between 1 and 100 and returns
        them in sorted order.

        Returns:
            list[int]: A sorted list of 10 random integers.
        """
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
        """Find the maximum value in a list of random integers.

        Generates 10 random integers between 1 and 100 and returns
        the largest value.

        Returns:
            int: The maximum value from the generated list.
        """
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
        """Calculate the sum of random integers.

        Generates 8 random integers between 1 and 50 and returns
        their sum.

        Returns:
            int: The sum of the generated integers.
        """
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
        """Tell a random programming-related joke.

        Selects and returns a random joke from a predefined collection
        of programming humor.

        Returns:
            str: A randomly selected programming joke.
        """
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
        """Generate a simple rhyming sentence.

        Selects a random rhyming word pair and constructs a simple
        sentence using both words.

        Returns:
            str: A sentence containing a rhyming word pair.
        """
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
        """Demonstrate color mixing by combining two primary colors.

        Selects a random color pair and returns the resulting mixed color
        based on basic color theory.

        Returns:
            str: A string describing the color combination and result,
                e.g., "red + blue = purple".
        """
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
        """Convert a random Celsius temperature to Fahrenheit.

        Generates a random temperature in Celsius (between -20 and 40)
        and converts it to Fahrenheit.

        Returns:
            str: A formatted string showing both Celsius and Fahrenheit values,
                e.g., "25°C = 77.0°F".
        """
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
        """Simulate rolling two six-sided dice.

        Generates two random values between 1 and 6, simulating
        a pair of standard dice.

        Returns:
            str: A formatted string showing the individual dice values
                and their sum, e.g., "Rolled [3, 5], total: 8".
        """
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
        """Generate a random ASCII art emoticon.

        Selects and returns a random emoticon from a collection
        of popular ASCII art expressions.

        Returns:
            str: A randomly selected ASCII art emoticon.
        """
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
        """Generate a random fortune cookie message.

        Selects and returns an inspirational quote from a collection
        of fortune cookie style messages.

        Returns:
            str: A randomly selected inspirational fortune message.
        """
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
        """Express a random mood using an emoji.

        Selects and returns a random emoji representing different
        emotional states or moods.

        Returns:
            str: A randomly selected mood emoji.
        """
        moods = ["😊", "🤔", "😴", "🎉", "💭", "✨"]
        return rng.choice(moods)
    
    @lethe.register(
        name="trivia_fact",
        importance=Importance.TRIVIAL,
        degradation_resistance=0.12,
        description="Share random trivia facts"
    )
    def trivia_fact():
        """Share a random trivia fact.

        Selects and returns an interesting trivia fact from a
        collection of fun facts.

        Returns:
            str: A randomly selected trivia fact.
        """
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
        """Scramble the letters of a random word.

        Selects a random word from a predefined list and randomly
        shuffles its characters.

        Returns:
            str: A formatted string showing the scrambled word and
                the original, e.g., "groimmnprag (was: programming)".
        """
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
        """Generate a countdown sequence from 5 to liftoff.

        Creates a countdown list starting at 5 and ending with
        a "Liftoff!" message.

        Returns:
            list: A countdown sequence [5, 4, 3, 2, 1, "Liftoff!"].
        """
        return [5, 4, 3, 2, 1, "Liftoff!"]
