"""
Decision - Decision-making models for agents.

Decision-making can be implemented using:
- Utility functions
- Rule-based logic
- GOAP (Goal-Oriented Action Planning)
- Small local language models (as decision filters)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum

if TYPE_CHECKING:
    from urbanium.agents.citizen import Citizen
    from urbanium.actions.base import Action


class DecisionStrategy(Enum):
    """Available decision-making strategies."""
    UTILITY = "utility"
    RULE_BASED = "rule_based"
    GOAP = "goap"
    RANDOM = "random"


@dataclass
class DecisionModel:
    """
    The decision-making model for a citizen.
    
    Supports multiple strategies:
    - Utility-based: Maximize expected utility
    - Rule-based: Follow priority rules
    - GOAP: Plan to achieve goals
    - Random: For testing/baseline
    """
    
    strategy: DecisionStrategy = DecisionStrategy.UTILITY
    
    # Utility weights for different outcomes
    utility_weights: Dict[str, float] = field(default_factory=dict)
    
    # Rules for rule-based decisions (priority ordered)
    rules: List[Callable] = field(default_factory=list)
    
    # Goals for GOAP
    goals: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default weights."""
        if not self.utility_weights:
            self.utility_weights = {
                "money": 1.0,
                "energy": 0.8,
                "food_need": 1.2,
                "rest_need": 1.0,
                "social_need": 0.6,
                "financial_need": 1.1,
            }
    
    def select_action(
        self,
        citizen: "Citizen",
        local_state: dict,
        available_actions: List["Action"]
    ) -> Optional["Action"]:
        """
        Select an action from the available options.
        
        Args:
            citizen: The citizen making the decision
            local_state: The local world state
            available_actions: List of valid actions
            
        Returns:
            The selected action, or None
        """
        if not available_actions:
            return None
        
        if self.strategy == DecisionStrategy.UTILITY:
            return self._select_by_utility(citizen, local_state, available_actions)
        elif self.strategy == DecisionStrategy.RULE_BASED:
            return self._select_by_rules(citizen, local_state, available_actions)
        elif self.strategy == DecisionStrategy.GOAP:
            return self._select_by_goap(citizen, local_state, available_actions)
        else:  # Random
            import random
            return random.choice(available_actions)
    
    def _select_by_utility(
        self,
        citizen: "Citizen",
        local_state: dict,
        available_actions: List["Action"]
    ) -> "Action":
        """Select action with highest expected utility."""
        best_action = None
        best_utility = float("-inf")
        
        for action in available_actions:
            utility = self._calculate_utility(citizen, local_state, action)
            if utility > best_utility:
                best_utility = utility
                best_action = action
        
        return best_action
    
    def _calculate_utility(
        self,
        citizen: "Citizen",
        local_state: dict,
        action: "Action"
    ) -> float:
        """
        Calculate the expected utility of an action.
        
        Considers:
        - Expected resource changes
        - Need satisfaction
        - Costs
        - Citizen's values and priorities
        """
        utility = 0.0
        
        # Get expected effects from action
        expected_effects = action.get_expected_effects()
        
        # Money utility
        if "money_change" in expected_effects:
            utility += expected_effects["money_change"] * self.utility_weights.get("money", 1.0)
        
        # Energy utility
        if "energy_change" in expected_effects:
            utility += expected_effects["energy_change"] * self.utility_weights.get("energy", 0.8)
        
        # Need satisfaction utility
        if "needs_satisfied" in expected_effects:
            for need_type, amount in expected_effects["needs_satisfied"].items():
                # Higher utility for more urgent needs
                current_level = citizen.needs.get_level(need_type)
                urgency_multiplier = 2.0 - (current_level / 100.0)  # Higher when need is low
                
                weight_key = f"{need_type.value}_need" if hasattr(need_type, 'value') else f"{need_type}_need"
                base_weight = self.utility_weights.get(weight_key, 1.0)
                
                utility += amount * base_weight * urgency_multiplier
        
        # Cost penalty
        cost = action.get_cost()
        if cost > 0:
            if not citizen.resources.can_afford(cost):
                return float("-inf")  # Can't afford
            utility -= cost * 0.5  # Mild penalty for spending
        
        return utility
    
    def _select_by_rules(
        self,
        citizen: "Citizen",
        local_state: dict,
        available_actions: List["Action"]
    ) -> Optional["Action"]:
        """Select action based on priority rules."""
        # Default rules if none specified
        if not self.rules:
            self.rules = self._get_default_rules()
        
        # Try each rule in priority order
        for rule in self.rules:
            action = rule(citizen, local_state, available_actions)
            if action is not None:
                return action
        
        # Fallback to first available action
        return available_actions[0] if available_actions else None
    
    def _get_default_rules(self) -> List[Callable]:
        """Get default decision rules."""
        from urbanium.actions.base import ActionType
        
        def critical_needs_rule(citizen, state, actions):
            """Prioritize critical needs."""
            critical = citizen.needs.get_critical_needs()
            if not critical:
                return None
            
            # Map needs to actions
            need_to_action = {
                "food": ActionType.EAT,
                "rest": ActionType.REST,
            }
            
            for need in critical:
                target_action_type = need_to_action.get(need.need_type.value)
                if target_action_type:
                    for action in actions:
                        if action.action_type == target_action_type:
                            return action
            return None
        
        def work_rule(citizen, state, actions):
            """Work if it's work hours and employed."""
            time_info = state.get("time", {})
            if isinstance(time_info, int):
                # Simple time check (assuming work hours 9-17)
                hour = (time_info % 24)
                if 9 <= hour < 17 and citizen.is_employed:
                    for action in actions:
                        if action.action_type == ActionType.WORK_SHIFT:
                            return action
            return None
        
        return [critical_needs_rule, work_rule]
    
    def _select_by_goap(
        self,
        citizen: "Citizen",
        local_state: dict,
        available_actions: List["Action"]
    ) -> Optional["Action"]:
        """Select action using Goal-Oriented Action Planning."""
        # Simple GOAP: find action that moves toward most important goal
        
        if not self.goals:
            # Default goals based on needs
            self.goals = [
                {"type": "satisfy_need", "need": "food", "priority": 1},
                {"type": "satisfy_need", "need": "rest", "priority": 2},
                {"type": "earn_money", "priority": 3},
            ]
        
        # Sort goals by priority
        sorted_goals = sorted(self.goals, key=lambda g: g.get("priority", 99))
        
        for goal in sorted_goals:
            if self._goal_needs_action(citizen, goal):
                action = self._find_action_for_goal(goal, available_actions)
                if action:
                    return action
        
        return available_actions[0] if available_actions else None
    
    def _goal_needs_action(self, citizen: "Citizen", goal: Dict) -> bool:
        """Check if a goal needs to be pursued."""
        goal_type = goal.get("type")
        
        if goal_type == "satisfy_need":
            from urbanium.agents.needs import NeedType
            need_name = goal.get("need")
            try:
                need_type = NeedType(need_name)
                need = citizen.needs.get(need_type)
                return need and need.current_level < 50
            except ValueError:
                return False
        
        elif goal_type == "earn_money":
            return citizen.resources.money < 100
        
        return False
    
    def _find_action_for_goal(
        self,
        goal: Dict,
        available_actions: List["Action"]
    ) -> Optional["Action"]:
        """Find an action that helps achieve the goal."""
        from urbanium.actions.base import ActionType
        
        goal_type = goal.get("type")
        
        goal_to_actions = {
            "satisfy_need": {
                "food": ActionType.EAT,
                "rest": ActionType.REST,
                "social": ActionType.SOCIALIZE,
            },
            "earn_money": ActionType.WORK_SHIFT,
        }
        
        if goal_type == "satisfy_need":
            need = goal.get("need")
            action_type = goal_to_actions.get(goal_type, {}).get(need)
        else:
            action_type = goal_to_actions.get(goal_type)
        
        if action_type:
            for action in available_actions:
                if action.action_type == action_type:
                    return action
        
        return None
