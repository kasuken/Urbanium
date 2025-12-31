"""
Relationship System - How citizens connect with each other.

Citizens form relationships that:
- Have types (acquaintance, friend, romantic, family)
- Have strength that grows/decays
- Track trust, intimacy, and shared history
- Influence decisions and emotions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
import random


class RelationshipType(Enum):
    """Types of relationships between citizens."""
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    COLLEAGUE = "colleague"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    BEST_FRIEND = "best_friend"
    ROMANTIC_INTEREST = "romantic_interest"
    DATING = "dating"
    PARTNER = "partner"
    SPOUSE = "spouse"
    EX_PARTNER = "ex_partner"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    EXTENDED_FAMILY = "extended_family"
    RIVAL = "rival"
    ENEMY = "enemy"


class InteractionOutcome(Enum):
    """Outcomes of interactions."""
    POSITIVE = auto()
    NEUTRAL = auto()
    NEGATIVE = auto()
    CONFLICT = auto()
    BONDING = auto()
    ROMANTIC = auto()


@dataclass
class RelationshipEvent:
    """A significant event in a relationship."""
    
    event_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    emotional_impact: float = 0.0  # -1 to 1
    
    def __repr__(self) -> str:
        return f"{self.event_type}: {self.description}"


@dataclass
class Relationship:
    """
    A relationship between two citizens.
    
    Attributes:
        other_id: ID of the other person
        other_name: Name of the other person
        relationship_type: Type of relationship
        strength: How strong the bond is (0-1)
        trust: How much they trust each other (0-1)
        intimacy: Emotional closeness (0-1)
        attraction: Romantic/physical attraction (0-1)
        respect: Professional/personal respect (0-1)
        familiarity: How well they know each other (0-1)
        started: When the relationship began
        last_interaction: Last time they interacted
        history: Significant events in the relationship
    """
    
    other_id: str
    other_name: str
    
    # Relationship type
    relationship_type: RelationshipType = RelationshipType.STRANGER
    
    # Core metrics (all 0-1)
    strength: float = 0.0
    trust: float = 0.5
    intimacy: float = 0.0
    attraction: float = 0.0
    respect: float = 0.5
    familiarity: float = 0.0
    
    # Tracking
    started: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    positive_interactions: int = 0
    negative_interactions: int = 0
    
    # History
    history: List[RelationshipEvent] = field(default_factory=list)
    max_history: int = 50
    
    # Flags
    is_mutual: bool = True  # Do they know each other?
    is_active: bool = True  # Is this relationship active?
    
    def interact(self, outcome: InteractionOutcome, description: str = "") -> None:
        """
        Record an interaction.
        
        Args:
            outcome: How the interaction went
            description: What happened
        """
        self.interaction_count += 1
        self.last_interaction = datetime.now()
        self.familiarity = min(1.0, self.familiarity + 0.02)
        
        # Update based on outcome
        if outcome == InteractionOutcome.POSITIVE:
            self.positive_interactions += 1
            self.strength = min(1.0, self.strength + 0.05)
            self.trust = min(1.0, self.trust + 0.02)
            self._add_event("positive_interaction", description, 0.3)
            
        elif outcome == InteractionOutcome.NEGATIVE:
            self.negative_interactions += 1
            self.strength = max(0.0, self.strength - 0.08)
            self.trust = max(0.0, self.trust - 0.05)
            self._add_event("negative_interaction", description, -0.4)
            
        elif outcome == InteractionOutcome.CONFLICT:
            self.negative_interactions += 1
            self.strength = max(0.0, self.strength - 0.15)
            self.trust = max(0.0, self.trust - 0.1)
            self.respect = max(0.0, self.respect - 0.05)
            self._add_event("conflict", description, -0.6)
            
        elif outcome == InteractionOutcome.BONDING:
            self.positive_interactions += 1
            self.strength = min(1.0, self.strength + 0.1)
            self.intimacy = min(1.0, self.intimacy + 0.05)
            self.trust = min(1.0, self.trust + 0.05)
            self._add_event("bonding", description, 0.5)
            
        elif outcome == InteractionOutcome.ROMANTIC:
            self.positive_interactions += 1
            self.intimacy = min(1.0, self.intimacy + 0.08)
            self.attraction = min(1.0, self.attraction + 0.1)
            self.strength = min(1.0, self.strength + 0.08)
            self._add_event("romantic", description, 0.6)
            
        else:  # NEUTRAL
            self.familiarity = min(1.0, self.familiarity + 0.01)
        
        # Update relationship type based on metrics
        self._update_type()
    
    def _add_event(self, event_type: str, description: str, impact: float) -> None:
        """Add an event to history."""
        event = RelationshipEvent(
            event_type=event_type,
            description=description,
            emotional_impact=impact,
        )
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _update_type(self) -> None:
        """Update relationship type based on current metrics."""
        # Don't change family relationships
        if self.relationship_type in (
            RelationshipType.PARENT,
            RelationshipType.CHILD,
            RelationshipType.SIBLING,
            RelationshipType.EXTENDED_FAMILY,
        ):
            return
        
        # Romantic path
        if self.relationship_type == RelationshipType.SPOUSE:
            if self.strength < 0.2 and self.trust < 0.2:
                # Divorce path - handled by life events
                pass
            return
        
        if self.relationship_type == RelationshipType.PARTNER:
            # Can become spouse through proposal (life event)
            if self.strength < 0.3:
                self.relationship_type = RelationshipType.DATING
            return
        
        if self.relationship_type == RelationshipType.DATING:
            if self.strength > 0.7 and self.intimacy > 0.6 and self.trust > 0.6:
                self.relationship_type = RelationshipType.PARTNER
            elif self.strength < 0.2:
                self.relationship_type = RelationshipType.EX_PARTNER
            return
        
        if self.relationship_type == RelationshipType.ROMANTIC_INTEREST:
            if self.attraction > 0.5 and self.strength > 0.4:
                self.relationship_type = RelationshipType.DATING
            elif self.attraction < 0.2:
                self.relationship_type = RelationshipType.FRIEND if self.strength > 0.4 else RelationshipType.ACQUAINTANCE
            return
        
        # Friendship path
        if self.attraction > 0.4 and self.intimacy > 0.3:
            self.relationship_type = RelationshipType.ROMANTIC_INTEREST
        elif self.strength > 0.8 and self.trust > 0.7 and self.intimacy > 0.6:
            self.relationship_type = RelationshipType.BEST_FRIEND
        elif self.strength > 0.6 and self.trust > 0.5:
            self.relationship_type = RelationshipType.CLOSE_FRIEND
        elif self.strength > 0.3 and self.familiarity > 0.3:
            self.relationship_type = RelationshipType.FRIEND
        elif self.familiarity > 0.1:
            self.relationship_type = RelationshipType.ACQUAINTANCE
        
        # Negative relationships
        if self.trust < 0.1 and self.negative_interactions > self.positive_interactions * 2:
            if self.strength < 0.1:
                self.relationship_type = RelationshipType.ENEMY
            else:
                self.relationship_type = RelationshipType.RIVAL
    
    def decay(self, days: float) -> None:
        """Apply time-based decay to relationship."""
        # Relationships decay without interaction
        days_since = (datetime.now() - self.last_interaction).days
        
        if days_since > 30:
            decay_rate = 0.01 * (days_since / 30)
            self.strength = max(0.0, self.strength - decay_rate * days)
            self.intimacy = max(0.0, self.intimacy - decay_rate * 0.5 * days)
        
        # Family relationships decay slower
        if self.relationship_type in (
            RelationshipType.PARENT,
            RelationshipType.CHILD,
            RelationshipType.SIBLING,
            RelationshipType.SPOUSE,
        ):
            return
        
        # Update type after decay
        self._update_type()
    
    def set_family(self, relationship_type: RelationshipType) -> None:
        """Set as a family relationship."""
        if relationship_type in (
            RelationshipType.PARENT,
            RelationshipType.CHILD,
            RelationshipType.SIBLING,
            RelationshipType.EXTENDED_FAMILY,
        ):
            self.relationship_type = relationship_type
            self.trust = 0.7
            self.intimacy = 0.5
            self.familiarity = 1.0
            self.strength = 0.6
    
    def marry(self) -> None:
        """Convert to marriage."""
        self.relationship_type = RelationshipType.SPOUSE
        self.trust = max(self.trust, 0.7)
        self.intimacy = max(self.intimacy, 0.7)
        self.strength = max(self.strength, 0.8)
        self._add_event("marriage", "Got married", 1.0)
    
    def divorce(self) -> None:
        """End marriage."""
        self.relationship_type = RelationshipType.EX_PARTNER
        self.trust = min(self.trust, 0.3)
        self.intimacy = min(self.intimacy, 0.2)
        self._add_event("divorce", "Got divorced", -0.8)
    
    @property
    def is_romantic(self) -> bool:
        """Check if this is a romantic relationship."""
        return self.relationship_type in (
            RelationshipType.ROMANTIC_INTEREST,
            RelationshipType.DATING,
            RelationshipType.PARTNER,
            RelationshipType.SPOUSE,
        )
    
    @property
    def is_family(self) -> bool:
        """Check if this is a family relationship."""
        return self.relationship_type in (
            RelationshipType.PARENT,
            RelationshipType.CHILD,
            RelationshipType.SIBLING,
            RelationshipType.EXTENDED_FAMILY,
            RelationshipType.SPOUSE,  # Spouse is also family
        )
    
    @property
    def is_friend(self) -> bool:
        """Check if this is a friendship."""
        return self.relationship_type in (
            RelationshipType.FRIEND,
            RelationshipType.CLOSE_FRIEND,
            RelationshipType.BEST_FRIEND,
        )
    
    @property
    def sentiment(self) -> float:
        """Get overall sentiment toward this person (-1 to 1)."""
        base = (self.trust - 0.5) * 0.3 + (self.strength - 0.5) * 0.4
        
        if self.interaction_count > 0:
            ratio = self.positive_interactions / self.interaction_count
            base += (ratio - 0.5) * 0.3
        
        return max(-1.0, min(1.0, base))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of relationship."""
        return {
            "other_id": self.other_id,
            "other_name": self.other_name,
            "type": self.relationship_type.value,
            "strength": self.strength,
            "trust": self.trust,
            "intimacy": self.intimacy,
            "attraction": self.attraction,
            "sentiment": self.sentiment,
            "interactions": self.interaction_count,
            "is_romantic": self.is_romantic,
            "is_family": self.is_family,
        }


