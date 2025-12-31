"""
Life Cycle & Aging - Life stages and aging system.

Citizens progress through life stages:
- Infant (0-2)
- Child (3-12)
- Teen (13-17)
- Young Adult (18-25)
- Adult (26-40)
- Middle Age (41-60)
- Senior (61-80)
- Elder (81+)

Each stage has different needs, abilities, and possibilities.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .citizen import Citizen


class LifeStage(Enum):
    """Life stages."""
    INFANT = "infant"        # 0-2
    CHILD = "child"          # 3-12
    TEEN = "teen"            # 13-17
    YOUNG_ADULT = "young_adult"  # 18-25
    ADULT = "adult"          # 26-40
    MIDDLE_AGE = "middle_age"    # 41-60
    SENIOR = "senior"        # 61-80
    ELDER = "elder"          # 81+


# Age ranges for each stage
LIFE_STAGE_AGES = {
    LifeStage.INFANT: (0, 2),
    LifeStage.CHILD: (3, 12),
    LifeStage.TEEN: (13, 17),
    LifeStage.YOUNG_ADULT: (18, 25),
    LifeStage.ADULT: (26, 40),
    LifeStage.MIDDLE_AGE: (41, 60),
    LifeStage.SENIOR: (61, 80),
    LifeStage.ELDER: (81, 120),
}


class DeathCause(Enum):
    """Causes of death."""
    NATURAL = "natural"  # Old age
    ILLNESS = "illness"
    ACCIDENT = "accident"
    OTHER = "other"


@dataclass
class AgingStats:
    """
    Statistics that change with age.
    """
    
    # Physical stats (0-1)
    physical_health: float = 1.0
    energy_max: float = 1.0
    fertility: float = 0.0  # Ability to have children
    
    # Mental stats (0-1)
    mental_acuity: float = 1.0
    wisdom: float = 0.0
    experience: float = 0.0
    
    # Social
    social_need_multiplier: float = 1.0
    can_work: bool = False
    can_live_independently: bool = False
    can_have_children: bool = False
    can_marry: bool = False
    is_retired: bool = False


def get_life_stage(age: float) -> LifeStage:
    """Get life stage for an age."""
    for stage, (min_age, max_age) in LIFE_STAGE_AGES.items():
        if min_age <= age <= max_age:
            return stage
    return LifeStage.ELDER


def get_aging_stats(age: float) -> AgingStats:
    """
    Calculate aging stats for a given age.
    
    Args:
        age: Age in years
        
    Returns:
        AgingStats for this age
    """
    stage = get_life_stage(age)
    stats = AgingStats()
    
    # Physical health peaks in 20s, declines after 50
    if age < 20:
        stats.physical_health = 0.7 + (age / 20) * 0.3
    elif age < 50:
        stats.physical_health = 1.0
    else:
        decline = (age - 50) / 50
        stats.physical_health = max(0.3, 1.0 - decline * 0.5)
    
    # Energy peaks in 20s-30s
    if age < 15:
        stats.energy_max = 0.6 + (age / 15) * 0.4
    elif age < 40:
        stats.energy_max = 1.0
    else:
        decline = (age - 40) / 60
        stats.energy_max = max(0.4, 1.0 - decline * 0.5)
    
    # Fertility
    if age < 16 or age > 50:
        stats.fertility = 0.0
    elif age < 25:
        stats.fertility = 0.5 + (age - 16) / 18
    elif age < 35:
        stats.fertility = 1.0
    else:
        stats.fertility = max(0.0, 1.0 - (age - 35) / 15)
    
    # Mental acuity peaks in 30s-40s
    if age < 25:
        stats.mental_acuity = 0.6 + (age / 25) * 0.4
    elif age < 50:
        stats.mental_acuity = 1.0
    else:
        decline = (age - 50) / 50
        stats.mental_acuity = max(0.5, 1.0 - decline * 0.3)
    
    # Wisdom increases with age
    stats.wisdom = min(1.0, age / 80)
    
    # Experience increases with age
    stats.experience = min(1.0, age / 60)
    
    # Social needs by stage
    if stage == LifeStage.INFANT:
        stats.social_need_multiplier = 0.3
    elif stage == LifeStage.CHILD:
        stats.social_need_multiplier = 1.2
    elif stage == LifeStage.TEEN:
        stats.social_need_multiplier = 1.5
    elif stage == LifeStage.YOUNG_ADULT:
        stats.social_need_multiplier = 1.3
    elif stage in (LifeStage.ADULT, LifeStage.MIDDLE_AGE):
        stats.social_need_multiplier = 1.0
    else:
        stats.social_need_multiplier = 0.8
    
    # Capabilities
    stats.can_work = 18 <= age < 67
    stats.can_live_independently = age >= 18
    stats.can_have_children = 16 <= age <= 50
    stats.can_marry = age >= 18
    stats.is_retired = age >= 67
    
    return stats


@dataclass
class LifeCycle:
    """
    Manages the life cycle of a citizen.
    """
    
    citizen_id: str
    
    # Birth and age
    birth_date: datetime = field(default_factory=datetime.now)
    current_age: float = 25.0
    
    # Life stage
    life_stage: LifeStage = LifeStage.ADULT
    
    # Stats
    stats: AgingStats = field(default_factory=AgingStats)
    
    # Death
    is_alive: bool = True
    death_date: Optional[datetime] = None
    death_cause: Optional[DeathCause] = None
    death_age: Optional[float] = None
    
    # Genetics (affect lifespan)
    genetic_health_factor: float = 1.0  # 0.7-1.3
    expected_lifespan: float = 80.0
    
    # Life events that happened at certain ages
    milestones: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize after creation."""
        self.life_stage = get_life_stage(self.current_age)
        self.stats = get_aging_stats(self.current_age)
        
        # Set expected lifespan based on genetics
        self.expected_lifespan = 75 + self.genetic_health_factor * 15
    
    def age_by(self, years: float) -> List[str]:
        """
        Age the citizen by a number of years.
        
        Args:
            years: Years to age
            
        Returns:
            List of milestone events that occurred
        """
        if not self.is_alive:
            return []
        
        events = []
        old_age = self.current_age
        old_stage = self.life_stage
        
        self.current_age += years
        self.life_stage = get_life_stage(self.current_age)
        self.stats = get_aging_stats(self.current_age)
        
        # Check for life stage change
        if self.life_stage != old_stage:
            events.append(f"entered_{self.life_stage.value}")
            
            # Stage-specific events
            if self.life_stage == LifeStage.TEEN:
                events.append("became_teenager")
            elif self.life_stage == LifeStage.YOUNG_ADULT:
                events.append("became_adult")
                events.append("can_work")
                events.append("can_live_independently")
            elif self.life_stage == LifeStage.SENIOR:
                events.append("became_senior")
                if old_age < 65 <= self.current_age:
                    events.append("retired")
        
        # Check for significant birthdays
        for milestone_age in [18, 21, 30, 40, 50, 60, 70, 80, 90, 100]:
            if old_age < milestone_age <= self.current_age:
                events.append(f"birthday_{milestone_age}")
                self.milestones[f"age_{milestone_age}"] = self.current_age
        
        # Check for death
        if self.check_mortality():
            events.append("death")
        
        return events
    
    def check_mortality(self) -> bool:
        """
        Check if citizen dies this aging cycle.
        
        Returns:
            True if citizen dies
        """
        if not self.is_alive:
            return False
        
        # Base mortality rate increases with age
        if self.current_age < 50:
            base_rate = 0.0001 * self.current_age
        elif self.current_age < 70:
            base_rate = 0.001 * (self.current_age - 40)
        elif self.current_age < 85:
            base_rate = 0.01 * (self.current_age - 60)
        else:
            base_rate = 0.05 * (self.current_age - 70)
        
        # Adjust for health
        mortality_rate = base_rate / (self.stats.physical_health + 0.1)
        mortality_rate /= self.genetic_health_factor
        
        # Very old age has higher rate
        if self.current_age > self.expected_lifespan:
            overage = self.current_age - self.expected_lifespan
            mortality_rate += 0.05 * overage
        
        # Check against random
        if random.random() < mortality_rate:
            self.die(DeathCause.NATURAL)
            return True
        
        return False
    
    def die(self, cause: DeathCause) -> None:
        """Handle death."""
        self.is_alive = False
        self.death_date = datetime.now()
        self.death_cause = cause
        self.death_age = self.current_age
    
    def record_milestone(self, name: str) -> None:
        """Record a life milestone."""
        self.milestones[name] = self.current_age
    
    def get_age_at_milestone(self, name: str) -> Optional[float]:
        """Get age at a specific milestone."""
        return self.milestones.get(name)
    
    @property
    def years_until_retirement(self) -> float:
        """Years until retirement age (67)."""
        return max(0, 67 - self.current_age)
    
    @property
    def is_working_age(self) -> bool:
        """Check if of working age."""
        return self.stats.can_work and self.is_alive
    
    @property
    def is_child(self) -> bool:
        """Check if a child (dependent)."""
        return self.life_stage in (
            LifeStage.INFANT,
            LifeStage.CHILD,
            LifeStage.TEEN,
        )
    
    @property
    def is_elderly(self) -> bool:
        """Check if elderly."""
        return self.life_stage in (LifeStage.SENIOR, LifeStage.ELDER)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get life cycle summary."""
        return {
            "age": self.current_age,
            "life_stage": self.life_stage.value,
            "is_alive": self.is_alive,
            "physical_health": self.stats.physical_health,
            "energy_max": self.stats.energy_max,
            "can_work": self.stats.can_work,
            "can_marry": self.stats.can_marry,
            "can_have_children": self.stats.can_have_children,
            "is_retired": self.stats.is_retired,
            "wisdom": self.stats.wisdom,
            "expected_lifespan": self.expected_lifespan,
            "milestones": list(self.milestones.keys()),
        }


@dataclass
class Population:
    """
    Manages population demographics.
    """
    
    citizens: Dict[str, LifeCycle] = field(default_factory=dict)
    
    # Statistics
    births_this_year: int = 0
    deaths_this_year: int = 0
    
    def add_citizen(
        self,
        citizen_id: str,
        age: float = 25.0,
        genetic_health: float = 1.0,
    ) -> LifeCycle:
        """Add a citizen to the population."""
        lifecycle = LifeCycle(
            citizen_id=citizen_id,
            current_age=age,
            genetic_health_factor=genetic_health,
        )
        self.citizens[citizen_id] = lifecycle
        return lifecycle
    
    def birth(
        self,
        child_id: str,
        parent1_health: float = 1.0,
        parent2_health: float = 1.0,
    ) -> LifeCycle:
        """Record a birth."""
        # Child inherits average of parents' genetic health with some variation
        avg_health = (parent1_health + parent2_health) / 2
        genetic_health = avg_health + random.gauss(0, 0.1)
        genetic_health = max(0.7, min(1.3, genetic_health))
        
        lifecycle = LifeCycle(
            citizen_id=child_id,
            current_age=0.0,
            genetic_health_factor=genetic_health,
        )
        self.citizens[child_id] = lifecycle
        self.births_this_year += 1
        
        return lifecycle
    
    def death(self, citizen_id: str, cause: DeathCause = DeathCause.NATURAL) -> None:
        """Record a death."""
        lifecycle = self.citizens.get(citizen_id)
        if lifecycle and lifecycle.is_alive:
            lifecycle.die(cause)
            self.deaths_this_year += 1
    
    def age_all(self, years: float) -> Dict[str, List[str]]:
        """
        Age all citizens.
        
        Args:
            years: Years to age everyone
            
        Returns:
            Dict of citizen_id -> list of events
        """
        all_events = {}
        
        for citizen_id, lifecycle in self.citizens.items():
            events = lifecycle.age_by(years)
            if events:
                all_events[citizen_id] = events
        
        return all_events
    
    def get_living(self) -> List[LifeCycle]:
        """Get all living citizens."""
        return [lc for lc in self.citizens.values() if lc.is_alive]
    
    def get_by_stage(self, stage: LifeStage) -> List[LifeCycle]:
        """Get citizens in a life stage."""
        return [
            lc for lc in self.citizens.values()
            if lc.is_alive and lc.life_stage == stage
        ]
    
    def get_working_age(self) -> List[LifeCycle]:
        """Get all working-age citizens."""
        return [lc for lc in self.citizens.values() if lc.is_working_age]
    
    def get_children(self) -> List[LifeCycle]:
        """Get all children."""
        return [lc for lc in self.citizens.values() if lc.is_alive and lc.is_child]
    
    def get_elderly(self) -> List[LifeCycle]:
        """Get all elderly citizens."""
        return [lc for lc in self.citizens.values() if lc.is_alive and lc.is_elderly]
    
    def get_average_age(self) -> float:
        """Get average age of living population."""
        living = self.get_living()
        if not living:
            return 0.0
        return sum(lc.current_age for lc in living) / len(living)
    
    def get_age_distribution(self) -> Dict[str, int]:
        """Get population by life stage."""
        distribution = {stage.value: 0 for stage in LifeStage}
        for lifecycle in self.citizens.values():
            if lifecycle.is_alive:
                distribution[lifecycle.life_stage.value] += 1
        return distribution
    
    def get_demographics(self) -> Dict[str, Any]:
        """Get population demographics."""
        living = self.get_living()
        
        return {
            "total_population": len(living),
            "average_age": self.get_average_age(),
            "children": len(self.get_children()),
            "working_age": len(self.get_working_age()),
            "elderly": len(self.get_elderly()),
            "births_this_year": self.births_this_year,
            "deaths_this_year": self.deaths_this_year,
            "by_stage": self.get_age_distribution(),
        }
    
    def reset_yearly_stats(self) -> None:
        """Reset yearly statistics."""
        self.births_this_year = 0
        self.deaths_this_year = 0
