"""
WorkShiftAction - Perform a work shift at the citizen's job.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, TYPE_CHECKING

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


@dataclass
class WorkShiftAction(Action):
    """
    Perform a work shift.
    
    Prerequisites:
    - Citizen must be employed
    - Must be during work hours
    - Must have sufficient energy
    
    Effects:
    - Earn wage
    - Consume energy
    - Gain work experience
    - Satisfy financial need
    """
    
    action_type: ActionType = ActionType.WORK_SHIFT
    energy_cost: float = 20.0
    duration: int = 8  # Standard work shift
    
    # Work-specific parameters
    overtime: bool = False
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can work."""
        # Must be employed
        if not citizen.is_employed:
            return False
        
        # Must have enough energy
        if citizen.resources.energy < self.energy_cost:
            return False
        
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute work shift and return results."""
        # Get the citizen's job info from world
        # For now, use a base wage
        base_wage = 100.0
        
        # Calculate earnings (could factor in skills, overtime, etc.)
        earnings = base_wage
        if self.overtime:
            earnings *= 1.5
            self.energy_cost *= 1.5
        
        # Apply taxes
        tax = world.institutions.calculate_income_tax(earnings)
        net_earnings = earnings - tax
        world.institutions.collect_taxes(tax)
        
        return {
            "success": True,
            "money_change": net_earnings,
            "energy_change": -self.energy_cost,
            "needs_satisfied": {
                "financial": 30.0,
                "esteem": 10.0,
            },
            "experience_gained": {
                "technical": 1.0,
            },
        }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        base_wage = 100.0
        expected_net = base_wage * 0.8  # Estimate after tax
        
        if self.overtime:
            expected_net *= 1.5
        
        return {
            "money_change": expected_net,
            "energy_change": -self.energy_cost,
            "needs_satisfied": {
                "financial": 30.0,
            },
        }
