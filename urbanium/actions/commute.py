"""
CommuteAction - Travel between locations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING
from enum import Enum

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


class TransportMode(Enum):
    """Modes of transportation."""
    WALK = "walk"
    TRANSIT = "transit"
    DRIVE = "drive"


@dataclass
class CommuteAction(Action):
    """
    Commute between locations.
    
    Prerequisites:
    - Must have a valid destination
    - Must have enough energy
    - Must afford transport cost (for transit/drive)
    
    Effects:
    - Change location
    - Consume energy
    - Consume money (if using paid transport)
    - Time passes
    """
    
    action_type: ActionType = ActionType.COMMUTE
    energy_cost: float = 5.0
    duration: int = 1
    
    # Commute-specific parameters
    destination: Optional[str] = None
    transport_mode: TransportMode = TransportMode.TRANSIT
    
    # Transport costs
    _transport_costs: Dict = field(default_factory=lambda: {
        TransportMode.WALK: 0.0,
        TransportMode.TRANSIT: 3.0,
        TransportMode.DRIVE: 10.0,
    })
    
    def __post_init__(self):
        """Set cost based on transport mode."""
        self.money_cost = self._transport_costs.get(self.transport_mode, 0.0)
        
        # Walking is slower but cheaper
        if self.transport_mode == TransportMode.WALK:
            self.duration = 3
            self.energy_cost = 15.0
        elif self.transport_mode == TransportMode.TRANSIT:
            self.duration = 2
            self.energy_cost = 5.0
        else:  # Drive
            self.duration = 1
            self.energy_cost = 3.0
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can commute."""
        # Must have a destination
        if not self.destination:
            return False
        
        # Must have enough energy
        if citizen.resources.energy < self.energy_cost:
            return False
        
        # Must afford the cost
        if not citizen.resources.can_afford(self.money_cost):
            return False
        
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute commute and return results."""
        # Validate destination exists
        if self.destination not in world.geography.locations:
            return {
                "success": False,
                "reason": "Invalid destination",
            }
        
        return {
            "success": True,
            "money_change": -self.money_cost,
            "energy_change": -self.energy_cost,
            "new_location": self.destination,
            "travel_time": self.duration,
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        return {
            "money_change": -self.money_cost,
            "energy_change": -self.energy_cost,
        }
