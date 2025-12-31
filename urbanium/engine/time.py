"""
TimeSystem - Manages simulation time.

Time advances in discrete ticks. Each tick represents a fixed unit of time.
"""

from dataclasses import dataclass
from enum import Enum


class TimeOfDay(Enum):
    """Time of day periods."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


@dataclass
class TimeSystem:
    """
    Manages the simulation's time system.
    
    Provides tick-based time with optional mapping to
    hours, days, weeks for more realistic scenarios.
    """
    
    current_tick: int = 0
    ticks_per_day: int = 24
    ticks_per_hour: int = 1
    
    def initialize(self) -> None:
        """Initialize the time system."""
        self.current_tick = 0
    
    def advance(self, ticks: int = 1) -> None:
        """Advance time by the specified number of ticks."""
        self.current_tick += ticks
    
    @property
    def current_day(self) -> int:
        """Get the current day number."""
        return self.current_tick // self.ticks_per_day
    
    @property
    def current_hour(self) -> int:
        """Get the current hour of the day (0-23)."""
        return (self.current_tick % self.ticks_per_day) // self.ticks_per_hour
    
    @property
    def time_of_day(self) -> TimeOfDay:
        """Get the current time of day period."""
        hour = self.current_hour
        if 6 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 18:
            return TimeOfDay.AFTERNOON
        elif 18 <= hour < 22:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT
    
    @property
    def is_work_hours(self) -> bool:
        """Check if current time is during typical work hours."""
        return 9 <= self.current_hour < 17
    
    @property
    def current_week(self) -> int:
        """Get the current week number."""
        return self.current_day // 7
    
    @property
    def day_of_week(self) -> int:
        """Get the day of the week (0=Monday, 6=Sunday)."""
        return self.current_day % 7
    
    @property
    def is_weekend(self) -> bool:
        """Check if it's the weekend."""
        return self.day_of_week >= 5
