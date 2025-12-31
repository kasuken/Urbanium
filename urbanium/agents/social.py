"""
Social - Social network and relationships.

Citizens have social ties that influence their behavior
and provide social capital.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


class RelationshipType(Enum):
    """Types of social relationships."""
    FAMILY = "family"
    FRIEND = "friend"
    COLLEAGUE = "colleague"
    NEIGHBOR = "neighbor"
    ACQUAINTANCE = "acquaintance"


@dataclass
class SocialTie:
    """A social connection between two citizens."""
    target_id: str
    relationship_type: RelationshipType
    strength: float = 0.5  # 0-1
    trust: float = 0.5  # 0-1
    frequency: float = 0.0  # Interactions per time unit
    
    # History
    interaction_count: int = 0
    last_interaction_tick: Optional[int] = None
    
    def interact(self, current_tick: int) -> None:
        """Record an interaction."""
        self.interaction_count += 1
        self.last_interaction_tick = current_tick
        
        # Strengthen bond with interaction
        self.strength = min(1.0, self.strength + 0.01)
    
    def decay(self, amount: float = 0.001) -> None:
        """Apply decay to the relationship strength."""
        self.strength = max(0.0, self.strength - amount)


@dataclass
class SocialNetwork:
    """
    The social network of a citizen.
    
    Manages relationships and social capital.
    """
    
    ties: Dict[str, SocialTie] = field(default_factory=dict)
    
    def add_tie(self, tie: SocialTie) -> None:
        """Add a social tie."""
        self.ties[tie.target_id] = tie
    
    def remove_tie(self, target_id: str) -> None:
        """Remove a social tie."""
        if target_id in self.ties:
            del self.ties[target_id]
    
    def get_tie(self, target_id: str) -> Optional[SocialTie]:
        """Get a specific tie."""
        return self.ties.get(target_id)
    
    def has_tie(self, target_id: str) -> bool:
        """Check if a tie exists."""
        return target_id in self.ties
    
    def get_ties_by_type(self, relationship_type: RelationshipType) -> List[SocialTie]:
        """Get all ties of a specific type."""
        return [
            tie for tie in self.ties.values()
            if tie.relationship_type == relationship_type
        ]
    
    def get_strong_ties(self, threshold: float = 0.7) -> List[SocialTie]:
        """Get ties above a strength threshold."""
        return [
            tie for tie in self.ties.values()
            if tie.strength >= threshold
        ]
    
    def get_weak_ties(self, threshold: float = 0.3) -> List[SocialTie]:
        """Get ties below a strength threshold."""
        return [
            tie for tie in self.ties.values()
            if tie.strength < threshold
        ]
    
    def update(self) -> None:
        """Update all ties (apply decay)."""
        # Remove very weak ties
        to_remove = [
            target_id for target_id, tie in self.ties.items()
            if tie.strength <= 0.01
        ]
        for target_id in to_remove:
            del self.ties[target_id]
        
        # Decay remaining ties
        for tie in self.ties.values():
            tie.decay()
    
    @property
    def network_size(self) -> int:
        """Get the number of connections."""
        return len(self.ties)
    
    @property
    def average_tie_strength(self) -> float:
        """Get the average strength of all ties."""
        if not self.ties:
            return 0.0
        return sum(tie.strength for tie in self.ties.values()) / len(self.ties)
    
    def get_social_capital(self) -> float:
        """
        Calculate social capital based on network structure.
        
        Considers both network size and tie strength.
        """
        if not self.ties:
            return 0.0
        
        # Weighted sum of tie strengths
        total_capital = sum(
            tie.strength * self._get_type_weight(tie.relationship_type)
            for tie in self.ties.values()
        )
        
        return total_capital
    
    def _get_type_weight(self, relationship_type: RelationshipType) -> float:
        """Get the weight multiplier for a relationship type."""
        weights = {
            RelationshipType.FAMILY: 2.0,
            RelationshipType.FRIEND: 1.5,
            RelationshipType.COLLEAGUE: 1.0,
            RelationshipType.NEIGHBOR: 0.8,
            RelationshipType.ACQUAINTANCE: 0.5,
        }
        return weights.get(relationship_type, 1.0)
    
    def get_connection_ids(self) -> Set[str]:
        """Get all connected citizen IDs."""
        return set(self.ties.keys())
