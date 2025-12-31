"""
Simulation coordinator for multi-agent system.

Manages the lifecycle and coordination of all autonomous agents.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, TYPE_CHECKING, Callable
import logging

from urbanium.multiagent.messaging import MessageBus, Message, MessageType
from urbanium.multiagent.interactions import InteractionManager
from urbanium.multiagent.runner import AgentRunner, AgentContext, AgentState

if TYPE_CHECKING:
    from urbanium.agents.citizen import Citizen
    from urbanium.engine.world import World
    from urbanium.ai.decision import AIDecisionModel

logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for the simulation."""
    
    # Timing
    tick_duration: float = 0.1          # Seconds per simulation tick
    max_duration: float = 60.0          # Maximum simulation duration in seconds
    
    # Agent behavior
    agent_think_interval: float = 1.0   # Seconds between agent decisions
    agent_action_interval: float = 0.5  # Minimum seconds between actions
    social_probability: float = 0.3     # Chance agents initiate interactions
    
    # AI
    use_ai: bool = False
    ai_config: Optional[Any] = None
    
    # Metrics
    collect_metrics: bool = True
    metrics_interval: float = 5.0       # Seconds between metrics collection


class SimulationCoordinator:
    """
    Coordinates the multi-agent simulation.
    
    Responsibilities:
    - Creating and managing agent runners
    - Providing shared infrastructure (message bus, interactions)
    - Collecting metrics and statistics
    - Managing simulation lifecycle
    """
    
    def __init__(
        self,
        world: "World",
        citizens: List["Citizen"],
        config: Optional[SimulationConfig] = None,
        ai_model: Optional["AIDecisionModel"] = None,
    ):
        """
        Initialize the simulation coordinator.
        
        Args:
            world: The simulation world
            citizens: List of citizens to run as agents
            config: Simulation configuration
            ai_model: Optional shared AI model for decisions
        """
        self.world = world
        self.citizens = citizens
        self.config = config or SimulationConfig()
        self.ai_model = ai_model
        
        # Shared infrastructure
        self.message_bus = MessageBus()
        self.interaction_manager = InteractionManager()
        
        # Agent runners
        self.runners: Dict[str, AgentRunner] = {}
        
        # State
        self._running = False
        self._start_time: Optional[datetime] = None
        self._tick = 0
        
        # Metrics
        self._metrics_history: List[Dict] = []
        
        # Event callbacks
        self._on_tick: List[Callable] = []
        self._on_action: List[Callable] = []
        self._on_interaction: List[Callable] = []
    
    def on_tick(self, callback: Callable):
        """Register a tick callback."""
        self._on_tick.append(callback)
    
    def on_action(self, callback: Callable):
        """Register an action callback."""
        self._on_action.append(callback)
    
    def on_interaction(self, callback: Callable):
        """Register an interaction callback."""
        self._on_interaction.append(callback)
    
    async def setup(self):
        """Set up the simulation."""
        logger.info(f"Setting up simulation with {len(self.citizens)} agents")
        
        # Create agent runners for each citizen
        for citizen in self.citizens:
            context = AgentContext(
                citizen=citizen,
                world=self.world,
                message_bus=self.message_bus,
                interaction_manager=self.interaction_manager,
                ai_model=self.ai_model,
                think_interval=self.config.agent_think_interval,
                action_interval=self.config.agent_action_interval,
                social_probability=self.config.social_probability,
            )
            
            runner = AgentRunner(
                context=context,
                on_action=self._handle_action,
                on_interaction=self._handle_interaction,
            )
            
            self.runners[citizen.id] = runner
        
        logger.info(f"Created {len(self.runners)} agent runners")
    
    def _handle_action(self, citizen: "Citizen", action: Any, result: Any):
        """Handle an agent action."""
        for callback in self._on_action:
            try:
                callback(citizen, action, result)
            except Exception as e:
                logger.error(f"Action callback error: {e}")
    
    def _handle_interaction(self, citizen: "Citizen", interaction: Any):
        """Handle an agent interaction."""
        for callback in self._on_interaction:
            try:
                callback(citizen, interaction)
            except Exception as e:
                logger.error(f"Interaction callback error: {e}")
    
    async def run(self) -> Dict:
        """
        Run the simulation.
        
        Returns:
            Final simulation results
        """
        if not self.runners:
            await self.setup()
        
        self._running = True
        self._start_time = datetime.now()
        self._tick = 0
        
        logger.info("Starting multi-agent simulation")
        
        try:
            # Start all agents
            start_tasks = [runner.start() for runner in self.runners.values()]
            await asyncio.gather(*start_tasks)
            
            # Main simulation loop
            metrics_last = datetime.now()
            
            while self._running:
                # Check duration limit
                elapsed = (datetime.now() - self._start_time).total_seconds()
                if elapsed >= self.config.max_duration:
                    logger.info("Simulation duration limit reached")
                    break
                
                # Tick callbacks
                self._tick += 1
                for callback in self._on_tick:
                    try:
                        callback(self._tick, self.world)
                    except Exception as e:
                        logger.error(f"Tick callback error: {e}")
                
                # Collect metrics periodically
                if self.config.collect_metrics:
                    metrics_elapsed = (datetime.now() - metrics_last).total_seconds()
                    if metrics_elapsed >= self.config.metrics_interval:
                        self._collect_metrics()
                        metrics_last = datetime.now()
                
                # Wait for tick duration
                await asyncio.sleep(self.config.tick_duration)
            
        finally:
            # Stop all agents
            await self.stop()
        
        return self.get_results()
    
    async def stop(self):
        """Stop the simulation."""
        self._running = False
        
        logger.info("Stopping simulation...")
        
        # Stop all agents
        stop_tasks = [runner.stop() for runner in self.runners.values()]
        await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        logger.info("Simulation stopped")
    
    def _collect_metrics(self):
        """Collect current simulation metrics."""
        metrics = {
            "tick": self._tick,
            "elapsed_seconds": (datetime.now() - self._start_time).total_seconds() if self._start_time else 0,
            "agents": {
                "total": len(self.runners),
                "by_state": {},
            },
            "messaging": self.message_bus.get_statistics(),
            "interactions": self.interaction_manager.get_statistics(),
            "actions": {
                "total": sum(r.actions_taken for r in self.runners.values()),
            },
        }
        
        # Count agents by state
        state_counts: Dict[str, int] = {}
        for runner in self.runners.values():
            state = runner.context.state.name
            state_counts[state] = state_counts.get(state, 0) + 1
        metrics["agents"]["by_state"] = state_counts
        
        self._metrics_history.append(metrics)
        
        logger.info(
            f"Tick {self._tick}: "
            f"actions={metrics['actions']['total']}, "
            f"messages={metrics['messaging']['messages_sent']}, "
            f"interactions={metrics['interactions']['total_interactions']}"
        )
    
    def get_results(self) -> Dict:
        """Get final simulation results."""
        elapsed = 0.0
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
        
        return {
            "duration_seconds": elapsed,
            "total_ticks": self._tick,
            "agents": {
                "count": len(self.runners),
                "statistics": [r.get_statistics() for r in self.runners.values()],
            },
            "messaging": self.message_bus.get_statistics(),
            "interactions": self.interaction_manager.get_statistics(),
            "metrics_history": self._metrics_history,
        }
    
    def get_agent_states(self) -> Dict[str, str]:
        """Get current state of all agents."""
        return {
            agent_id: runner.context.state.name
            for agent_id, runner in self.runners.items()
        }
    
    def get_agent_locations(self) -> Dict[str, str]:
        """Get current location of all agents."""
        return {
            agent_id: runner.citizen.current_location or "unknown"
            for agent_id, runner in self.runners.items()
        }


