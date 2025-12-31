"""
SocializeAction - Interact with other citizens.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from enum import Enum

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


class SocialActivity(Enum):
    """Types of social activities."""
    CASUAL = "casual"
    MEAL = "meal"
    ENTERTAINMENT = "entertainment"
    GATHERING = "gathering"


@dataclass
class SocializeAction(Action):
    """
    Socialize with other citizens.
    
    Prerequisites:
    - Must have social connections (or be at a social location)
    - Must have enough energy
    - Must afford any costs
    
    Effects:
    - Satisfy social need
    - Strengthen social ties
    - Small entertainment/hedonism satisfaction
    - Consume energy and possibly money
    """
    
    action_type: ActionType = ActionType.SOCIALIZE
    energy_cost: float = 10.0
    duration: int = 2
    
    # Socialize-specific parameters
    activity: SocialActivity = SocialActivity.CASUAL
    target_ids: List[str] = field(default_factory=list)
    
    # Activity costs and benefits
    _activity_data: Dict = field(default_factory=lambda: {
        SocialActivity.CASUAL: {"cost": 0.0, "social": 20.0, "energy": 10.0},
        SocialActivity.MEAL: {"cost": 20.0, "social": 40.0, "energy": 5.0},
        SocialActivity.ENTERTAINMENT: {"cost": 30.0, "social": 50.0, "energy": 15.0},
        SocialActivity.GATHERING: {"cost": 10.0, "social": 60.0, "energy": 20.0},
    })
    
    def __post_init__(self):
        """Set cost based on activity type."""
        activity_info = self._activity_data.get(
            self.activity, 
            self._activity_data[SocialActivity.CASUAL]
        )
        self.money_cost = activity_info["cost"]
        self.energy_cost = activity_info["energy"]
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can socialize."""
        # Must have enough energy
        if citizen.resources.energy < self.energy_cost:
            return False
        
        # Must afford the cost
        if not citizen.resources.can_afford(self.money_cost):
            return False
        
        # Should have social connections (but can socialize without)
        # This is a soft requirement
        
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute socializing and return results."""
        activity_info = self._activity_data.get(
            self.activity,
            self._activity_data[SocialActivity.CASUAL]
        )
        
        # Bonus for socializing with known people
        social_bonus = 0.0
        connections_strengthened = []
        
        # TODO: Update social ties for target_ids
        if self.target_ids:
            social_bonus = len(self.target_ids) * 5.0
            connections_strengthened = self.target_ids
        
        return {
            "success": True,
            "money_change": -activity_info["cost"],
            "energy_change": -activity_info["energy"],
            "needs_satisfied": {
                "social": activity_info["social"] + social_bonus,
                "belonging": 10.0,
            },
            "connections_strengthened": connections_strengthened,
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        activity_info = self._activity_data.get(
            self.activity,
            self._activity_data[SocialActivity.CASUAL]
        )
        
        return {
            "money_change": -activity_info["cost"],
            "energy_change": -activity_info["energy"],
            "needs_satisfied": {
                "social": activity_info["social"],
            },
        }
