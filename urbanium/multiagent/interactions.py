"""
Inter-agent interactions.

Defines how agents can interact with each other autonomously.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
import logging
import random

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of interactions between agents."""
    
    # Social
    CONVERSATION = auto()      # Casual chat
    GREETING = auto()          # Simple greeting
    FRIENDSHIP = auto()        # Building friendship
    CONFLICT = auto()          # Disagreement/argument
    
    # Economic
    TRADE = auto()             # Exchange goods/money
    EMPLOYMENT = auto()        # Job offer/hiring
    SERVICE = auto()           # Provide/request service
    
    # Information
    SHARE_KNOWLEDGE = auto()   # Share information
    ASK_DIRECTION = auto()     # Ask for directions
    GOSSIP = auto()            # Share rumors
    
    # Cooperative
    HELP = auto()              # Offer/request help
    COLLABORATION = auto()     # Work together
    MENTORING = auto()         # Teach/learn


@dataclass
class Interaction:
    """
    A record of an interaction between agents.
    
    Attributes:
        id: Unique interaction identifier
        type: Type of interaction
        initiator_id: Agent who started the interaction
        participant_ids: All agents involved
        start_time: When interaction began
        end_time: When interaction ended
        outcome: Result of the interaction
        effects: Changes caused by the interaction
    """
    
    type: InteractionType
    initiator_id: str
    participant_ids: List[str]
    
    id: str = field(default_factory=lambda: f"int_{random.randint(100000, 999999)}")
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    outcome: str = "pending"
    effects: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, outcome: str, effects: Optional[Dict] = None):
        """Mark interaction as complete."""
        self.end_time = datetime.now()
        self.outcome = outcome
        if effects:
            self.effects.update(effects)
    
    @property
    def duration_seconds(self) -> float:
        """Get duration of interaction in seconds."""
        if self.end_time is None:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def is_active(self) -> bool:
        """Check if interaction is still ongoing."""
        return self.end_time is None


class InteractionManager:
    """
    Manages interactions between agents.
    
    Handles:
    - Initiating interactions
    - Processing interaction outcomes
    - Applying effects to agents
    - Tracking interaction history
    """
    
    def __init__(self):
        """Initialize the interaction manager."""
        self._active_interactions: Dict[str, Interaction] = {}
        self._history: List[Interaction] = []
        self._max_history: int = 5000
        
        # Interaction cooldowns (agent_id -> last interaction time per type)
        self._cooldowns: Dict[str, Dict[InteractionType, datetime]] = {}
        
        # Statistics
        self.total_interactions: int = 0
        self.successful_interactions: int = 0
    
    def can_interact(
        self,
        agent_id: str,
        other_id: str,
        interaction_type: InteractionType,
        cooldown_seconds: float = 5.0,
    ) -> bool:
        """
        Check if an agent can initiate an interaction.
        
        Args:
            agent_id: The initiating agent
            other_id: The target agent
            interaction_type: Type of interaction
            cooldown_seconds: Minimum time between same-type interactions
            
        Returns:
            True if interaction is allowed
        """
        # Check if either agent is already in an interaction
        for interaction in self._active_interactions.values():
            if agent_id in interaction.participant_ids:
                return False
            if other_id in interaction.participant_ids:
                return False
        
        # Check cooldown
        if agent_id in self._cooldowns:
            last_time = self._cooldowns[agent_id].get(interaction_type)
            if last_time:
                elapsed = (datetime.now() - last_time).total_seconds()
                if elapsed < cooldown_seconds:
                    return False
        
        return True
    
    def start_interaction(
        self,
        interaction_type: InteractionType,
        initiator_id: str,
        participant_ids: List[str],
        context: Optional[Dict] = None,
    ) -> Interaction:
        """
        Start a new interaction.
        
        Args:
            interaction_type: Type of interaction
            initiator_id: Agent starting the interaction
            participant_ids: All agents involved (including initiator)
            context: Additional context
            
        Returns:
            The created Interaction
        """
        interaction = Interaction(
            type=interaction_type,
            initiator_id=initiator_id,
            participant_ids=participant_ids,
            context=context or {},
        )
        
        self._active_interactions[interaction.id] = interaction
        self.total_interactions += 1
        
        logger.debug(
            f"Interaction started: {interaction_type.name} between "
            f"{', '.join(participant_ids)}"
        )
        
        return interaction
    
    def complete_interaction(
        self,
        interaction_id: str,
        outcome: str,
        effects: Optional[Dict] = None,
    ) -> Optional[Interaction]:
        """
        Complete an interaction.
        
        Args:
            interaction_id: ID of the interaction
            outcome: Result of the interaction
            effects: Effects to apply
            
        Returns:
            The completed Interaction, or None if not found
        """
        interaction = self._active_interactions.pop(interaction_id, None)
        if interaction is None:
            logger.warning(f"Interaction {interaction_id} not found")
            return None
        
        interaction.complete(outcome, effects)
        
        # Update cooldowns
        for agent_id in interaction.participant_ids:
            if agent_id not in self._cooldowns:
                self._cooldowns[agent_id] = {}
            self._cooldowns[agent_id][interaction.type] = datetime.now()
        
        # Store in history
        self._history.append(interaction)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        if outcome in ("success", "positive", "completed"):
            self.successful_interactions += 1
        
        logger.debug(
            f"Interaction {interaction_id} completed: {outcome}"
        )
        
        return interaction
    
    def get_active_interactions(self, agent_id: Optional[str] = None) -> List[Interaction]:
        """Get active interactions, optionally filtered by agent."""
        if agent_id is None:
            return list(self._active_interactions.values())
        
        return [
            i for i in self._active_interactions.values()
            if agent_id in i.participant_ids
        ]
    
    def get_interaction_history(
        self,
        agent_id: Optional[str] = None,
        interaction_type: Optional[InteractionType] = None,
        limit: int = 100,
    ) -> List[Interaction]:
        """
        Get interaction history with optional filters.
        
        Args:
            agent_id: Filter by agent
            interaction_type: Filter by type
            limit: Maximum results
            
        Returns:
            List of matching interactions
        """
        results = self._history
        
        if agent_id:
            results = [i for i in results if agent_id in i.participant_ids]
        
        if interaction_type:
            results = [i for i in results if i.type == interaction_type]
        
        return results[-limit:]
    
    def get_relationship_score(
        self,
        agent_a: str,
        agent_b: str,
    ) -> float:
        """
        Calculate relationship score between two agents based on interactions.
        
        Returns:
            Score from -1 (hostile) to 1 (close friends)
        """
        interactions = [
            i for i in self._history
            if agent_a in i.participant_ids and agent_b in i.participant_ids
        ]
        
        if not interactions:
            return 0.0
        
        score = 0.0
        for interaction in interactions:
            if interaction.outcome in ("success", "positive", "completed"):
                score += 0.1
            elif interaction.outcome in ("failure", "negative", "conflict"):
                score -= 0.15
        
        return max(-1.0, min(1.0, score))
    
    def get_statistics(self) -> Dict:
        """Get interaction statistics."""
        return {
            "total_interactions": self.total_interactions,
            "successful_interactions": self.successful_interactions,
            "success_rate": (
                self.successful_interactions / self.total_interactions
                if self.total_interactions > 0 else 0
            ),
            "active_count": len(self._active_interactions),
            "history_size": len(self._history),
        }
