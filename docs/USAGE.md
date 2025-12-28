# Lethe Usage Guide

This guide provides detailed instructions for using the Lethe self-degrading cognitive system.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Command Line Interface](#command-line-interface)
4. [Programmatic Usage](#programmatic-usage)
5. [Custom Capabilities](#custom-capabilities)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/your-username/lethe.git
cd lethe

# Install dependencies
pip install -r requirements.txt
```

### Development Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
pytest tests/ -v
```

## Quick Start

### Run the Demo

The demo mode runs 20 fast iterations to show how the system degrades:

```bash
python run.py --demo
```

### Run Indefinitely

For the full experience, run without arguments:

```bash
python run.py
```

Press `Ctrl+C` to stop gracefully.

## Command Line Interface

### Basic Options

```bash
python run.py [OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--iterations N` | `-n` | Run for N iterations |
| `--demo` | | Quick demo mode (20 iterations) |
| `--verbose` | `-v` | Enable debug logging |
| `--seed N` | | Set random seed |

### Timing Options

| Option | Description | Default |
|--------|-------------|---------|
| `--decay-interval` | Seconds between decay attempts | 5.0 |
| `--decay-prob` | Probability of decay (0.0-1.0) | 0.4 |
| `--loop-interval` | Seconds between main loops | 2.0 |
| `--narrative-interval` | Seconds between narratives | 10.0 |

### Examples

```bash
# Run for exactly 100 iterations
python run.py --iterations 100

# Fast decay for testing
python run.py --decay-interval 1.0 --decay-prob 0.8 --loop-interval 0.5

# Slow, gradual decay
python run.py --decay-interval 30.0 --decay-prob 0.2

# Reproducible run with seed
python run.py --seed 42 --iterations 50

# Verbose output for debugging
python run.py --verbose --demo
```

## Programmatic Usage

### Basic Usage

```python
from src.lethe import Lethe
from src.capabilities import register_default_capabilities

# Create Lethe instance
lethe = Lethe(
    decay_interval=5.0,
    decay_probability=0.4,
    seed=42
)

# Register default capabilities
register_default_capabilities(lethe)

# Initialize
lethe.initialize()

# Run for 50 iterations
lethe.run(max_iterations=50)
```

### Manual Control

```python
from src.lethe import Lethe
from src.capabilities import register_default_capabilities

lethe = Lethe()
register_default_capabilities(lethe)
lethe.initialize()

# Manual tick control
for i in range(100):
    iteration = lethe.tick()
    print(f"Iteration {iteration.iteration}, Health: {iteration.health:.1f}%")
    
    # Custom logic between ticks
    if iteration.health < 50:
        print("Health is getting low!")
```

### Accessing Components

```python
# Get system status
status = lethe.get_status()
print(f"Health: {status['introspection']['health_percentage']:.1f}%")
print(f"Active capabilities: {status['introspection']['active_capabilities']}")

# Access individual components
registry = lethe.registry
decay_engine = lethe.decay_engine
introspector = lethe.introspector
narrator = lethe.narrative
safety = lethe.safety

# Force a specific decay
lethe.force_decay("joke_telling")

# Pause/resume decay
lethe.pause()  # Stop decay
lethe.resume()  # Continue decay

# Stop execution
lethe.stop()
```

## Custom Capabilities

### Using Decorators

```python
from src.lethe import Lethe
from src.capability import Importance

lethe = Lethe()

@lethe.register(
    name="calculate_fibonacci",
    importance=Importance.HIGH,
    degradation_resistance=0.7,
    description="Calculate Fibonacci numbers"
)
def calculate_fibonacci(n: int = 10) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

@lethe.register(
    name="greet_user",
    importance=Importance.LOW,
    dependencies=["remember_name"],
    degradation_resistance=0.3,
    description="Greet the user by name"
)
def greet_user():
    return "Hello, friend!"
```

### Using Direct Registration

```python
def my_function():
    return "Hello, World!"

lethe.register_function(
    func=my_function,
    name="my_function",
    importance=Importance.MEDIUM,
    degradation_resistance=0.5,
    description="A simple greeting function"
)
```

### Importance Levels

| Level | Value | Description | Decay Resistance |
|-------|-------|-------------|------------------|
| TRIVIAL | 1 | Non-essential, first to forget | Very low |
| LOW | 2 | Nice to have | Low |
| MEDIUM | 3 | Standard functionality | Medium |
| HIGH | 4 | Important features | High |
| CRITICAL | 5 | Core functionality | Very high |
| ESSENTIAL | 6 | Cannot be removed | Protected |

### Dependencies

Capabilities can declare dependencies on other capabilities:

```python
@lethe.register(
    name="complex_calculation",
    dependencies=["basic_arithmetic", "pattern_recognition"],
    importance=Importance.MEDIUM
)
def complex_calculation():
    # This depends on basic_arithmetic and pattern_recognition
    return calculate_something()
```

## Configuration

### Lethe Constructor Parameters

```python
lethe = Lethe(
    decay_interval=5.0,       # Seconds between decay attempts
    decay_probability=0.4,    # Base probability of decay (0.0-1.0)
    loop_interval=2.0,        # Seconds between main loop iterations
    narrative_interval=10.0,  # Seconds between narrative outputs
    seed=None,                # Random seed for reproducibility
    log_level=logging.INFO    # Logging level
)
```

### Decay Configuration

The decay engine can be configured after creation:

```python
# Adjust decay timing
lethe.decay_engine.decay_interval = 10.0

# Adjust decay probability
lethe.decay_engine.decay_probability = 0.3

# Disable decay temporarily
lethe.decay_engine.disable()

# Re-enable decay
lethe.decay_engine.enable()
```

## Monitoring

### System Status

```python
status = lethe.get_status()

# Introspection data
print(f"Health: {status['introspection']['health_percentage']:.1f}%")
print(f"Active: {status['introspection']['active_capabilities']}")
print(f"Degraded: {status['introspection']['degraded_capabilities']}")
print(f"Deleted: {status['introspection']['deleted_capabilities']}")
print(f"Trend: {status['introspection']['health_trend']}")

# Decay statistics
print(f"Total decays: {status['decay']['total_decays']}")
print(f"Approximations: {status['decay']['approximations']}")
print(f"Stubs: {status['decay']['stubs']}")
print(f"Deletions: {status['decay']['deletions']}")

# Safety status
print(f"Safety active: {status['safety']['is_active']}")
print(f"Emergency mode: {status['safety']['is_emergency']}")

# Narrative mood
print(f"Mental state: {status['narrative']['current_state']}")
```

### Capability Inspection

```python
# List all capabilities
for name in lethe.registry.list_capabilities():
    info = lethe.introspector.get_capability_info(name)
    print(f"{name}: {info['importance']} (degradation: {info['degradation_level']})")

# Get specific capability info
info = lethe.introspector.get_capability_info("heartbeat")
print(f"Name: {info['name']}")
print(f"Importance: {info['importance']}")
print(f"Degraded: {info['is_degraded']}")
print(f"Executions: {info['execution_count']}")

# Check what's been forgotten
forgotten = lethe.introspector.get_forgotten_names()
print(f"Forgotten capabilities: {forgotten}")

# Check what's fading
fading = lethe.introspector.get_fading_memories()
print(f"Fading capabilities: {fading}")
```

### History Access

```python
# Decay history
for event in lethe.decay_engine.get_recent_history(10):
    print(f"{event.timestamp}: {event.capability_name} - {event.decay_type}")

# State history
for state in lethe.introspector.get_recent_states(5):
    print(f"{state.timestamp}: Health={state.health_percentage:.1f}%")

# Narrative history
for entry in lethe.narrative.get_recent_entries(5):
    print(f"[{entry.mental_state.value}] {entry.message}")
```

## Troubleshooting

### System Not Degrading

1. Check if decay engine is enabled:
   ```python
   print(lethe.decay_engine.is_enabled)
   ```

2. Verify decay probability is non-zero:
   ```python
   print(lethe.decay_engine.decay_probability)
   ```

3. Check if all non-essential capabilities are already deleted:
   ```python
   print(lethe.registry.get_degradation_candidates())
   ```

### System Degrading Too Fast

1. Increase decay interval:
   ```bash
   python run.py --decay-interval 30.0
   ```

2. Reduce decay probability:
   ```bash
   python run.py --decay-prob 0.1
   ```

3. Increase capability resistance:
   ```python
   @lethe.register(name="important", degradation_resistance=0.9)
   def important():
       pass
   ```

### Capability Not Being Protected

Ensure it's marked as ESSENTIAL:

```python
@lethe.register(name="must_protect", importance=Importance.ESSENTIAL)
def must_protect():
    pass
```

### Logging Issues

Enable verbose logging:

```bash
python run.py --verbose
```

Or programmatically:

```python
import logging
lethe = Lethe(log_level=logging.DEBUG)
```

### Memory Issues

For long-running instances, history can accumulate. You can:

1. Limit history access to recent entries only
2. Reset the decay engine periodically:
   ```python
   lethe.decay_engine.reset()
   ```

### Reproducibility Issues

Use a seed for consistent behavior:

```python
lethe = Lethe(seed=42)
register_default_capabilities(lethe, seed=42)
```

Both the Lethe instance and capabilities should use the same seed for full reproducibility.
