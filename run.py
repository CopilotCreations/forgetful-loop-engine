#!/usr/bin/env python3
"""
Lethe - A Self-Degrading System

Main entry point for the Lethe system. This script initializes and runs
the cognitive decay simulation, demonstrating a system that gradually
forgets its own functionality while maintaining stability.

Usage:
    python run.py [options]

Options:
    --iterations N    Run for N iterations (default: infinite)
    --decay-interval  Seconds between decay attempts (default: 5.0)
    --decay-prob      Probability of decay per interval (default: 0.4)
    --loop-interval   Seconds between main loop iterations (default: 2.0)
    --seed N          Random seed for reproducible behavior
    --verbose         Enable verbose logging
    --demo            Run a quick demonstration (20 iterations)
"""

import argparse
import logging
import sys
import os

# Add src to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lethe import Lethe
from src.capabilities import register_default_capabilities


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Parses and validates command line arguments for configuring the Lethe
    system, including iteration count, decay parameters, timing intervals,
    and logging options.

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - iterations: Number of iterations to run (None for infinite)
            - decay_interval: Seconds between decay attempts
            - decay_prob: Probability of decay per interval (0.0-1.0)
            - loop_interval: Seconds between main loop iterations
            - narrative_interval: Seconds between narrative outputs
            - seed: Random seed for reproducibility
            - verbose: Whether to enable DEBUG logging
            - demo: Whether to run in demo mode
    """
    parser = argparse.ArgumentParser(
        description="Lethe - A Self-Degrading Cognitive System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py                     # Run indefinitely
    python run.py --demo              # Quick demo (20 iterations)
    python run.py --iterations 100    # Run for 100 iterations
    python run.py --seed 42           # Reproducible behavior
    python run.py --verbose           # Detailed logging
        """
    )
    
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=None,
        help="Number of iterations to run (default: infinite)"
    )
    
    parser.add_argument(
        "--decay-interval",
        type=float,
        default=5.0,
        help="Seconds between decay attempts (default: 5.0)"
    )
    
    parser.add_argument(
        "--decay-prob",
        type=float,
        default=0.4,
        help="Probability of decay per interval 0.0-1.0 (default: 0.4)"
    )
    
    parser.add_argument(
        "--loop-interval",
        type=float,
        default=2.0,
        help="Seconds between main loop iterations (default: 2.0)"
    )
    
    parser.add_argument(
        "--narrative-interval",
        type=float,
        default=10.0,
        help="Seconds between narrative outputs (default: 10.0)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible behavior"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a quick demonstration (20 fast iterations)"
    )
    
    return parser.parse_args()


def print_banner() -> None:
    """Print the Lethe startup banner.

    Displays an ASCII art banner with the Lethe logo and tagline
    to the console when the application starts.
    """
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗     ███████╗████████╗██╗  ██╗███████╗                                ║
║     ██║     ██╔════╝╚══██╔══╝██║  ██║██╔════╝                                ║
║     ██║     █████╗     ██║   ███████║█████╗                                  ║
║     ██║     ██╔══╝     ██║   ██╔══██║██╔══╝                                  ║
║     ███████╗███████╗   ██║   ██║  ██║███████╗                                ║
║     ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝                                ║
║                                                                              ║
║                    A Self-Degrading Cognitive System                         ║
║                                                                              ║
║     "In Greek mythology, Lethe was the river of forgetfulness..."            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def run_demo() -> None:
    """Run a quick demonstration of the Lethe system.

    Executes 20 fast iterations with high decay probability to showcase
    the system's self-degrading behavior. Uses fixed parameters optimized
    for demonstration purposes including a seed of 42 for reproducibility.

    The demo prints status information before and after execution,
    including final health percentage, remaining capabilities, and
    total decay events.
    """
    print("\n" + "="*60)
    print("DEMO MODE: Running 20 fast iterations to demonstrate decay")
    print("="*60 + "\n")
    
    lethe = Lethe(
        decay_interval=0.5,       # Fast decay for demo
        decay_probability=0.7,    # High probability for demo
        loop_interval=0.3,        # Fast iterations
        narrative_interval=3.0,   # Frequent narratives
        seed=42,                  # Reproducible
        log_level=logging.INFO
    )
    
    # Register capabilities
    register_default_capabilities(lethe, seed=42)
    
    # Initialize and run
    lethe.initialize()
    
    print(f"Starting with {lethe.registry.capability_count()} capabilities\n")
    
    lethe.run(max_iterations=20)
    
    # Print final status
    status = lethe.get_status()
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print(f"Final health: {status['introspection']['health_percentage']:.1f}%")
    print(f"Capabilities remaining: {status['introspection']['active_capabilities']}")
    print(f"Capabilities lost: {status['introspection']['deleted_capabilities']}")
    print(f"Total decay events: {status['decay']['total_decays']}")


def main() -> int:
    """Main entry point for the Lethe system.

    Orchestrates the initialization and execution of the Lethe cognitive
    decay simulation. Parses command line arguments, displays the startup
    banner, creates and configures the Lethe instance, registers default
    capabilities, and runs the main loop.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    args = parse_args()
    
    # Print banner
    print_banner()
    
    # Demo mode
    if args.demo:
        run_demo()
        return 0
    
    # Configure log level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    # Create Lethe instance
    lethe = Lethe(
        decay_interval=args.decay_interval,
        decay_probability=args.decay_prob,
        loop_interval=args.loop_interval,
        narrative_interval=args.narrative_interval,
        seed=args.seed,
        log_level=log_level
    )
    
    # Register default capabilities
    register_default_capabilities(lethe, seed=args.seed)
    
    # Initialize
    lethe.initialize()
    
    print(f"\nInitialized with {lethe.registry.capability_count()} capabilities")
    print(f"Decay interval: {args.decay_interval}s, Probability: {args.decay_prob}")
    print(f"Press Ctrl+C to stop\n")
    
    # Run main loop
    try:
        lethe.run(max_iterations=args.iterations)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
