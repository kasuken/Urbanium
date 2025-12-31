"""
Urbanium - A deterministic, agent-based city simulation framework.

Urbanium models a city as a set of explicit systems (economy, geography, institutions)
and a population of constrained citizens whose decisions are bounded, observable,
and reproducible.

Version 0.2.0 adds:
- Memory system for citizens
- Emotional state tracking
- Relationship management
- Life events (marriage, children, career)
- Life cycle with aging
- City locations and workplaces
"""

__version__ = "0.2.0"
__author__ = "Urbanium Contributors"

from urbanium.engine.world import World
from urbanium.engine.tick import TickLoop
from urbanium.agents.citizen import Citizen

# City systems
from urbanium.city import (
    CityMap,
    Location,
    JobMarket,
    Company,
)

__all__ = [
    "World",
    "TickLoop",
    "Citizen",
    "CityMap",
    "Location",
    "JobMarket",
    "Company",
]
