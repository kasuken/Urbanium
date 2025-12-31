"""
Urbanium - Main simulation runner.

This module provides the main entry point for running Urbanium simulations.

Usage:
    python -m urbanium.main
    python -m urbanium.main --seed 42 --ticks 1000
    python -m urbanium.main --ai --ai-url http://localhost:1234/v1
"""

import argparse
import logging
import time
from typing import Optional

from urbanium.engine.world import World
from urbanium.engine.tick import TickLoop
from urbanium.scenarios import SimpleCityScenario
from urbanium.scenarios.base import ScenarioConfig
from urbanium.metrics import (
    EmploymentObserver,
    EconomicObserver,
    SocialObserver,
    MetricsAggregator,
)

# AI imports (optional)
try:
    from urbanium.ai import AIConfig, AIDecisionModel
    HAS_AI = True
except ImportError:
    HAS_AI = False


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the simulation."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_simulation(
    seed: int = 42,
    population: int = 100,
    max_ticks: int = 1000,
    use_ai: bool = False,
    ai_config: Optional["AIConfig"] = None,
) -> tuple:
    """
    Create a simulation with the given parameters.
    
    Args:
        seed: Random seed for reproducibility
        population: Number of citizens
        max_ticks: Maximum ticks to run
        use_ai: Whether to use AI for agent decisions
        ai_config: Configuration for AI endpoint
    
    Returns:
        tuple: (world, tick_loop, aggregator)
    """
    logger = logging.getLogger("urbanium")
    
    # Create world
    world = World(seed=seed)
    
    # Create scenario
    config = ScenarioConfig(
        name="Custom Simulation",
        seed=seed,
        population_size=population,
        max_ticks=max_ticks,
    )
    scenario = SimpleCityScenario(config=config)
    
    # Initialize scenario
    citizens = scenario.initialize(world)
    
    # Set up AI decision model if requested
    if use_ai:
        if not HAS_AI:
            raise ImportError(
                "AI features require the 'openai' package. "
                "Install with: pip install urbanium[ai]"
            )
        
        logger.info("Enabling AI-powered decision making")
        ai_decision_model = AIDecisionModel.create(ai_config)
        
        # Check connection
        if ai_decision_model.ai_client and ai_decision_model.ai_client.check_connection():
            logger.info(f"Connected to AI endpoint: {ai_config.base_url if ai_config else 'default'}")
        else:
            logger.warning("Could not connect to AI endpoint, using fallback decisions")
        
        # Assign AI decision model to all citizens
        for citizen in citizens:
            citizen.decision_model = ai_decision_model
    
    # Create tick loop
    tick_loop = TickLoop(
        world=world,
        agents=citizens,
        max_ticks=max_ticks,
    )
    
    # Create metrics aggregator and observers
    aggregator = MetricsAggregator()
    aggregator.add_observer(EmploymentObserver())
    aggregator.add_observer(EconomicObserver())
    aggregator.add_observer(SocialObserver())
    
    # Add observers to tick loop
    for observer in aggregator.observers:
        tick_loop.add_observer(observer)
    
    return world, tick_loop, aggregator


def run_simulation(
    seed: int = 42,
    population: int = 100,
    max_ticks: int = 1000,
    verbose: bool = True,
    use_ai: bool = False,
    ai_config: Optional["AIConfig"] = None,
) -> dict:
    """
    Run a complete simulation.
    
    Args:
        seed: Random seed for reproducibility
        population: Number of citizens
        max_ticks: Maximum number of ticks to run
        verbose: Whether to print progress
        use_ai: Whether to use AI for agent decisions
        ai_config: Configuration for AI endpoint
        
    Returns:
        dict: Simulation results
    """
    logger = logging.getLogger("urbanium")
    
    # Create simulation
    world, tick_loop, aggregator = create_simulation(
        seed=seed,
        population=population,
        max_ticks=max_ticks,
        use_ai=use_ai,
        ai_config=ai_config,
    )
    
    # Run
    start_time = time.time()
    
    if verbose:
        # Add progress callback
        def on_tick_end(tick: int):
            if tick % 100 == 0:
                metrics = aggregator.get_current_metrics()
                emp_rate = metrics.get("employment", {}).get("current_employment_rate", 0)
                logger.info(f"Tick {tick}: Employment rate = {emp_rate:.2%}")
        
        tick_loop.on_tick_end = on_tick_end
    
    tick_loop.run()
    
    elapsed = time.time() - start_time
    
    # Finalize metrics
    result = aggregator.finalize_run(seed, tick_loop.current_tick)
    
    if verbose:
        logger.info(f"Simulation completed in {elapsed:.2f}s")
        logger.info(f"Final tick: {tick_loop.current_tick}")
        print("\n" + aggregator.summary())
    
    return {
        "seed": seed,
        "ticks": tick_loop.current_tick,
        "elapsed_seconds": elapsed,
        "metrics": result.metrics,
    }


