"""
Needs - Dynamic needs that drive behavior.

Needs evolve over time and must be satisfied through actions.
They are a primary driver of agent decision-making.
"""

from dataclasses import dataclass, field
from typing import Dict
from enum import Enum


class NeedType(Enum):
    """Types of needs that citizens have."""
    # Physiological needs
    FOOD = "food"
    REST = "rest"
    SHELTER = "shelter"
    
    # Safety needs
    SAFETY = "safety"
    FINANCIAL = "financial"
    
    # Social needs
    SOCIAL = "social"
    BELONGING = "belonging"
    
    # Esteem needs
    ESTEEM = "esteem"
    ACHIEVEMENT = "achievement"
    
    # Self-actualization
    GROWTH = "growth"


@dataclass
class Need:
    """A single need with current level and decay rate."""
    need_type: NeedType
    current_level: float = 100.0  # 0-100
    max_level: float = 100.0
    decay_rate: float = 1.0  # Per tick
    urgency_threshold: float = 30.0
    critical_threshold: float = 10.0
    
    def update(self) -> None:
        """Update the need level (decay over time)."""
        self.current_level = max(0.0, self.current_level - self.decay_rate)
    
    def satisfy(self, amount: float) -> None:
        """Satisfy the need by the given amount."""
        self.current_level = min(self.max_level, self.current_level + amount)
    
    @property
    def satisfaction(self) -> float:
        """Get the satisfaction level (0.0 to 1.0)."""
        return self.current_level / self.max_level
    
    @property
    def is_urgent(self) -> bool:
        """Check if the need is urgent."""
        return self.current_level <= self.urgency_threshold
    
    @property
    def is_critical(self) -> bool:
        """Check if the need is critical."""
        return self.current_level <= self.critical_threshold


@dataclass
class Needs:
    """
    Collection of all needs for a citizen.
    
    Needs decay over time and must be satisfied through actions.
    """
    
    _needs: Dict[NeedType, Need] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default needs."""
        if not self._needs:
            self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Set up default needs with appropriate decay rates."""
        self._needs = {
            NeedType.FOOD: Need(
                need_type=NeedType.FOOD,
                decay_rate=2.0,  # Decays faster
                urgency_threshold=40.0,
            ),
            NeedType.REST: Need(
                need_type=NeedType.REST,
                decay_rate=1.5,
                urgency_threshold=30.0,
            ),
            NeedType.SHELTER: Need(
                need_type=NeedType.SHELTER,
                decay_rate=0.1,  # Decays slowly
            ),
            NeedType.FINANCIAL: Need(
                need_type=NeedType.FINANCIAL,
                decay_rate=0.5,
            ),
            NeedType.SOCIAL: Need(
                need_type=NeedType.SOCIAL,
                decay_rate=0.3,
            ),
            NeedType.ESTEEM: Need(
                need_type=NeedType.ESTEEM,
                decay_rate=0.2,
            ),
        }
    
    def get(self, need_type: NeedType) -> Need:
        """Get a specific need."""
        return self._needs.get(need_type)
    
    def get_level(self, need_type: NeedType) -> float:
        """Get the current level of a need."""
        need = self._needs.get(need_type)
        return need.current_level if need else 0.0
    
    def get_all(self) -> Dict[str, float]:
        """Get all need levels."""
        return {
            need_type.value: need.current_level
            for need_type, need in self._needs.items()
        }
    
    def update(self) -> None:
        """Update all needs (apply decay)."""
        for need in self._needs.values():
            need.update()
    
    def satisfy(self, need_type: NeedType, amount: float) -> None:
        """Satisfy a specific need."""
        if need_type in self._needs:
            self._needs[need_type].satisfy(amount)
    
    def get_urgent_needs(self) -> list:
        """Get list of urgent needs, sorted by urgency."""
        urgent = [
            need for need in self._needs.values()
            if need.is_urgent
        ]
        return sorted(urgent, key=lambda n: n.current_level)
    
    def get_critical_needs(self) -> list:
        """Get list of critical needs."""
        return [
            need for need in self._needs.values()
            if need.is_critical
        ]
    
    def get_most_pressing(self) -> Need:
        """Get the most pressing need."""
        return min(self._needs.values(), key=lambda n: n.current_level)
    
    def get_overall_satisfaction(self) -> float:
        """Get overall need satisfaction (0.0 to 1.0)."""
        if not self._needs:
            return 1.0
        total = sum(need.satisfaction for need in self._needs.values())
        return total / len(self._needs)
    
    # Convenience property accessors for common needs
    @property
    def food(self) -> float:
        """Get food need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.FOOD)
        return need.satisfaction if need else 1.0
    
    @food.setter
    def food(self, value: float) -> None:
        """Set food need level."""
        if NeedType.FOOD in self._needs:
            self._needs[NeedType.FOOD].current_level = min(100.0, max(0.0, value * 100.0))
    
    @property
    def rest(self) -> float:
        """Get rest need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.REST)
        return need.satisfaction if need else 1.0
    
    @rest.setter
    def rest(self, value: float) -> None:
        """Set rest need level."""
        if NeedType.REST in self._needs:
            self._needs[NeedType.REST].current_level = min(100.0, max(0.0, value * 100.0))
    
    @property
    def social(self) -> float:
        """Get social need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.SOCIAL)
        return need.satisfaction if need else 1.0
    
    @social.setter
    def social(self, value: float) -> None:
        """Set social need level."""
        if NeedType.SOCIAL in self._needs:
            self._needs[NeedType.SOCIAL].current_level = min(100.0, max(0.0, value * 100.0))
    
    @property
    def shelter(self) -> float:
        """Get shelter need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.SHELTER)
        return need.satisfaction if need else 1.0
    
    @shelter.setter
    def shelter(self, value: float) -> None:
        """Set shelter need level."""
        if NeedType.SHELTER in self._needs:
            self._needs[NeedType.SHELTER].current_level = min(100.0, max(0.0, value * 100.0))
    
    @property
    def financial(self) -> float:
        """Get financial need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.FINANCIAL)
        return need.satisfaction if need else 1.0
    
    @financial.setter
    def financial(self, value: float) -> None:
        """Set financial need level."""
        if NeedType.FINANCIAL in self._needs:
            self._needs[NeedType.FINANCIAL].current_level = min(100.0, max(0.0, value * 100.0))
    
    @property
    def esteem(self) -> float:
        """Get esteem need satisfaction (0.0 to 1.0)."""
        need = self._needs.get(NeedType.ESTEEM)
        return need.satisfaction if need else 1.0
    
    @esteem.setter
    def esteem(self, value: float) -> None:
        """Set esteem need level."""
        if NeedType.ESTEEM in self._needs:
            self._needs[NeedType.ESTEEM].current_level = min(100.0, max(0.0, value * 100.0))
