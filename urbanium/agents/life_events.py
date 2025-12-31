"""
Life Events System - Major life transitions and events.

Citizens experience life events that:
- Change their relationships (marriage, divorce, having children)
- Change their living situation (moving, household changes)
- Change their career (job changes, promotions, retirement)
- Mark significant moments (birthdays, achievements, losses)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .citizen import Citizen


class LifeEventType(Enum):
    """Types of life events."""
    # Relationships
    FIRST_MEETING = "first_meeting"
    START_DATING = "start_dating"
    BREAK_UP = "break_up"
    ENGAGEMENT = "engagement"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    
    # Family
    PREGNANCY = "pregnancy"
    BIRTH = "birth"
    CHILD_GROWS_UP = "child_grows_up"
    CHILD_MOVES_OUT = "child_moves_out"
    
    # Career
    JOB_OFFER = "job_offer"
    JOB_START = "job_start"
    JOB_LOSS = "job_loss"
    PROMOTION = "promotion"
    RETIREMENT = "retirement"
    
    # Life transitions
    BIRTHDAY = "birthday"
    MOVE_HOME = "move_home"
    BUY_PROPERTY = "buy_property"
    
    # Loss
    DEATH = "death"
    FUNERAL = "funeral"
    INHERITANCE = "inheritance"
    
    # Social
    MADE_FRIEND = "made_friend"
    LOST_FRIEND = "lost_friend"
    CONFLICT = "conflict"
    RECONCILIATION = "reconciliation"
    
    # Achievements
    GRADUATION = "graduation"
    SKILL_MASTERY = "skill_mastery"
    WEALTH_MILESTONE = "wealth_milestone"


@dataclass
class LifeEvent:
    """
    A significant life event.
    
    Attributes:
        event_type: Type of the event
        timestamp: When it happened
        description: Human-readable description
        participants: IDs of people involved
        location: Where it happened
        emotional_impact: How emotionally significant (-1 to 1)
        data: Additional event-specific data
    """
    
    event_type: LifeEventType
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    participants: List[str] = field(default_factory=list)
    location: Optional[str] = None
    emotional_impact: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"LifeEvent({self.event_type.value}: {self.description})"


class LifeEventTrigger:
    """
    Evaluates conditions for triggering life events.
    """
    
    @staticmethod
    def check_dating_potential(
        citizen1_id: str,
        citizen2_id: str,
        relationship_data: Dict[str, Any],
    ) -> bool:
        """Check if two people might start dating."""
        # Both must be attracted and have some strength
        attraction = relationship_data.get("attraction", 0)
        strength = relationship_data.get("strength", 0)
        
        if attraction > 0.4 and strength > 0.3:
            # Chance based on compatibility
            chance = (attraction + strength) / 4
            return random.random() < chance
        return False
    
    @staticmethod
    def check_engagement_ready(relationship_data: Dict[str, Any]) -> bool:
        """Check if a couple might get engaged."""
        # Need strong relationship
        strength = relationship_data.get("strength", 0)
        trust = relationship_data.get("trust", 0)
        intimacy = relationship_data.get("intimacy", 0)
        
        if strength > 0.75 and trust > 0.7 and intimacy > 0.65:
            # Duration matters too
            interaction_count = relationship_data.get("interaction_count", 0)
            if interaction_count > 30:
                return random.random() < 0.1  # 10% chance per check
        return False
    
    @staticmethod
    def check_pregnancy_chance(
        couple_data: Dict[str, Any],
        age: float,
    ) -> bool:
        """Check if a pregnancy might occur."""
        # Must be in committed relationship
        if couple_data.get("relationship_type") not in ("partner", "spouse"):
            return False
        
        # Age affects fertility
        if age < 18 or age > 45:
            return False
        
        fertility = 1.0 - abs(age - 28) / 30  # Peak at 28
        fertility = max(0.1, min(1.0, fertility))
        
        # Chance per check
        base_chance = 0.02 * fertility
        return random.random() < base_chance
    
    @staticmethod
    def check_breakup_risk(relationship_data: Dict[str, Any]) -> bool:
        """Check if a couple might break up."""
        trust = relationship_data.get("trust", 0.5)
        strength = relationship_data.get("strength", 0.5)
        
        if trust < 0.3 or strength < 0.2:
            risk = (1 - trust) * (1 - strength)
            return random.random() < risk * 0.1
        return False
    
    @staticmethod
    def check_divorce_risk(relationship_data: Dict[str, Any]) -> bool:
        """Check if a marriage might end in divorce."""
        trust = relationship_data.get("trust", 0.5)
        strength = relationship_data.get("strength", 0.5)
        
        # Divorce is harder than breakup
        if trust < 0.2 and strength < 0.2:
            risk = (1 - trust) * (1 - strength)
            return random.random() < risk * 0.05
        return False


@dataclass
class LifeEventManager:
    """
    Manages life events for a citizen.
    """
    
    citizen_id: str
    event_history: List[LifeEvent] = field(default_factory=list)
    pending_events: List[LifeEvent] = field(default_factory=list)
    event_callbacks: Dict[LifeEventType, List[Callable]] = field(default_factory=dict)
    
    max_history: int = 200
    
    def add_event(self, event: LifeEvent) -> None:
        """
        Record a life event.
        
        Args:
            event: The event that occurred
        """
        self.event_history.append(event)
        
        # Trim history if needed
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Trigger callbacks
        self._trigger_callbacks(event)
    
    def create_event(
        self,
        event_type: LifeEventType,
        description: str,
        participants: Optional[List[str]] = None,
        location: Optional[str] = None,
        emotional_impact: float = 0.0,
        data: Optional[Dict[str, Any]] = None,
    ) -> LifeEvent:
        """Create and record a life event."""
        event = LifeEvent(
            event_type=event_type,
            description=description,
            participants=participants or [],
            location=location,
            emotional_impact=emotional_impact,
            data=data or {},
        )
        self.add_event(event)
        return event
    
    def _trigger_callbacks(self, event: LifeEvent) -> None:
        """Trigger registered callbacks for an event type."""
        callbacks = self.event_callbacks.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception:
                pass  # Don't let callback errors break the system
    
    def register_callback(
        self,
        event_type: LifeEventType,
        callback: Callable[[LifeEvent], None],
    ) -> None:
        """Register a callback for a specific event type."""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    # ===== Event Creation Helpers =====
    
    def record_first_meeting(
        self,
        other_id: str,
        other_name: str,
        location: Optional[str] = None,
    ) -> LifeEvent:
        """Record meeting someone for the first time."""
        return self.create_event(
            event_type=LifeEventType.FIRST_MEETING,
            description=f"Met {other_name}",
            participants=[other_id],
            location=location,
            emotional_impact=0.1,
        )
    
    def record_start_dating(
        self,
        partner_id: str,
        partner_name: str,
    ) -> LifeEvent:
        """Record starting a romantic relationship."""
        return self.create_event(
            event_type=LifeEventType.START_DATING,
            description=f"Started dating {partner_name}",
            participants=[partner_id],
            emotional_impact=0.7,
        )
    
    def record_breakup(
        self,
        ex_id: str,
        ex_name: str,
        reason: str = "",
    ) -> LifeEvent:
        """Record a breakup."""
        desc = f"Broke up with {ex_name}"
        if reason:
            desc += f" ({reason})"
        return self.create_event(
            event_type=LifeEventType.BREAK_UP,
            description=desc,
            participants=[ex_id],
            emotional_impact=-0.6,
            data={"reason": reason},
        )
    
    def record_engagement(
        self,
        partner_id: str,
        partner_name: str,
    ) -> LifeEvent:
        """Record getting engaged."""
        return self.create_event(
            event_type=LifeEventType.ENGAGEMENT,
            description=f"Got engaged to {partner_name}",
            participants=[partner_id],
            emotional_impact=0.9,
        )
    
    def record_marriage(
        self,
        spouse_id: str,
        spouse_name: str,
        location: Optional[str] = None,
    ) -> LifeEvent:
        """Record getting married."""
        return self.create_event(
            event_type=LifeEventType.MARRIAGE,
            description=f"Married {spouse_name}",
            participants=[spouse_id],
            location=location,
            emotional_impact=1.0,
        )
    
    def record_divorce(
        self,
        ex_spouse_id: str,
        ex_spouse_name: str,
    ) -> LifeEvent:
        """Record divorce."""
        return self.create_event(
            event_type=LifeEventType.DIVORCE,
            description=f"Divorced {ex_spouse_name}",
            participants=[ex_spouse_id],
            emotional_impact=-0.8,
        )
    
    def record_pregnancy(self, partner_id: str, partner_name: str) -> LifeEvent:
        """Record pregnancy."""
        return self.create_event(
            event_type=LifeEventType.PREGNANCY,
            description=f"Expecting a child with {partner_name}",
            participants=[partner_id],
            emotional_impact=0.8,
        )
    
    def record_birth(
        self,
        child_id: str,
        child_name: str,
        partner_id: Optional[str] = None,
    ) -> LifeEvent:
        """Record birth of a child."""
        participants = [child_id]
        if partner_id:
            participants.append(partner_id)
        return self.create_event(
            event_type=LifeEventType.BIRTH,
            description=f"Welcomed {child_name} into the world",
            participants=participants,
            emotional_impact=1.0,
            data={"child_name": child_name},
        )
    
    def record_job_start(
        self,
        company: str,
        position: str,
        salary: float,
    ) -> LifeEvent:
        """Record starting a new job."""
        return self.create_event(
            event_type=LifeEventType.JOB_START,
            description=f"Started as {position} at {company}",
            emotional_impact=0.5,
            data={
                "company": company,
                "position": position,
                "salary": salary,
            },
        )
    
    def record_job_loss(self, company: str, reason: str = "") -> LifeEvent:
        """Record losing a job."""
        desc = f"Left job at {company}"
        if reason:
            desc += f" ({reason})"
        return self.create_event(
            event_type=LifeEventType.JOB_LOSS,
            description=desc,
            emotional_impact=-0.6,
            data={"company": company, "reason": reason},
        )
    
    def record_promotion(
        self,
        new_position: str,
        salary_increase: float,
    ) -> LifeEvent:
        """Record a promotion."""
        return self.create_event(
            event_type=LifeEventType.PROMOTION,
            description=f"Promoted to {new_position}",
            emotional_impact=0.6,
            data={
                "new_position": new_position,
                "salary_increase": salary_increase,
            },
        )
    
    def record_move(
        self,
        new_location: str,
        old_location: Optional[str] = None,
    ) -> LifeEvent:
        """Record moving to a new home."""
        desc = f"Moved to {new_location}"
        if old_location:
            desc = f"Moved from {old_location} to {new_location}"
        return self.create_event(
            event_type=LifeEventType.MOVE_HOME,
            description=desc,
            location=new_location,
            emotional_impact=0.3,
            data={"old_location": old_location, "new_location": new_location},
        )
    
    def record_birthday(self, new_age: int) -> LifeEvent:
        """Record a birthday."""
        return self.create_event(
            event_type=LifeEventType.BIRTHDAY,
            description=f"Turned {new_age}",
            emotional_impact=0.4,
            data={"new_age": new_age},
        )
    
    def record_death(
        self,
        deceased_id: str,
        deceased_name: str,
        relationship: str,
    ) -> LifeEvent:
        """Record death of someone known."""
        return self.create_event(
            event_type=LifeEventType.DEATH,
            description=f"{relationship} {deceased_name} passed away",
            participants=[deceased_id],
            emotional_impact=-0.9,
            data={"relationship": relationship},
        )
    
    def record_made_friend(
        self,
        friend_id: str,
        friend_name: str,
    ) -> LifeEvent:
        """Record making a new friend."""
        return self.create_event(
            event_type=LifeEventType.MADE_FRIEND,
            description=f"Became friends with {friend_name}",
            participants=[friend_id],
            emotional_impact=0.4,
        )
    
    # ===== Query Methods =====
    
    def get_events_by_type(
        self,
        event_type: LifeEventType,
    ) -> List[LifeEvent]:
        """Get all events of a specific type."""
        return [e for e in self.event_history if e.event_type == event_type]
    
    def get_events_involving(self, person_id: str) -> List[LifeEvent]:
        """Get all events involving a specific person."""
        return [e for e in self.event_history if person_id in e.participants]
    
    def get_recent_events(self, count: int = 10) -> List[LifeEvent]:
        """Get most recent events."""
        return self.event_history[-count:] if self.event_history else []
    
    def get_significant_events(
        self,
        threshold: float = 0.5,
    ) -> List[LifeEvent]:
        """Get emotionally significant events."""
        return [
            e for e in self.event_history
            if abs(e.emotional_impact) >= threshold
        ]
    
    def get_positive_events(self) -> List[LifeEvent]:
        """Get positive events."""
        return [e for e in self.event_history if e.emotional_impact > 0.3]
    
    def get_negative_events(self) -> List[LifeEvent]:
        """Get negative events."""
        return [e for e in self.event_history if e.emotional_impact < -0.3]
    
    def count_events_by_type(self) -> Dict[str, int]:
        """Count events by type."""
        counts: Dict[str, int] = {}
        for event in self.event_history:
            type_name = event.event_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def get_life_summary(self) -> Dict[str, Any]:
        """Get a summary of life events."""
        return {
            "total_events": len(self.event_history),
            "positive_events": len(self.get_positive_events()),
            "negative_events": len(self.get_negative_events()),
            "marriages": len(self.get_events_by_type(LifeEventType.MARRIAGE)),
            "divorces": len(self.get_events_by_type(LifeEventType.DIVORCE)),
            "children": len(self.get_events_by_type(LifeEventType.BIRTH)),
            "jobs_held": len(self.get_events_by_type(LifeEventType.JOB_START)),
            "promotions": len(self.get_events_by_type(LifeEventType.PROMOTION)),
            "moves": len(self.get_events_by_type(LifeEventType.MOVE_HOME)),
        }
