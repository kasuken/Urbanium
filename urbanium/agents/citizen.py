"""
Citizen - The core agent model.

Citizens are structured agents with bounded decision-making.
Every decision can be traced back to state, traits, and constraints.

Enhanced with:
- Memory system for remembering events and people
- Emotional state tracking (Plutchik's wheel + PAD model)
- Relationship management
- Life events tracking
- Life cycle and aging
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import uuid

from urbanium.agents.traits import Traits, Values
from urbanium.agents.needs import Needs
from urbanium.agents.skills import Skills
from urbanium.agents.social import SocialNetwork
from urbanium.agents.decision import DecisionModel

# New life simulation imports
from urbanium.agents.memory import MemorySystem
from urbanium.agents.emotions import EmotionalState
from urbanium.agents.relationships import RelationshipManager
from urbanium.agents.life_events import LifeEventManager
from urbanium.agents.lifecycle import LifeCycle, get_life_stage


@dataclass
class RoleBindings:
    """Role bindings for a citizen (job, home, etc.)."""
    job_id: Optional[str] = None
    employer_id: Optional[str] = None
    home_id: Optional[str] = None
    household_id: Optional[str] = None
    spouse_id: Optional[str] = None


@dataclass
class Resources:
    """Resources owned by a citizen."""
    money: float = 0.0
    energy: float = 100.0
    health: float = 100.0
    
    def can_afford(self, amount: float) -> bool:
        """Check if citizen can afford a cost."""
        return self.money >= amount
    
    def spend(self, amount: float) -> bool:
        """Spend money. Returns False if insufficient funds."""
        if not self.can_afford(amount):
            return False
        self.money -= amount
        return True
    
    def earn(self, amount: float) -> None:
        """Add money."""
        self.money += amount
    
    def consume_energy(self, amount: float) -> None:
        """Consume energy."""
        self.energy = max(0.0, self.energy - amount)
    
    def restore_energy(self, amount: float) -> None:
        """Restore energy."""
        self.energy = min(100.0, self.energy + amount)


@dataclass
class Finances:
    """Financial information for easier access."""
    cash: float = 500.0
    savings: float = 0.0
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0


@dataclass
class Citizen:
    """
    A citizen in the Urbanium simulation.
    
    Citizens are structured agents whose decisions are bounded,
    observable, and reproducible.
    
    Enhanced with:
    - Memory for remembering people and events
    - Emotions that affect decisions
    - Relationships with other citizens
    - Life events tracking (marriage, children, etc.)
    - Life cycle with aging
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    age: float = 25.0
    
    # Core components
    traits: Traits = field(default_factory=Traits)
    values: Values = field(default_factory=Values)
    needs: Needs = field(default_factory=Needs)
    skills: Skills = field(default_factory=Skills)
    resources: Resources = field(default_factory=Resources)
    social: SocialNetwork = field(default_factory=SocialNetwork)
    roles: RoleBindings = field(default_factory=RoleBindings)
    
    # Decision model
    decision_model: DecisionModel = field(default_factory=DecisionModel)
    
    # NEW: Life simulation systems
    memory: MemorySystem = field(default_factory=lambda: MemorySystem())
    emotions: EmotionalState = field(default_factory=EmotionalState)
    relationships: RelationshipManager = field(default_factory=lambda: RelationshipManager(owner_id=""))
    life_events: LifeEventManager = field(default_factory=lambda: LifeEventManager(citizen_id=""))
    lifecycle: LifeCycle = field(default_factory=lambda: LifeCycle(citizen_id=""))
    
    # NEW: Finances helper
    finances: Finances = field(default_factory=Finances)
    
    # Current state
    current_location: Optional[str] = None
    current_action: Optional[str] = None
    
    # History for explainability
    action_history: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize after creation."""
        # Link components to citizen ID
        self.memory = MemorySystem(owner_id=self.id)
        self.relationships = RelationshipManager(owner_id=self.id)
        self.life_events = LifeEventManager(citizen_id=self.id)
        self.lifecycle = LifeCycle(citizen_id=self.id, current_age=self.age)
        
        # Initialize emotions from personality
        self.emotions.set_baseline_from_personality(self.traits.to_dict())
    
    def decide(self, local_state: dict) -> Optional[Any]:
        """
        Make a decision based on local state.
        
        The decision is bounded and enumerable - agents choose
        among a small, valid set of actions.
        
        Args:
            local_state: The local world state visible to this agent
            
        Returns:
            An action to propose, or None to do nothing
        """
        # Update needs based on current state
        self.needs.update()
        
        # Update emotions (decay over time)
        self.emotions.update()
        
        # Get available actions
        available_actions = self._get_available_actions(local_state)
        
        if not available_actions:
            return None
        
        # Use decision model to select action
        # Emotions can modify decision weights
        emotion_modifier = self.emotions.get_decision_modifier()
        selected_action = self.decision_model.select_action(
            self,
            local_state,
            available_actions
        )
        
        return selected_action
    
    def _get_available_actions(self, local_state: dict) -> List[Any]:
        """Get the list of currently available actions."""
        from urbanium.actions import get_available_actions
        return get_available_actions(self, local_state)
    
    def receive_action_result(self, result: dict) -> None:
        """
        Process the result of an executed action.
        
        Args:
            result: The result from the world after action execution
        """
        # Record in history
        self.action_history.append({
            "action": self.current_action,
            "result": result,
        })
        
        # Update state based on result
        if result.get("success"):
            # Apply any resource changes
            if "money_change" in result:
                if result["money_change"] > 0:
                    self.resources.earn(result["money_change"])
                    self.finances.cash += result["money_change"]
                else:
                    self.resources.spend(abs(result["money_change"]))
                    self.finances.cash -= abs(result["money_change"])
            
            if "energy_change" in result:
                if result["energy_change"] > 0:
                    self.resources.restore_energy(result["energy_change"])
                else:
                    self.resources.consume_energy(abs(result["energy_change"]))
            
            # Update needs satisfaction
            if "needs_satisfied" in result:
                for need_type, amount in result["needs_satisfied"].items():
                    self.needs.satisfy(need_type, amount)
            
            # NEW: Create memory of action
            action_name = self.current_action if self.current_action else "unknown"
            self.memory.remember_event(
                f"Did action: {action_name}",
                tags=[action_name],
                emotional_valence=0.1 if result.get("success") else -0.1,
            )
            
            # NEW: Update emotions based on result
            if result.get("success"):
                from urbanium.agents.emotions import EmotionType
                self.emotions.feel(EmotionType.JOY, 0.1)
            else:
                from urbanium.agents.emotions import EmotionType
                self.emotions.feel(EmotionType.SADNESS, 0.1)
    
    def get_state(self) -> dict:
        """Get the current state of the citizen for inspection."""
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "life_stage": self.lifecycle.life_stage.value,
            "location": self.current_location,
            "resources": {
                "money": self.resources.money,
                "energy": self.resources.energy,
                "health": self.resources.health,
            },
            "finances": {
                "cash": self.finances.cash,
                "savings": self.finances.savings,
            },
            "needs": self.needs.get_all(),
            "roles": {
                "job_id": self.roles.job_id,
                "home_id": self.roles.home_id,
                "spouse_id": self.roles.spouse_id,
            },
            "emotions": self.emotions.get_summary(),
            "relationships": self.relationships.get_summary(),
            "memory_count": len(self.memory.memories),
            "is_alive": self.lifecycle.is_alive,
        }
    
    @property
    def is_employed(self) -> bool:
        """Check if the citizen is employed."""
        return self.roles.job_id is not None
    
    @property
    def has_home(self) -> bool:
        """Check if the citizen has a home."""
        return self.roles.home_id is not None
    
    @property
    def is_married(self) -> bool:
        """Check if the citizen is married."""
        return self.roles.spouse_id is not None
    
    @property
    def is_alive(self) -> bool:
        """Check if the citizen is alive."""
        return self.lifecycle.is_alive
    
    def age_by(self, years: float) -> List[str]:
        """Age the citizen by a number of years."""
        events = self.lifecycle.age_by(years)
        self.age = self.lifecycle.current_age
        
        # Update lifecycle stats
        if events:
            for event in events:
                if event.startswith("birthday"):
                    self.life_events.record_birthday(int(self.age))
        
        return events
    
    def meet(self, other_id: str, other_name: str) -> None:
        """Meet another citizen for the first time."""
        rel = self.relationships.get_or_create(other_id, other_name)
        
        if rel.interaction_count == 0:
            # First meeting
            self.life_events.record_first_meeting(other_id, other_name)
            self.memory.remember_event(
                f"Met {other_name} for the first time",
                tags=["meeting", other_id],
                emotional_valence=0.2,
            )
    
    def interact_with(
        self,
        other_id: str,
        other_name: str,
        positive: bool = True,
        description: str = "",
    ) -> None:
        """Record an interaction with another citizen."""
        from urbanium.agents.relationships import InteractionOutcome
        
        outcome = InteractionOutcome.POSITIVE if positive else InteractionOutcome.NEGATIVE
        self.relationships.interact_with(other_id, other_name, outcome, description)
        
        # Create memory
        sentiment = "good" if positive else "bad"
        self.memory.remember_event(
            f"Had a {sentiment} interaction with {other_name}: {description}",
            tags=["interaction", other_id],
            emotional_valence=0.3 if positive else -0.3,
        )
    
    def __repr__(self) -> str:
        return f"Citizen(id={self.id[:8]}..., name={self.name}, age={self.age:.1f})"
