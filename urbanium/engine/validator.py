"""
ActionValidator - Validates agent actions against world constraints.

Actions are proposals. The world enforces legality, cost, and consequences.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.actions.base import Action


@dataclass
class ValidationResult:
    """Result of action validation."""
    valid: bool
    reason: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ActionValidator:
    """
    Validates actions proposed by agents.
    
    Ensures all constraints are satisfied before execution.
    """
    
    @staticmethod
    def validate(world: "World", agent_id: str, action: "Action") -> bool:
        """
        Validate an action for a specific agent.
        
        Args:
            world: The world state
            agent_id: The ID of the agent proposing the action
            action: The action to validate
            
        Returns:
            bool: True if the action is valid, False otherwise
        """
        result = ActionValidator.validate_detailed(world, agent_id, action)
        return result.valid
    
    @staticmethod
    def validate_detailed(world: "World", agent_id: str, action: "Action") -> ValidationResult:
        """
        Validate an action and return detailed results.
        
        Checks:
        1. Action is valid for the current time
        2. Agent has required resources
        3. Agent meets action prerequisites
        4. World state allows the action
        """
        # Check if action exists and is properly formed
        if action is None:
            return ValidationResult(valid=False, reason="No action provided")
        
        # Check action's own validation
        if not action.is_valid():
            return ValidationResult(valid=False, reason="Action failed internal validation")
        
        # Check time constraints
        if not ActionValidator._validate_time_constraints(world, action):
            return ValidationResult(valid=False, reason="Action not available at current time")
        
        # Check agent-specific constraints
        agent_validation = ActionValidator._validate_agent_constraints(world, agent_id, action)
        if not agent_validation.valid:
            return agent_validation
        
        # Check world state constraints
        world_validation = ActionValidator._validate_world_constraints(world, action)
        if not world_validation.valid:
            return world_validation
        
        return ValidationResult(valid=True)
    
    @staticmethod
    def _validate_time_constraints(world: "World", action: "Action") -> bool:
        """Check if the action is valid at the current time."""
        # Some actions are only available during certain times
        action_type = action.action_type
        current_hour = world.time.current_hour
        
        # Work shifts only during work hours
        if action_type.value == "work_shift" and not world.time.is_work_hours:
            return False
        
        return True
    
    @staticmethod
    def _validate_agent_constraints(world: "World", agent_id: str, action: "Action") -> ValidationResult:
        """Check if the agent can perform the action."""
        # Get agent state from world
        # This would check resources, skills, current state, etc.
        
        # Check cost
        cost = action.get_cost()
        # TODO: Verify agent has enough resources
        
        return ValidationResult(valid=True)
    
    @staticmethod
    def _validate_world_constraints(world: "World", action: "Action") -> ValidationResult:
        """Check if the world state allows the action."""
        # Check location constraints
        # Check capacity constraints
        # Check availability of targets (jobs, housing, etc.)
        
        return ValidationResult(valid=True)
