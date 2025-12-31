"""
WorldState - The explicit and versioned world state.

The world state is the single source of truth for all simulation data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from copy import deepcopy


@dataclass
class MarketState:
    """State of economic markets."""
    labor_demand: Dict[str, int] = field(default_factory=dict)
    housing_supply: Dict[str, int] = field(default_factory=dict)
    goods_prices: Dict[str, float] = field(default_factory=dict)
    wage_levels: Dict[str, float] = field(default_factory=dict)


@dataclass
class PopulationState:
    """State of the population."""
    total_citizens: int = 0
    households: Dict[str, List[str]] = field(default_factory=dict)
    employed_count: int = 0
    unemployed_count: int = 0


@dataclass
class InfrastructureState:
    """State of city infrastructure."""
    buildings: Dict[str, dict] = field(default_factory=dict)
    districts: Dict[str, dict] = field(default_factory=dict)
    transport_links: List[tuple] = field(default_factory=list)


@dataclass
class WorldState:
    """
    The complete world state.
    
    This is explicit, versioned, and the single source of truth.
    """
    
    # Meta
    version: int = 0
    initialized: bool = False
    
    # Time and RNG
    current_tick: int = 0
    rng_state: Optional[Any] = None
    
    # Core systems
    market: MarketState = field(default_factory=MarketState)
    population: PopulationState = field(default_factory=PopulationState)
    infrastructure: InfrastructureState = field(default_factory=InfrastructureState)
    
    # Employers and services
    employers: Dict[str, dict] = field(default_factory=dict)
    public_services: Dict[str, dict] = field(default_factory=dict)
    
    # Environment
    environment: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics (rolling and snapshot)
    metrics_rolling: Dict[str, List[float]] = field(default_factory=dict)
    metrics_snapshot: Dict[str, float] = field(default_factory=dict)
    
    def copy(self) -> "WorldState":
        """Create a deep copy of the world state."""
        return deepcopy(self)
    
    def increment_version(self) -> None:
        """Increment the state version after modifications."""
        self.version += 1