@dataclass
class RelationshipManager:
    """
    Manages all relationships for a citizen.
    """
    
    owner_id: str
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    
    def get_or_create(self, other_id: str, other_name: str = "Unknown") -> Relationship:
        """Get existing relationship or create new one."""
        if other_id not in self.relationships:
            self.relationships[other_id] = Relationship(
                other_id=other_id,
                other_name=other_name,
            )
        return self.relationships[other_id]
    
    def get(self, other_id: str) -> Optional[Relationship]:
        """Get relationship if it exists."""
        return self.relationships.get(other_id)
    
    def interact_with(
        self,
        other_id: str,
        other_name: str,
        outcome: InteractionOutcome,
        description: str = "",
    ) -> Relationship:
        """
        Record an interaction with another person.
        
        Args:
            other_id: ID of the other person
            other_name: Name of the other person
            outcome: How the interaction went
            description: What happened
            
        Returns:
            The updated Relationship
        """
        rel = self.get_or_create(other_id, other_name)
        rel.interact(outcome, description)
        return rel
    
    def add_family_member(
        self,
        other_id: str,
        other_name: str,
        relationship_type: RelationshipType,
    ) -> Relationship:
        """Add a family relationship."""
        rel = self.get_or_create(other_id, other_name)
        rel.set_family(relationship_type)
        return rel
    
    def get_family(self) -> List[Relationship]:
        """Get all family relationships."""
        return [r for r in self.relationships.values() if r.is_family]
    
    def get_friends(self) -> List[Relationship]:
        """Get all friendships."""
        return [r for r in self.relationships.values() if r.is_friend]
    
    def get_romantic_partner(self) -> Optional[Relationship]:
        """Get current romantic partner (if any)."""
        for rel in self.relationships.values():
            if rel.relationship_type in (
                RelationshipType.DATING,
                RelationshipType.PARTNER,
                RelationshipType.SPOUSE,
            ):
                return rel
        return None
    
    def get_spouse(self) -> Optional[Relationship]:
        """Get spouse (if married)."""
        for rel in self.relationships.values():
            if rel.relationship_type == RelationshipType.SPOUSE:
                return rel
        return None
    
    def get_children(self) -> List[Relationship]:
        """Get all children."""
        return [
            r for r in self.relationships.values()
            if r.relationship_type == RelationshipType.CHILD
        ]
    
    def get_parents(self) -> List[Relationship]:
        """Get parents."""
        return [
            r for r in self.relationships.values()
            if r.relationship_type == RelationshipType.PARENT
        ]
    
    def get_by_type(self, rel_type: RelationshipType) -> List[Relationship]:
        """Get all relationships of a specific type."""
        return [r for r in self.relationships.values() if r.relationship_type == rel_type]
    
    def get_closest(self, count: int = 5) -> List[Relationship]:
        """Get the closest relationships."""
        sorted_rels = sorted(
            self.relationships.values(),
            key=lambda r: r.strength * r.intimacy,
            reverse=True,
        )
        return sorted_rels[:count]
    
    def knows(self, other_id: str) -> bool:
        """Check if this person knows another."""
        if other_id not in self.relationships:
            return False
        return self.relationships[other_id].familiarity > 0.1
    
    def get_sentiment_toward(self, other_id: str) -> float:
        """Get sentiment toward another person."""
        rel = self.get(other_id)
        if rel is None:
            return 0.0
        return rel.sentiment
    
    def update(self, days: float = 1.0) -> None:
        """Update all relationships (apply decay)."""
        for rel in self.relationships.values():
            rel.decay(days)
    
    def get_social_circle_size(self) -> int:
        """Get size of social circle (non-stranger relationships)."""
        return len([
            r for r in self.relationships.values()
            if r.relationship_type != RelationshipType.STRANGER
            and r.strength > 0.1
        ])
    
    def calculate_compatibility(
        self,
        other_traits: Dict[str, float],
        own_traits: Dict[str, float],
    ) -> float:
        """
        Calculate compatibility with another person based on traits.
        
        Args:
            other_traits: Their personality traits
            own_traits: Own personality traits
            
        Returns:
            Compatibility score (0-1)
        """
        # Similarity in some traits, complementarity in others
        similarity_traits = ["openness", "conscientiousness"]
        complement_traits = ["extraversion"]
        
        score = 0.5
        
        for trait in similarity_traits:
            if trait in other_traits and trait in own_traits:
                diff = abs(other_traits[trait] - own_traits[trait])
                score += (1 - diff) * 0.1
        
        for trait in complement_traits:
            if trait in other_traits and trait in own_traits:
                # Some difference is good
                diff = abs(other_traits[trait] - own_traits[trait])
                score += (0.5 - abs(diff - 0.3)) * 0.1
        
        return max(0.0, min(1.0, score))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all relationships."""
        return {
            "total": len(self.relationships),
            "friends": len(self.get_friends()),
            "family": len(self.get_family()),
            "has_partner": self.get_romantic_partner() is not None,
            "is_married": self.get_spouse() is not None,
            "children": len(self.get_children()),
            "social_circle_size": self.get_social_circle_size(),
            "closest": [r.get_summary() for r in self.get_closest(3)],
        }
