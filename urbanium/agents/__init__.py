"""
Agents module - Citizen models and decision logic.

Citizens are structured agents, not chatbots. Each citizen has:
- Stable traits and values
- Skills and resources
- Needs that evolve over time
- Social ties
- Role bindings (job, home)
- A bounded decision model

Enhanced with:
- Memory system (episodic, semantic memories with decay)
- Emotional state (Plutchik's wheel + PAD model)
- Relationship management (types, strength, trust)
- Life events tracking (marriage, children, career)
- Life cycle with aging
"""

from urbanium.agents.citizen import Citizen
from urbanium.agents.traits import Traits, Values
from urbanium.agents.needs import Needs, NeedType
from urbanium.agents.skills import Skills
from urbanium.agents.social import SocialNetwork, SocialTie
from urbanium.agents.decision import DecisionModel

# New life simulation modules
from urbanium.agents.memory import Memory, MemorySystem, MemoryType
from urbanium.agents.emotions import (
    Emotion,
    EmotionType,
    Mood,
    EmotionalState,
)
from urbanium.agents.relationships import (
    Relationship,
    RelationshipType,
    RelationshipManager,
    InteractionOutcome,
)
from urbanium.agents.life_events import (
    LifeEvent,
    LifeEventType,
    LifeEventManager,
    LifeEventTrigger,
)
from urbanium.agents.lifecycle import (
    LifeCycle,
    LifeStage,
    Population,
    get_life_stage,
    get_aging_stats,
)
from urbanium.agents.household import (
    Household,
    HouseholdType,
    HouseholdMember,
    HouseholdManager,
    FamilyRole,
    FamilyTree,
)

__all__ = [
    # Core
    "Citizen",
    "Traits",
    "Values", 
    "Needs",
    "NeedType",
    "Skills",
    "SocialNetwork",
    "SocialTie",
    "DecisionModel",
    # Memory
    "Memory",
    "MemorySystem",
    "MemoryType",
    # Emotions
    "Emotion",
    "EmotionType",
    "Mood",
    "EmotionalState",
    # Relationships
    "Relationship",
    "RelationshipType",
    "RelationshipManager",
    "InteractionOutcome",
    # Life Events
    "LifeEvent",
    "LifeEventType",
    "LifeEventManager",
    "LifeEventTrigger",
    # Life Cycle
    "LifeCycle",
    "LifeStage",
    "Population",
    "get_life_stage",
    "get_aging_stats",
    # Household
    "Household",
    "HouseholdType",
    "HouseholdMember",
    "HouseholdManager",
    "FamilyRole",
    "FamilyTree",
]
