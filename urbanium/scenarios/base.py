"""
Base Scenario - Abstract base class for scenarios.

Scenarios define the initial conditions for a simulation run.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen


@dataclass
class ScenarioConfig:
    """Configuration for a scenario."""
    name: str = "Unnamed Scenario"
    description: str = ""
    
    # Random seed for reproducibility
    seed: int = 42
    
    # Population settings
    population_size: int = 100
    
    # Time settings
    max_ticks: int = 1000
    ticks_per_day: int = 24
    
    # Economic settings
    initial_money_range: tuple = (100.0, 1000.0)
    base_wage: float = 100.0
    base_rent: float = 50.0
    
    # Geographic settings
    num_districts: int = 5
    
    # Custom parameters
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Scenario(ABC):
    """
    Base class for simulation scenarios.
    
    Scenarios are responsible for:
    1. Creating and configuring the world
    2. Generating the initial population
    3. Setting up the geographic structure
    4. Configuring economic conditions
    """
    
    config: ScenarioConfig = field(default_factory=ScenarioConfig)
    
    @abstractmethod
    def setup_world(self, world: "World") -> None:
        """
        Set up the world state.
        
        Called once at the start of the simulation.
        """
        pass
    
    @abstractmethod
    def generate_population(self, world: "World") -> List["Citizen"]:
        """
        Generate the initial population.
        
        Returns:
            List of citizens to add to the simulation
        """
        pass
    
    @abstractmethod
    def setup_geography(self, world: "World") -> None:
        """
        Set up the geographic structure.
        
        Creates locations, districts, and connections.
        """
        pass
    
    @abstractmethod
    def setup_economy(self, world: "World") -> None:
        """
        Set up the economic conditions.
        
        Creates jobs, housing, and sets prices.
        """
        pass
    
    def initialize(self, world: "World") -> List["Citizen"]:
        """
        Initialize the complete scenario.
        
        Called by the simulation runner to set everything up.
        """
        # Set up world systems
        world.seed = self.config.seed
        world.time.ticks_per_day = self.config.ticks_per_day
        
        # Setup in order
        self.setup_geography(world)
        self.setup_economy(world)
        self.setup_world(world)
        
        # Generate population
        citizens = self.generate_population(world)
        
        return citizens
    
    def get_description(self) -> str:
        """Get a human-readable description of the scenario."""
        return f"{self.config.name}: {self.config.description}"
