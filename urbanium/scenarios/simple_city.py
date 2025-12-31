"""
Simple City Scenario - A basic single-city scenario for v0.

This is the default scenario for initial Urbanium experiments:
- 100 citizens
- Core actions implemented
- Single city with multiple districts
- Basic economy (jobs, housing, goods)
"""

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import random

from urbanium.scenarios.base import Scenario, ScenarioConfig
from urbanium.engine.geography import Location, LocationType, Connection, ConnectionType, District
from urbanium.engine.economy import JobPosting, HousingUnit, JobType, HousingType
from urbanium.agents.citizen import Citizen
from urbanium.agents.traits import Traits, Values
from urbanium.agents.skills import Skills

if TYPE_CHECKING:
    from urbanium.engine.world import World


@dataclass
class SimpleCityScenario(Scenario):
    """
    A simple single-city scenario.
    
    Features:
    - 5 districts (downtown + 4 residential)
    - 20 locations per district
    - Jobs matching population (~70% employment target)
    - Housing for entire population
    - Basic economic conditions
    """
    
    config: ScenarioConfig = field(default_factory=lambda: ScenarioConfig(
        name="Simple City",
        description="A basic city with 100 citizens for initial experiments",
        seed=42,
        population_size=100,
        max_ticks=1000,
        num_districts=5,
    ))
    
    def setup_world(self, world: "World") -> None:
        """Set up world state."""
        world.initialize()
    
    def setup_geography(self, world: "World") -> None:
        """Set up the city geography."""
        rng = random.Random(self.config.seed)
        
        # Create downtown district
        downtown = District(id="downtown", name="Downtown")
        world.geography.districts["downtown"] = downtown
        
        # Add downtown locations (commercial/mixed)
        for i in range(20):
            loc_type = rng.choice([LocationType.COMMERCIAL, LocationType.MIXED, LocationType.PUBLIC])
            location = Location(
                id=f"downtown_loc_{i}",
                name=f"Downtown Location {i}",
                location_type=loc_type,
                district_id="downtown",
                coordinates=(50 + rng.uniform(-10, 10), 50 + rng.uniform(-10, 10))
            )
            world.geography.add_location(location)
        
        # Create residential districts
        district_positions = [
            (25, 25),  # NW
            (75, 25),  # NE
            (25, 75),  # SW
            (75, 75),  # SE
        ]
        
        for i, (x, y) in enumerate(district_positions):
            district_id = f"residential_{i}"
            district = District(id=district_id, name=f"Residential Area {i+1}")
            world.geography.districts[district_id] = district
            
            # Add residential locations
            for j in range(15):
                location = Location(
                    id=f"{district_id}_loc_{j}",
                    name=f"Residential {i+1} Location {j}",
                    location_type=LocationType.RESIDENTIAL,
                    district_id=district_id,
                    coordinates=(x + rng.uniform(-10, 10), y + rng.uniform(-10, 10))
                )
                world.geography.add_location(location)
            
            # Connect to downtown
            downtown_loc = f"downtown_loc_{i * 5}"
            residential_loc = f"{district_id}_loc_0"
            
            connection = Connection(
                source_id=residential_loc,
                target_id=downtown_loc,
                connection_type=ConnectionType.TRANSIT,
                travel_time=3,
            )
            world.geography.add_connection(connection)
        
        # Connect locations within districts
        for district_id, district in world.geography.districts.items():
            locations = [
                loc_id for loc_id, loc in world.geography.locations.items()
                if loc.district_id == district_id
            ]
            
            # Create a simple connected network
            for i in range(len(locations) - 1):
                connection = Connection(
                    source_id=locations[i],
                    target_id=locations[i + 1],
                    connection_type=ConnectionType.PEDESTRIAN,
                    travel_time=1,
                )
                world.geography.add_connection(connection)
    
    def setup_economy(self, world: "World") -> None:
        """Set up the economic conditions."""
        rng = random.Random(self.config.seed + 1)  # Different seed for economy
        
        # Create employers and jobs
        num_jobs = int(self.config.population_size * 0.8)  # 80% of population
        
        job_type_distribution = [
            (JobType.UNSKILLED, 0.4),
            (JobType.SKILLED, 0.35),
            (JobType.PROFESSIONAL, 0.2),
            (JobType.MANAGEMENT, 0.05),
        ]
        
        wage_by_type = {
            JobType.UNSKILLED: 80.0,
            JobType.SKILLED: 120.0,
            JobType.PROFESSIONAL: 180.0,
            JobType.MANAGEMENT: 250.0,
        }
        
        downtown_locations = [
            loc_id for loc_id, loc in world.geography.locations.items()
            if loc.district_id == "downtown"
        ]
        
        for i in range(num_jobs):
            # Determine job type
            r = rng.random()
            cumulative = 0.0
            job_type = JobType.UNSKILLED
            for jt, prob in job_type_distribution:
                cumulative += prob
                if r < cumulative:
                    job_type = jt
                    break
            
            # Create job posting
            job = JobPosting(
                id=f"job_{i}",
                employer_id=f"employer_{i // 10}",
                job_type=job_type,
                wage=wage_by_type[job_type] * rng.uniform(0.9, 1.1),
                location_id=rng.choice(downtown_locations) if downtown_locations else "downtown_loc_0",
            )
            world.economy.job_postings[job.id] = job
        
        # Create housing
        num_housing = int(self.config.population_size * 1.1)  # 10% surplus
        
        housing_type_distribution = [
            (HousingType.SHARED, 0.2),
            (HousingType.STUDIO, 0.3),
            (HousingType.APARTMENT, 0.4),
            (HousingType.HOUSE, 0.1),
        ]
        
        rent_by_type = {
            HousingType.SHARED: 30.0,
            HousingType.STUDIO: 50.0,
            HousingType.APARTMENT: 80.0,
            HousingType.HOUSE: 150.0,
        }
        
        residential_locations = [
            loc_id for loc_id, loc in world.geography.locations.items()
            if loc.location_type == LocationType.RESIDENTIAL
        ]
        
        for i in range(num_housing):
            # Determine housing type
            r = rng.random()
            cumulative = 0.0
            housing_type = HousingType.STUDIO
            for ht, prob in housing_type_distribution:
                cumulative += prob
                if r < cumulative:
                    housing_type = ht
                    break
            
            capacity = 1 if housing_type != HousingType.SHARED else rng.randint(2, 4)
            
            # Create housing unit
            unit = HousingUnit(
                id=f"housing_{i}",
                housing_type=housing_type,
                rent=rent_by_type[housing_type] * rng.uniform(0.8, 1.2),
                location_id=rng.choice(residential_locations) if residential_locations else "residential_0_loc_0",
                capacity=capacity,
            )
            world.economy.housing_units[unit.id] = unit
        
        # Set base economic parameters
        world.economy.base_wage = self.config.base_wage
        world.economy.base_rent = self.config.base_rent
    
    def generate_population(self, world: "World") -> List[Citizen]:
        """Generate the initial population."""
        rng = random.Random(self.config.seed + 2)  # Different seed for population
        
        citizens = []
        
        # Names for variety
        first_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery",
            "Parker", "Drew", "Cameron", "Sage", "River", "Finley", "Hayden", "Reese",
        ]
        
        for i in range(self.config.population_size):
            # Generate random traits
            traits = Traits.random(rng)
            values = Values.random(rng)
            skills = Skills.random(rng, max_level=30.0)
            
            # Random age distribution (18-65)
            age = int(rng.gauss(35, 12))
            age = max(18, min(65, age))
            
            # Random initial money
            initial_money = rng.uniform(*self.config.initial_money_range)
            
            citizen = Citizen(
                name=f"{rng.choice(first_names)} {i+1}",
                age=age,
                traits=traits,
                values=values,
                skills=skills,
            )
            citizen.resources.money = initial_money
            citizen.resources.energy = rng.uniform(50, 100)
            
            citizens.append(citizen)
        
        # Assign some citizens to housing and jobs
        available_housing = list(world.economy.housing_units.keys())
        available_jobs = [j for j in world.economy.job_postings.values() if not j.filled]
        
        rng.shuffle(available_housing)
        rng.shuffle(available_jobs)
        
        # Assign housing to 80% of population
        num_housed = int(len(citizens) * 0.8)
        for i, citizen in enumerate(citizens[:num_housed]):
            if i < len(available_housing):
                housing_id = available_housing[i]
                housing = world.economy.housing_units[housing_id]
                if world.economy.occupy_housing(housing_id, citizen.id):
                    citizen.roles.home_id = housing_id
                    citizen.current_location = housing.location_id
        
        # Assign jobs to 60% of population
        num_employed = int(len(citizens) * 0.6)
        for i, citizen in enumerate(citizens[:num_employed]):
            if i < len(available_jobs):
                job = available_jobs[i]
                if world.economy.fill_job(job.id, citizen.id):
                    citizen.roles.job_id = job.id
                    citizen.roles.employer_id = job.employer_id
        
        return citizens
