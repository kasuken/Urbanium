"""
Economy - Labor, housing, and goods markets.

The economy system manages all market dynamics, prices, and economic state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class JobType(Enum):
    """Types of jobs in the economy."""
    UNSKILLED = "unskilled"
    SKILLED = "skilled"
    PROFESSIONAL = "professional"
    MANAGEMENT = "management"


class HousingType(Enum):
    """Types of housing."""
    STUDIO = "studio"
    APARTMENT = "apartment"
    HOUSE = "house"
    SHARED = "shared"


@dataclass
class JobPosting:
    """A job posting from an employer."""
    id: str
    employer_id: str
    job_type: JobType
    wage: float
    location_id: str
    required_skills: List[str] = field(default_factory=list)
    filled: bool = False
    employee_id: Optional[str] = None


@dataclass
class HousingUnit:
    """A housing unit in the market."""
    id: str
    housing_type: HousingType
    rent: float
    location_id: str
    capacity: int = 1
    occupied: bool = False
    tenant_ids: List[str] = field(default_factory=list)


@dataclass
class Economy:
    """
    Manages the economic systems of the city.
    
    Includes labor market, housing market, and goods/services.
    """
    
    # Labor market
    job_postings: Dict[str, JobPosting] = field(default_factory=dict)
    employers: Dict[str, dict] = field(default_factory=dict)
    
    # Housing market
    housing_units: Dict[str, HousingUnit] = field(default_factory=dict)
    
    # Goods market
    goods_prices: Dict[str, float] = field(default_factory=dict)
    
    # Economic indicators
    base_wage: float = 1000.0
    base_rent: float = 500.0
    inflation_rate: float = 0.0
    unemployment_rate: float = 0.0
    
    def initialize(self) -> None:
        """Initialize the economy with default values."""
        self._set_default_prices()
        self._create_initial_employers()
    
    def _set_default_prices(self) -> None:
        """Set default prices for goods."""
        self.goods_prices = {
            "food": 10.0,
            "transport": 5.0,
            "entertainment": 20.0,
            "utilities": 50.0,
        }
    
    def _create_initial_employers(self) -> None:
        """Create initial employers."""
        # This would be populated by scenarios
        pass
    
    def update(self, current_tick: int) -> None:
        """Update the economy for the current tick."""
        # Update prices based on supply/demand
        self._update_prices()
        
        # Calculate economic indicators
        self._calculate_indicators()
    
    def _update_prices(self) -> None:
        """Update prices based on market conditions."""
        # Simple inflation model
        for good in self.goods_prices:
            self.goods_prices[good] *= (1 + self.inflation_rate / 365)
    
    def _calculate_indicators(self) -> None:
        """Calculate economic indicators."""
        total_jobs = len(self.job_postings)
        filled_jobs = sum(1 for job in self.job_postings.values() if job.filled)
        
        if total_jobs > 0:
            self.unemployment_rate = 1 - (filled_jobs / total_jobs)
    
    def get_public_state(self) -> dict:
        """Get the public economic state visible to agents."""
        return {
            "goods_prices": self.goods_prices.copy(),
            "unemployment_rate": self.unemployment_rate,
            "available_jobs": self.get_available_jobs_count(),
            "available_housing": self.get_available_housing_count(),
        }
    
    def get_available_jobs(self, job_type: Optional[JobType] = None) -> List[JobPosting]:
        """Get available job postings, optionally filtered by type."""
        jobs = [job for job in self.job_postings.values() if not job.filled]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        return jobs
    
    def get_available_jobs_count(self) -> int:
        """Get the count of available jobs."""
        return sum(1 for job in self.job_postings.values() if not job.filled)
    
    def get_available_housing(self, housing_type: Optional[HousingType] = None) -> List[HousingUnit]:
        """Get available housing units, optionally filtered by type."""
        units = [unit for unit in self.housing_units.values() if not unit.occupied]
        if housing_type:
            units = [unit for unit in units if unit.housing_type == housing_type]
        return units
    
    def get_available_housing_count(self) -> int:
        """Get the count of available housing units."""
        return sum(1 for unit in self.housing_units.values() if not unit.occupied)
    
    def fill_job(self, job_id: str, employee_id: str) -> bool:
        """Assign an employee to a job."""
        if job_id not in self.job_postings:
            return False
        
        job = self.job_postings[job_id]
        if job.filled:
            return False
        
        job.filled = True
        job.employee_id = employee_id
        return True
    
    def occupy_housing(self, unit_id: str, tenant_id: str) -> bool:
        """Assign a tenant to a housing unit."""
        if unit_id not in self.housing_units:
            return False
        
        unit = self.housing_units[unit_id]
        if len(unit.tenant_ids) >= unit.capacity:
            return False
        
        unit.tenant_ids.append(tenant_id)
        if len(unit.tenant_ids) >= unit.capacity:
            unit.occupied = True
        return True