async def run_multiagent_simulation(
    world: "World",
    citizens: List["Citizen"],
    duration: float = 60.0,
    use_ai: bool = False,
    ai_config: Optional[Any] = None,
    on_tick: Optional[Callable] = None,
    verbose: bool = True,
) -> Dict:
    """
    Convenience function to run a multi-agent simulation.
    
    Args:
        world: The simulation world
        citizens: List of citizens
        duration: Maximum simulation duration in seconds
        use_ai: Whether to use AI for decisions
        ai_config: AI configuration
        on_tick: Optional tick callback
        verbose: Whether to print progress
        
    Returns:
        Simulation results
    """
    config = SimulationConfig(
        max_duration=duration,
        use_ai=use_ai,
        ai_config=ai_config,
    )
    
    # Create AI model if needed
    ai_model = None
    if use_ai:
        try:
            from urbanium.ai import AIDecisionModel, AIConfig
            if ai_config:
                ai_model = AIDecisionModel.create(ai_config)
            else:
                ai_model = AIDecisionModel.create()
        except ImportError:
            logger.warning("AI features not available")
    
    coordinator = SimulationCoordinator(
        world=world,
        citizens=citizens,
        config=config,
        ai_model=ai_model,
    )
    
    if on_tick:
        coordinator.on_tick(on_tick)
    
    if verbose:
        def print_progress(tick: int, world: "World"):
            if tick % 100 == 0:
                print(f"  Tick {tick}...")
        coordinator.on_tick(print_progress)
    
    print(f"\nStarting multi-agent simulation with {len(citizens)} citizens...")
    print(f"Duration: {duration}s, AI: {'enabled' if use_ai else 'disabled'}")
    
    results = await coordinator.run()
    
    if verbose:
        print(f"\n=== Simulation Complete ===")
        print(f"Duration: {results['duration_seconds']:.1f}s")
        print(f"Ticks: {results['total_ticks']}")
        print(f"Total actions: {sum(a['actions_taken'] for a in results['agents']['statistics'])}")
        print(f"Total messages: {results['messaging']['messages_sent']}")
        print(f"Total interactions: {results['interactions']['total_interactions']}")
    
    return results