def run_batch(
    seeds: list,
    population: int = 100,
    max_ticks: int = 1000,
) -> list:
    """
    Run multiple simulations with different seeds.
    
    Args:
        seeds: List of seeds to use
        population: Number of citizens
        max_ticks: Maximum ticks per run
        
    Returns:
        list: Results from all runs
    """
    logger = logging.getLogger("urbanium")
    results = []
    
    for i, seed in enumerate(seeds):
        logger.info(f"Running simulation {i+1}/{len(seeds)} with seed {seed}")
        result = run_simulation(
            seed=seed,
            population=population,
            max_ticks=max_ticks,
            verbose=False,
        )
        results.append(result)
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Urbanium - Deterministic city simulation"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--population", type=int, default=100,
        help="Number of citizens"
    )
    parser.add_argument(
        "--ticks", type=int, default=1000,
        help="Maximum number of ticks"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--batch", type=int, default=1,
        help="Number of runs (with different seeds)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output file for results (JSON)"
    )
    
    # Multi-agent mode
    parser.add_argument(
        "--multiagent", action="store_true",
        help="Run in multi-agent autonomous mode"
    )
    parser.add_argument(
        "--duration", type=float, default=60.0,
        help="Multi-agent simulation duration in seconds"
    )
    
    # AI options
    parser.add_argument(
        "--ai", action="store_true",
        help="Enable AI-powered decision making"
    )
    parser.add_argument(
        "--ai-url", type=str, default="http://localhost:1234/v1",
        help="AI API endpoint URL (default: LM Studio)"
    )
    parser.add_argument(
        "--ai-key", type=str, default="lm-studio",
        help="AI API key"
    )
    parser.add_argument(
        "--ai-model", type=str, default="local-model",
        help="AI model name"
    )
    parser.add_argument(
        "--ai-temperature", type=float, default=0.1,
        help="AI sampling temperature (0.0-1.0)"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    # Set up AI config if enabled
    ai_config = None
    if args.ai:
        if not HAS_AI:
            print("Error: AI features require the 'openai' package.")
            print("Install with: pip install urbanium[ai]")
            return
        
        ai_config = AIConfig(
            base_url=args.ai_url,
            api_key=args.ai_key,
            model=args.ai_model,
            temperature=args.ai_temperature,
        )
        print(f"AI enabled: {args.ai_url} (model: {args.ai_model})")
    
    # Multi-agent mode
    if args.multiagent:
        import asyncio
        from urbanium.multiagent import run_multiagent_simulation
        from urbanium.engine.world import World
        from urbanium.scenarios import SimpleCityScenario
        from urbanium.scenarios.base import ScenarioConfig
        
        # Create world and citizens
        world = World(seed=args.seed)
        config = ScenarioConfig(
            name="Multi-Agent Simulation",
            seed=args.seed,
            population_size=args.population,
        )
        scenario = SimpleCityScenario(config=config)
        citizens = scenario.initialize(world)
        
        # Run multi-agent simulation
        result = asyncio.run(
            run_multiagent_simulation(
                world=world,
                citizens=citizens,
                duration=args.duration,
                use_ai=args.ai,
                ai_config=ai_config,
                verbose=True,
            )
        )
    elif args.batch > 1:
        # Batch mode
        seeds = [args.seed + i for i in range(args.batch)]
        results = run_batch(
            seeds=seeds,
            population=args.population,
            max_ticks=args.ticks,
        )
        
        # Analyze cross-run results
        print("\n=== Batch Results ===")
        print(f"Runs: {len(results)}")
        
        emp_rates = [r["metrics"]["employment"]["current_employment_rate"] for r in results]
        print(f"Employment rate: {sum(emp_rates)/len(emp_rates):.2%} (mean)")
        
        gini_values = [r["metrics"]["economic"]["current_gini"] for r in results]
        print(f"Gini coefficient: {sum(gini_values)/len(gini_values):.4f} (mean)")
        result = results
    else:
        # Single run (tick-based)
        result = run_simulation(
            seed=args.seed,
            population=args.population,
            max_ticks=args.ticks,
            use_ai=args.ai,
            ai_config=ai_config,
        )
    
    # Save results if output specified
    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
