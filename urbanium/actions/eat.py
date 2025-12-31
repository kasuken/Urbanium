"""
EatAction - Consume food to satisfy hunger.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, TYPE_CHECKING
from enum import Enum

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


class MealType(Enum):
    """Types of meals."""
    BASIC = "basic"
    STANDARD = "standard"
    QUALITY = "quality"


@dataclass
class EatAction(Action):
    """
    Eat a meal.
    
    Prerequisites:
    - Must have enough money for the meal
    
    Effects:
    - Consume money (meal cost)
    - Satisfy food need
    - Small energy boost
    """
    
    action_type: ActionType = ActionType.EAT
    energy_cost: float = 0.0
    duration: int = 1
    
    # Eat-specific parameters
    meal_type: MealType = MealType.STANDARD
    
    # Meal costs and benefits
    _meal_data: Dict = field(default_factory=lambda: {
        MealType.BASIC: {"cost": 5.0, "satisfaction": 30.0, "energy": 5.0},
        MealType.STANDARD: {"cost": 15.0, "satisfaction": 50.0, "energy": 10.0},
        MealType.QUALITY: {"cost": 40.0, "satisfaction": 80.0, "energy": 15.0},
    })
    
    def __post_init__(self):
        """Set cost based on meal type."""
        meal_info = self._meal_data.get(self.meal_type, self._meal_data[MealType.STANDARD])
        self.money_cost = meal_info["cost"]
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can afford the meal."""
        return citizen.resources.can_afford(self.money_cost)
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute eating and return results."""
        meal_info = self._meal_data.get(self.meal_type, self._meal_data[MealType.STANDARD])
        
        return {
            "success": True,
            "money_change": -meal_info["cost"],
            "energy_change": meal_info["energy"],
            "needs_satisfied": {
                "food": meal_info["satisfaction"],
            },
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        meal_info = self._meal_data.get(self.meal_type, self._meal_data[MealType.STANDARD])
        
        return {
            "money_change": -meal_info["cost"],
            "energy_change": meal_info["energy"],
            "needs_satisfied": {
                "food": meal_info["satisfaction"],
            },
        }
