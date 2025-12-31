"""
HousingChangeAction - Change housing situation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING
from enum import Enum

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


class HousingChangeType(Enum):
    """Types of housing changes."""
    SEARCH = "search"  # Look for new housing
    MOVE = "move"  # Move to specific housing
    LEAVE = "leave"  # Leave current housing


@dataclass
class HousingChangeAction(Action):
    """
    Change housing situation.
    
    Prerequisites:
    - SEARCH: Must have enough energy
    - MOVE: Must have found housing and afford deposit
    - LEAVE: Must have current housing
    
    Effects:
    - May find housing (SEARCH)
    - Change housing location (MOVE)
    - Lose housing (LEAVE)
    - Various costs depending on action
    """
    
    action_type: ActionType = ActionType.HOUSING_CHANGE
    energy_cost: float = 20.0
    duration: int = 4
    
    # Housing change parameters
    change_type: HousingChangeType = HousingChangeType.SEARCH
    target_housing_id: Optional[str] = None
    
    def __post_init__(self):
        """Set costs based on change type."""
        if self.change_type == HousingChangeType.SEARCH:
            self.money_cost = 10.0  # Transport, application fees
            self.energy_cost = 20.0
        elif self.change_type == HousingChangeType.MOVE:
            self.money_cost = 500.0  # Deposit + first month (placeholder)
            self.energy_cost = 40.0
        else:  # LEAVE
            self.money_cost = 0.0
            self.energy_cost = 30.0
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can change housing."""
        # Must have enough energy
        if citizen.resources.energy < self.energy_cost:
            return False
        
        # Must afford the cost
        if not citizen.resources.can_afford(self.money_cost):
            return False
        
        # MOVE requires a target
        if self.change_type == HousingChangeType.MOVE:
            if not self.target_housing_id:
                return False
        
        # LEAVE requires current housing
        if self.change_type == HousingChangeType.LEAVE:
            if not citizen.has_home:
                return False
        
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute housing change and return results."""
        if self.change_type == HousingChangeType.SEARCH:
            return self._execute_search(world, agent_id)
        elif self.change_type == HousingChangeType.MOVE:
            return self._execute_move(world, agent_id)
        else:
            return self._execute_leave(world, agent_id)
    
    def _execute_search(self, world: "World", agent_id: str) -> dict:
        """Search for housing."""
        rng = world.get_random()
        
        # Get available housing
        available_housing = world.economy.get_available_housing()
        
        if not available_housing:
            return {
                "success": True,
                "found_housing": False,
                "reason": "No housing available",
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
        
        # Calculate success probability
        base_probability = min(0.4, len(available_housing) * 0.1)
        
        if rng.random() < base_probability:
            # Found housing!
            unit = rng.choice(available_housing)
            
            return {
                "success": True,
                "found_housing": True,
                "housing_id": unit.id,
                "rent": unit.rent,
                "location_id": unit.location_id,
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
        else:
            return {
                "success": True,
                "found_housing": False,
                "reason": "Search unsuccessful",
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
    
    def _execute_move(self, world: "World", agent_id: str) -> dict:
        """Move to housing."""
        # Verify housing is available
        housing = world.economy.housing_units.get(self.target_housing_id)
        
        if not housing or housing.occupied:
            return {
                "success": False,
                "reason": "Housing not available",
            }
        
        # Occupy the housing
        world.economy.occupy_housing(self.target_housing_id, agent_id)
        
        return {
            "success": True,
            "moved": True,
            "housing_id": self.target_housing_id,
            "location_id": housing.location_id,
            "money_change": -self.money_cost,
            "energy_change": -self.energy_cost,
            "needs_satisfied": {
                "shelter": 100.0,
                "safety": 50.0,
            },
        }
    
    def _execute_leave(self, world: "World", agent_id: str) -> dict:
        """Leave current housing."""
        return {
            "success": True,
            "left_housing": True,
            "energy_change": -self.energy_cost,
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        if self.change_type == HousingChangeType.SEARCH:
            return {
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
        elif self.change_type == HousingChangeType.MOVE:
            return {
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
                "needs_satisfied": {
                    "shelter": 100.0,
                },
            }
        else:
            return {
                "energy_change": -self.energy_cost,
            }
