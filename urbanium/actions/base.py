"""
Base Action - Abstract base class for all actions.

Actions are proposals that agents make. The world validates
and executes them, enforcing legality, cost, and consequences.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


class ActionType(Enum):
    """Types of actions available in v0."""
    WORK_SHIFT = "work_shift"
    REST = "rest"
    EAT = "eat"
    COMMUTE = "commute"
    SOCIALIZE = "socialize"
    JOB_SEARCH = "job_search"
    HOUSING_CHANGE = "housing_change"


@dataclass
class Action(ABC):
    """
    Base class for all actions.
    
    Actions are proposals that must be validated by the world
    before execution. Each action has:
    - Type identifier
    - Cost (resources required)
    - Duration (in ticks)
    - Prerequisites
    - Expected effects
    """
    
    action_type: ActionType
    
    # Cost and duration
    energy_cost: float = 0.0
    money_cost: float = 0.0
    duration: int = 1  # Ticks
    
    # Parameters (action-specific)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """
        Check if the action is properly formed.
        
        Override in subclasses for action-specific validation.
        """
        return True
    
    @abstractmethod
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """
        Check if the citizen meets prerequisites for this action.
        
        Args:
            citizen: The citizen attempting the action
            local_state: The local world state
            
        Returns:
            bool: True if prerequisites are met
        """
        pass
    
    @abstractmethod
    def execute(self, world: "World", agent_id: str) -> dict:
        """
        Execute the action in the world.
        
        This is called by the world after validation.
        
        Args:
            world: The world state
            agent_id: The ID of the agent performing the action
            
        Returns:
            dict: Result of the action execution
        """
        pass
    
    @abstractmethod
    def get_expected_effects(self) -> dict:
        """
        Get the expected effects of this action.
        
        Used by decision models to evaluate actions.
        
        Returns:
            dict: Expected changes to agent state
        """
        pass
    
    def get_cost(self) -> float:
        """Get the total monetary cost of the action."""
        return self.money_cost
    
    def get_energy_cost(self) -> float:
        """Get the energy cost of the action."""
        return self.energy_cost
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.action_type.value})"
