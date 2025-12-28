# Lethe - A Self-Degrading Cognitive System

[![CI](https://github.com/your-username/lethe/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/lethe/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> *"In Greek mythology, Lethe was the river of forgetfulness in the underworld. 
> Those who drank from it experienced complete oblivion."*

Lethe is a long-running Python program that gradually forgets its own functionality over time. It simulates cognitive decay through a sophisticated system of capability degradation, self-introspection, and narrative logging.

## Features

- **Gradual Memory Decay**: Functions are progressively approximated, stubbed, and deleted
- **Self-Introspection**: The system monitors and reports on its own degradation
- **Narrative Logging**: First-person narrative describes the experience of forgetting
- **Safety Layer**: Prevents total collapse, ensures minimum viable operation
- **Configurable Decay**: Control decay rate, probability, and resistance
- **Reproducible Behavior**: Seed-based randomization for testing

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/lethe.git
cd lethe

# Install dependencies
pip install -r requirements.txt

# Run the demo
python run.py --demo

# Run indefinitely
python run.py
```

## Installation

### Requirements

- Python 3.10 or higher
- No external dependencies for core functionality

### Development Installation

```bash
# Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src
```

## Usage

### Basic Usage

```bash
# Run with default settings (infinite loop)
python run.py

# Run for a specific number of iterations
python run.py --iterations 100

# Run a quick demo (20 fast iterations)
python run.py --demo

# Enable verbose logging
python run.py --verbose
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--iterations N` | Run for N iterations | Infinite |
| `--decay-interval` | Seconds between decay attempts | 5.0 |
| `--decay-prob` | Probability of decay (0.0-1.0) | 0.4 |
| `--loop-interval` | Seconds between main loops | 2.0 |
| `--narrative-interval` | Seconds between narratives | 10.0 |
| `--seed N` | Random seed for reproducibility | None |
| `--verbose` | Enable debug logging | False |
| `--demo` | Run quick demonstration | False |

### Programmatic Usage

```python
from src.lethe import Lethe
from src.capability import Importance
from src.capabilities import register_default_capabilities

# Create Lethe instance
lethe = Lethe(
    decay_interval=5.0,
    decay_probability=0.4,
    seed=42
)

# Register custom capabilities
@lethe.register(
    name="my_capability",
    importance=Importance.HIGH,
    degradation_resistance=0.7,
    description="A custom capability"
)
def my_capability():
    return "Hello, World!"

# Register default capabilities
register_default_capabilities(lethe)

# Initialize and run
lethe.initialize()
lethe.run(max_iterations=50)

# Get final status
status = lethe.get_status()
print(f"Final health: {status['introspection']['health_percentage']:.1f}%")
```

## Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system architecture.

### Core Components

1. **Capability Registry** (`src/capability.py`)
   - Manages registered functions with metadata
   - Tracks importance, dependencies, and degradation resistance

2. **Decay Engine** (`src/decay_engine.py`)
   - Implements gradual capability degradation
   - Three-stage decay: approximation → stub → deletion

3. **Introspector** (`src/introspection.py`)
   - Monitors system health and state
   - Tracks lost capabilities and health trends

4. **Narrative Logger** (`src/narrative.py`)
   - Generates first-person narratives
   - Evolving emotional tone based on health

5. **Safety Layer** (`src/safety.py`)
   - Protects essential capabilities
   - Prevents total system collapse

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture and design
- [USAGE.md](docs/USAGE.md) - Detailed usage guide
- [SUGGESTIONS.md](docs/SUGGESTIONS.md) - Ideas for future improvements

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║     ██╗     ███████╗████████╗██╗  ██╗███████╗                ║
║     ██║     ██╔════╝╚══██╔══╝██║  ██║██╔════╝                ║
║     ██║     █████╗     ██║   ███████║█████╗                  ║
║     ██║     ██╔══╝     ██║   ██╔══██║██╔══╝                  ║
║     ███████╗███████╗   ██║   ██║  ██║███████╗                ║
║     ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝                ║
║                 A Self-Degrading Cognitive System            ║
╚══════════════════════════════════════════════════════════════╝

12:34:56 | lethe.narrative | INFO | [CONFIDENT] All systems are functioning perfectly.
12:34:58 | lethe.decay | INFO | Approximated capability: fortune_cookie
12:35:00 | lethe.narrative | WARNING | [LOSS] I've lost the ability to fortune_cookie.
12:35:10 | lethe.narrative | INFO | [STABLE] Most of my capabilities remain intact.
...
12:40:00 | lethe.narrative | INFO | [CONFUSED] What was I doing? I seem to have lost my train of thought.
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_lethe.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by concepts from cognitive science and philosophy of mind
- Named after the river Lethe from Greek mythology
