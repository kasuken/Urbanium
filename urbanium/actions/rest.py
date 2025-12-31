"""
RestAction - Rest to recover energy.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, TYPE_CHECKING

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


@dataclass
class RestAction(Action):
    """
    Rest to recover energy.
    
    Prerequisites:
    - None (can always rest)
    
    Effects:
    - Restore energy
    - Satisfy rest need
    """
    
    action_type: ActionType = ActionType.REST
    energy_cost: float = 0.0
    duration: int = 8  # Standard rest period
    
    # Rest-specific parameters
    quality: float = 1.0  # Quality multiplier (affected by home, noise, etc.)
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Rest is always available."""
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute rest and return results."""
        # Base energy restoration
        base_restoration = 50.0
        
        # Adjust for quality
        actual_restoration = base_restoration * self.quality
        
        # Bonus if resting at home
        # TODO: Check if at home location
        
        return {
            "success": True,
            "energy_change": actual_restoration,
            "needs_satisfied": {
                "rest": 60.0 * self.quality,
            },
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        return {
            "energy_change": 50.0 * self.quality,
            "needs_satisfied": {
                "rest": 60.0 * self.quality,
            },
        }
