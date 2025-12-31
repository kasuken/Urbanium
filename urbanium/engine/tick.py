"""
TickLoop - The discrete time simulation loop.

The world advances in discrete ticks. Each tick follows a strict sequence:
1. World updates exogenous systems
2. Agents receive their local state
3. Agents propose one action
4. World validates and executes
5. Metrics are recorded
"""

from dataclasses import dataclass, field
from typing import List, Callable, Optional
import logging

from urbanium.engine.world import World
from urbanium.agents.citizen import Citizen
from urbanium.metrics.observer import MetricsObserver


logger = logging.getLogger(__name__)


@dataclass
class TickLoop:
    """
    The main simulation loop.
    
    Manages the discrete time progression and orchestrates
    world updates, agent decisions, and metrics collection.
    """
    
    world: World
    agents: List[Citizen] = field(default_factory=list)
    observers: List[MetricsObserver] = field(default_factory=list)
    
    max_ticks: int = 1000
    current_tick: int = 0
    
    # Callbacks for custom logic
    on_tick_start: Optional[Callable[[int], None]] = None
    on_tick_end: Optional[Callable[[int], None]] = None
    
    def run(self, num_ticks: Optional[int] = None) -> None:
        """
        Run the simulation for a specified number of ticks.
        
        Args:
            num_ticks: Number of ticks to run. Defaults to max_ticks.
        """
        ticks_to_run = num_ticks or self.max_ticks
        
        logger.info(f"Starting simulation for {ticks_to_run} ticks")
        
        for _ in range(ticks_to_run):
            if not self._run_single_tick():
                break
        
        logger.info(f"Simulation completed at tick {self.current_tick}")
    
    def _run_single_tick(self) -> bool:
        """
        Execute a single tick of the simulation.
        
        Returns:
            bool: True if simulation should continue, False to stop.
        """
        self.current_tick += 1
        
        # Callback: tick start
        if self.on_tick_start:
            self.on_tick_start(self.current_tick)
        
        # Step 1: World updates exogenous systems
        self.world.update_exogenous_systems()
        
        # Step 2-4: Agent decision loop
        for agent in self.agents:
            # Step 2: Agent receives local state
            local_state = self.world.get_local_state(agent.id)
            
            # Step 3: Agent proposes one action
            action = agent.decide(local_state)
            
            if action is not None:
                # Step 4: World validates and executes
                result = self.world.execute_action(agent.id, action)
                agent.receive_action_result(result)
        
        # Step 5: Metrics are recorded
        self._record_metrics()
        
        # Callback: tick end
        if self.on_tick_end:
            self.on_tick_end(self.current_tick)
        
        return self.current_tick < self.max_ticks
    
    def _record_metrics(self) -> None:
        """Record metrics from all observers."""
        state_snapshot = self.world.get_state_snapshot()
        
        for observer in self.observers:
            observer.observe(self.current_tick, state_snapshot, self.agents)
    
    def add_agent(self, agent: Citizen) -> None:
        """Add an agent to the simulation."""
        self.agents.append(agent)
    
    def add_observer(self, observer: MetricsObserver) -> None:
        """Add a metrics observer to the simulation."""
        self.observers.append(observer)
    
    def get_metrics(self) -> dict:
        """Get aggregated metrics from all observers."""
        return {
            observer.name: observer.get_results()
            for observer in self.observers
        }
