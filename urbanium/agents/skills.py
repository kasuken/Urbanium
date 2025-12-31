"""
Skills - Abilities and competencies of citizens.

Skills determine what jobs citizens can hold and how effectively
they can perform certain actions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class SkillCategory(Enum):
    """Categories of skills."""
    COGNITIVE = "cognitive"
    PHYSICAL = "physical"
    SOCIAL = "social"
    TECHNICAL = "technical"
    CREATIVE = "creative"


@dataclass
class Skill:
    """A single skill with level and experience."""
    name: str
    category: SkillCategory
    level: float = 0.0  # 0-100
    experience: float = 0.0
    
    # Experience required for level up
    experience_per_level: float = 100.0
    
    def add_experience(self, amount: float) -> bool:
        """
        Add experience to the skill.
        
        Returns:
            bool: True if leveled up
        """
        self.experience += amount
        
        # Check for level up
        if self.experience >= self.experience_per_level:
            self.experience -= self.experience_per_level
            self.level = min(100.0, self.level + 1)
            return True
        return False
    
    def meets_requirement(self, required_level: float) -> bool:
        """Check if skill level meets a requirement."""
        return self.level >= required_level


@dataclass
class Skills:
    """
    Collection of skills for a citizen.
    
    Skills can be learned and improved through actions.
    """
    
    _skills: Dict[str, Skill] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default skills."""
        if not self._skills:
            self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Set up default skills at level 0."""
        defaults = [
            ("communication", SkillCategory.SOCIAL),
            ("problem_solving", SkillCategory.COGNITIVE),
            ("manual_labor", SkillCategory.PHYSICAL),
            ("technical", SkillCategory.TECHNICAL),
            ("creativity", SkillCategory.CREATIVE),
        ]
        
        for name, category in defaults:
            self._skills[name] = Skill(name=name, category=category)
    
    def get(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self._skills.get(skill_name)
    
    def get_level(self, skill_name: str) -> float:
        """Get the level of a skill."""
        skill = self._skills.get(skill_name)
        return skill.level if skill else 0.0
    
    def add_skill(self, skill: Skill) -> None:
        """Add or update a skill."""
        self._skills[skill.name] = skill
    
    def gain_experience(self, skill_name: str, amount: float) -> bool:
        """
        Add experience to a skill.
        
        Returns:
            bool: True if leveled up
        """
        if skill_name not in self._skills:
            return False
        return self._skills[skill_name].add_experience(amount)
    
    def get_all(self) -> Dict[str, float]:
        """Get all skill levels."""
        return {name: skill.level for name, skill in self._skills.items()}
    
    def get_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a category."""
        return [
            skill for skill in self._skills.values()
            if skill.category == category
        ]
    
    def meets_requirements(self, requirements: Dict[str, float]) -> bool:
        """Check if all skill requirements are met."""
        for skill_name, required_level in requirements.items():
            if self.get_level(skill_name) < required_level:
                return False
        return True
    
    def get_best_skill(self) -> Optional[Skill]:
        """Get the highest level skill."""
        if not self._skills:
            return None
        return max(self._skills.values(), key=lambda s: s.level)
    
    @classmethod
    def random(cls, rng, max_level: float = 50.0) -> "Skills":
        """Generate skills with random levels."""
        skills = cls()
        for skill in skills._skills.values():
            skill.level = rng.random() * max_level
        return skills
