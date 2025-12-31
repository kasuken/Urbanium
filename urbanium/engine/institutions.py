"""
Institutions - Public services and governance.

Institutions represent the organized structures that provide services
and enforce rules in the city.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class InstitutionType(Enum):
    """Types of institutions."""
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    EMERGENCY = "emergency"
    UTILITIES = "utilities"


@dataclass
class Institution:
    """An institution providing services to citizens."""
    id: str
    name: str
    institution_type: InstitutionType
    location_id: str
    capacity: int = 1000
    budget: float = 0.0
    employees: List[str] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)


@dataclass
class Policy:
    """A policy or regulation affecting the city."""
    id: str
    name: str
    description: str
    active: bool = True
    parameters: Dict = field(default_factory=dict)


@dataclass
class Institutions:
    """
    Manages public institutions and governance.
    
    Provides services to citizens and enforces policies.
    """
    
    institutions: Dict[str, Institution] = field(default_factory=dict)
    policies: Dict[str, Policy] = field(default_factory=dict)
    
    # Tax rates
    income_tax_rate: float = 0.2
    property_tax_rate: float = 0.01
    sales_tax_rate: float = 0.08
    
    # Public budget
    public_budget: float = 0.0
    
    def initialize(self) -> None:
        """Initialize institutions with defaults."""
        self._create_default_policies()
    
    def _create_default_policies(self) -> None:
        """Create default policies."""
        self.policies["minimum_wage"] = Policy(
            id="minimum_wage",
            name="Minimum Wage",
            description="Minimum hourly wage for all workers",
            parameters={"amount": 15.0}
        )
        
        self.policies["housing_assistance"] = Policy(
            id="housing_assistance",
            name="Housing Assistance",
            description="Rent assistance for low-income citizens",
            parameters={"threshold": 0.3, "assistance_rate": 0.5}
        )
    
    def add_institution(self, institution: Institution) -> None:
        """Add an institution."""
        self.institutions[institution.id] = institution
    
    def get_institution(self, institution_id: str) -> Optional[Institution]:
        """Get an institution by ID."""
        return self.institutions.get(institution_id)
    
    def get_institutions_by_type(self, inst_type: InstitutionType) -> List[Institution]:
        """Get all institutions of a specific type."""
        return [
            inst for inst in self.institutions.values()
            if inst.institution_type == inst_type
        ]
    
    def is_policy_active(self, policy_id: str) -> bool:
        """Check if a policy is active."""
        policy = self.policies.get(policy_id)
        return policy.active if policy else False
    
    def get_policy_parameter(self, policy_id: str, param_name: str) -> Optional[any]:
        """Get a parameter value from a policy."""
        policy = self.policies.get(policy_id)
        if policy:
            return policy.parameters.get(param_name)
        return None
    
    def calculate_income_tax(self, income: float) -> float:
        """Calculate income tax for a given income."""
        return income * self.income_tax_rate
    
    def collect_taxes(self, amount: float) -> None:
        """Add collected taxes to the public budget."""
        self.public_budget += amount
