"""
Traits - Stable personality traits and values.

Traits are relatively stable characteristics that influence
decision-making and behavior patterns.
"""

from dataclasses import dataclass, field
from typing import Dict
from enum import Enum


class TraitType(Enum):
    """Core personality trait dimensions."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class ValueType(Enum):
    """Core value dimensions."""
    SECURITY = "security"
    ACHIEVEMENT = "achievement"
    HEDONISM = "hedonism"
    BENEVOLENCE = "benevolence"
    CONFORMITY = "conformity"
    SELF_DIRECTION = "self_direction"


@dataclass
class Traits:
    """
    Personality traits for a citizen.
    
    Uses the Big Five personality model with values from 0.0 to 1.0.
    Traits are stable and don't change during simulation (by default).
    """
    
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5
    
    def get(self, trait_type: TraitType) -> float:
        """Get the value of a specific trait."""
        return getattr(self, trait_type.value)
    
    def get_all(self) -> Dict[str, float]:
        """Get all trait values."""
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }
    
    @classmethod
    def random(cls, rng) -> "Traits":
        """Generate random traits using the provided RNG."""
        return cls(
            openness=rng.random(),
            conscientiousness=rng.random(),
            extraversion=rng.random(),
            agreeableness=rng.random(),
            neuroticism=rng.random(),
        )
    
    def is_introverted(self) -> bool:
        """Check if the citizen tends toward introversion."""
        return self.extraversion < 0.4
    
    def is_risk_averse(self) -> bool:
        """Check if the citizen tends to avoid risk."""
        return self.neuroticism > 0.6 or self.openness < 0.4


@dataclass
class Values:
    """
    Personal values that guide priorities and decisions.
    
    Values influence what citizens prioritize when making choices.
    """
    
    security: float = 0.5
    achievement: float = 0.5
    hedonism: float = 0.5
    benevolence: float = 0.5
    conformity: float = 0.5
    self_direction: float = 0.5
    
    def get(self, value_type: ValueType) -> float:
        """Get the strength of a specific value."""
        return getattr(self, value_type.value)
    
    def get_all(self) -> Dict[str, float]:
        """Get all value strengths."""
        return {
            "security": self.security,
            "achievement": self.achievement,
            "hedonism": self.hedonism,
            "benevolence": self.benevolence,
            "conformity": self.conformity,
            "self_direction": self.self_direction,
        }
    
    def get_priority_order(self) -> list:
        """Get values sorted by priority (highest first)."""
        all_values = self.get_all()
        return sorted(all_values.items(), key=lambda x: x[1], reverse=True)
    
    @classmethod
    def random(cls, rng) -> "Values":
        """Generate random values using the provided RNG."""
        return cls(
            security=rng.random(),
            achievement=rng.random(),
            hedonism=rng.random(),
            benevolence=rng.random(),
            conformity=rng.random(),
            self_direction=rng.random(),
        )
