"""
World - The central simulation container.

The world owns truth. It manages all systems and validates all agent actions.
"""

from dataclasses import dataclass, field
from typing import Optional
import random

from urbanium.engine.state import WorldState
from urbanium.engine.time import TimeSystem
from urbanium.engine.geography import Geography
from urbanium.engine.economy import Economy
from urbanium.engine.institutions import Institutions
from urbanium.engine.events import EventSystem


@dataclass
class World:
    """
    The World is the single source of truth for the simulation.
    
    It contains all systems (time, geography, economy, institutions, events)
    and manages the population of agents.
    """
    
    seed: int = 42
    state: WorldState = field(default_factory=WorldState)
    time: TimeSystem = field(default_factory=TimeSystem)
    geography: Geography = field(default_factory=Geography)
    economy: Economy = field(default_factory=Economy)
    institutions: Institutions = field(default_factory=Institutions)
    events: EventSystem = field(default_factory=EventSystem)
    
    _rng: random.Random = field(init=False, repr=False)
    
    def __post_init__(self):
        """Initialize the random number generator with the seed."""
        self._rng = random.Random(self.seed)
    
    def initialize(self) -> None:
        """Initialize all world systems."""
        self.time.initialize()
        self.geography.initialize()
        self.economy.initialize()
        self.institutions.initialize()
        self.events.initialize()
        self.state.initialized = True
    
    def get_random(self) -> random.Random:
        """Get the world's random number generator for deterministic behavior."""
        return self._rng
    
    def update_exogenous_systems(self) -> None:
        """
        Update all exogenous systems at the start of each tick.
        
        This includes time progression, market updates, and scheduled events.
        """
        self.time.advance()
        self.economy.update(self.time.current_tick)
        self.events.process_scheduled(self.time.current_tick)
    
    def get_local_state(self, agent_id: str) -> dict:
        """
        Get the local state visible to a specific agent.
        
        Agents only see what they can observe from their position and connections.
        """
        # TODO: Implement visibility based on agent location and social ties
        return {
            "time": self.time.current_tick,
            "economy": self.economy.get_public_state(),
        }
    
    def validate_action(self, agent_id: str, action) -> bool:
        """
        Validate whether an action is legal for the given agent.
        
        Actions must satisfy all constraints to be executed.
        """
        from urbanium.engine.validator import ActionValidator
        return ActionValidator.validate(self, agent_id, action)
    
    def execute_action(self, agent_id: str, action) -> dict:
        """
        Execute a validated action and return the result.
        
        The world enforces legality, cost, and consequences.
        """
        if not self.validate_action(agent_id, action):
            return {"success": False, "reason": "Action validation failed"}
        
        # Execute the action and update world state
        result = action.execute(self, agent_id)
        return result
    
    def get_state_snapshot(self) -> WorldState:
        """Get a snapshot of the current world state for metrics."""
        return self.state.copy()
