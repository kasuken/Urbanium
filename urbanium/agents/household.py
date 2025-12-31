"""
Household System - Family units and living arrangements.

Households represent:
- Groups of people living together
- Family dynamics (parents, children, roommates)
- Shared finances and resources
- Home ownership and maintenance
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set
import random


class HouseholdType(Enum):
    """Types of household arrangements."""
    SINGLE = "single"
    COUPLE = "couple"
    NUCLEAR_FAMILY = "nuclear_family"  # Parents + children
    SINGLE_PARENT = "single_parent"
    EXTENDED_FAMILY = "extended_family"
    ROOMMATES = "roommates"
    MULTIGENERATIONAL = "multigenerational"


class FamilyRole(Enum):
    """Role within a family/household."""
    HEAD = "head"
    SPOUSE = "spouse"
    CHILD = "child"
    PARENT = "parent"
    GRANDPARENT = "grandparent"
    SIBLING = "sibling"
    ROOMMATE = "roommate"
    DEPENDENT = "dependent"


@dataclass
class HouseholdMember:
    """A member of a household."""
    
    citizen_id: str
    name: str
    role: FamilyRole
    joined: datetime = field(default_factory=datetime.now)
    contributes_income: bool = True
    income_contribution: float = 0.0
    is_dependent: bool = False
    age: float = 25.0


@dataclass
class Household:
    """
    A household - a group of people living together.
    
    Attributes:
        id: Unique identifier
        name: Household name (e.g., "The Smith Family")
        household_type: Type of household arrangement
        members: List of household members
        location_id: Where the household lives
        home_value: Value of the home (if owned)
        is_renting: Whether renting or owning
        monthly_rent: Rent payment (if renting)
        shared_finances: Total shared household money
        formed: When the household was formed
    """
    
    id: str
    name: str
    household_type: HouseholdType = HouseholdType.SINGLE
    members: List[HouseholdMember] = field(default_factory=list)
    
    # Location
    location_id: Optional[str] = None
    address: str = ""
    
    # Finances
    home_value: float = 0.0
    is_renting: bool = True
    monthly_rent: float = 1000.0
    mortgage_remaining: float = 0.0
    shared_finances: float = 0.0
    
    # Tracking
    formed: datetime = field(default_factory=datetime.now)
    
    def add_member(
        self,
        citizen_id: str,
        name: str,
        role: FamilyRole,
        age: float = 25.0,
        is_dependent: bool = False,
    ) -> HouseholdMember:
        """Add a member to the household."""
        member = HouseholdMember(
            citizen_id=citizen_id,
            name=name,
            role=role,
            is_dependent=is_dependent,
            age=age,
            contributes_income=not is_dependent and age >= 16,
        )
        self.members.append(member)
        self._update_type()
        return member
    
    def remove_member(self, citizen_id: str) -> Optional[HouseholdMember]:
        """Remove a member from the household."""
        for i, member in enumerate(self.members):
            if member.citizen_id == citizen_id:
                removed = self.members.pop(i)
                self._update_type()
                return removed
        return None
    
    def get_member(self, citizen_id: str) -> Optional[HouseholdMember]:
        """Get a specific member."""
        for member in self.members:
            if member.citizen_id == citizen_id:
                return member
        return None
    
    def _update_type(self) -> None:
        """Update household type based on members."""
        if len(self.members) == 0:
            return
        
        if len(self.members) == 1:
            self.household_type = HouseholdType.SINGLE
            return
        
        # Check for children
        has_children = any(m.role == FamilyRole.CHILD for m in self.members)
        has_spouse = any(m.role == FamilyRole.SPOUSE for m in self.members)
        has_grandparents = any(m.role == FamilyRole.GRANDPARENT for m in self.members)
        only_roommates = all(m.role == FamilyRole.ROOMMATE for m in self.members)
        
        if has_grandparents:
            self.household_type = HouseholdType.MULTIGENERATIONAL
        elif has_children and has_spouse:
            self.household_type = HouseholdType.NUCLEAR_FAMILY
        elif has_children and not has_spouse:
            self.household_type = HouseholdType.SINGLE_PARENT
        elif has_spouse and not has_children:
            self.household_type = HouseholdType.COUPLE
        elif only_roommates:
            self.household_type = HouseholdType.ROOMMATES
        else:
            self.household_type = HouseholdType.EXTENDED_FAMILY
    
    def get_head(self) -> Optional[HouseholdMember]:
        """Get the head of household."""
        for member in self.members:
            if member.role == FamilyRole.HEAD:
                return member
        # If no head, return first adult
        for member in self.members:
            if not member.is_dependent:
                return member
        return self.members[0] if self.members else None
    
    def get_children(self) -> List[HouseholdMember]:
        """Get all children in the household."""
        return [m for m in self.members if m.role == FamilyRole.CHILD]
    
    def get_adults(self) -> List[HouseholdMember]:
        """Get all adults in the household."""
        return [m for m in self.members if not m.is_dependent]
    
    def get_dependents(self) -> List[HouseholdMember]:
        """Get all dependents."""
        return [m for m in self.members if m.is_dependent]
    
    def calculate_monthly_expenses(self) -> float:
        """Calculate total monthly expenses."""
        expenses = 0.0
        
        # Housing
        if self.is_renting:
            expenses += self.monthly_rent
        else:
            # Mortgage payment estimate
            if self.mortgage_remaining > 0:
                expenses += self.mortgage_remaining / 360  # Assume 30-year mortgage
        
        # Per-person expenses
        expenses += len(self.members) * 300  # Food, utilities, etc.
        
        # Children cost more
        expenses += len(self.get_children()) * 200
        
        return expenses
    
    def calculate_total_income(self) -> float:
        """Calculate total household income."""
        return sum(
            m.income_contribution
            for m in self.members
            if m.contributes_income
        )
    
    def update_member_income(self, citizen_id: str, income: float) -> None:
        """Update a member's income contribution."""
        member = self.get_member(citizen_id)
        if member:
            member.income_contribution = income
    
    def is_financially_stable(self) -> bool:
        """Check if household is financially stable."""
        income = self.calculate_total_income()
        expenses = self.calculate_monthly_expenses()
        return income >= expenses * 0.9
    
    def buy_home(self, value: float, down_payment: float) -> bool:
        """Purchase a home."""
        if self.shared_finances >= down_payment:
            self.shared_finances -= down_payment
            self.home_value = value
            self.mortgage_remaining = value - down_payment
            self.is_renting = False
            self.monthly_rent = 0
            return True
        return False
    
    def pay_monthly_bills(self) -> Tuple[bool, float]:
        """Pay monthly expenses."""
        expenses = self.calculate_monthly_expenses()
        
        if self.shared_finances >= expenses:
            self.shared_finances -= expenses
            return True, expenses
        else:
            # Partial payment
            paid = self.shared_finances
            self.shared_finances = 0
            return False, paid
    
    def contribute_to_shared(self, amount: float) -> None:
        """Add money to shared finances."""
        self.shared_finances += amount
    
    @property
    def size(self) -> int:
        """Get household size."""
        return len(self.members)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get household summary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.household_type.value,
            "size": self.size,
            "adults": len(self.get_adults()),
            "children": len(self.get_children()),
            "is_renting": self.is_renting,
            "monthly_expenses": self.calculate_monthly_expenses(),
            "monthly_income": self.calculate_total_income(),
            "is_stable": self.is_financially_stable(),
        }


# Import Tuple for type hints
from typing import Tuple


@dataclass
class FamilyTree:
    """
    Tracks family relationships across generations.
    """
    
    # Parent -> Children mapping
    parent_to_children: Dict[str, Set[str]] = field(default_factory=dict)
    
    # Child -> Parents mapping
    child_to_parents: Dict[str, Set[str]] = field(default_factory=dict)
    
    # Spouse pairs
    marriages: Dict[str, str] = field(default_factory=dict)  # Both directions
    
    # Sibling groups
    siblings: Dict[str, Set[str]] = field(default_factory=dict)
    
    def add_parent_child(self, parent_id: str, child_id: str) -> None:
        """Record a parent-child relationship."""
        if parent_id not in self.parent_to_children:
            self.parent_to_children[parent_id] = set()
        self.parent_to_children[parent_id].add(child_id)
        
        if child_id not in self.child_to_parents:
            self.child_to_parents[child_id] = set()
        self.child_to_parents[child_id].add(parent_id)
    
    def add_marriage(self, spouse1_id: str, spouse2_id: str) -> None:
        """Record a marriage."""
        self.marriages[spouse1_id] = spouse2_id
        self.marriages[spouse2_id] = spouse1_id
    
    def remove_marriage(self, spouse1_id: str, spouse2_id: str) -> None:
        """Remove a marriage (divorce)."""
        self.marriages.pop(spouse1_id, None)
        self.marriages.pop(spouse2_id, None)
    
    def add_siblings(self, sibling_ids: List[str]) -> None:
        """Record siblings."""
        for sib_id in sibling_ids:
            if sib_id not in self.siblings:
                self.siblings[sib_id] = set()
            for other_id in sibling_ids:
                if other_id != sib_id:
                    self.siblings[sib_id].add(other_id)
    
    def get_children(self, parent_id: str) -> Set[str]:
        """Get all children of a parent."""
        return self.parent_to_children.get(parent_id, set())
    
    def get_parents(self, child_id: str) -> Set[str]:
        """Get parents of a child."""
        return self.child_to_parents.get(child_id, set())
    
    def get_spouse(self, citizen_id: str) -> Optional[str]:
        """Get spouse of a citizen."""
        return self.marriages.get(citizen_id)
    
    def get_siblings(self, citizen_id: str) -> Set[str]:
        """Get siblings of a citizen."""
        return self.siblings.get(citizen_id, set())
    
    def get_grandchildren(self, grandparent_id: str) -> Set[str]:
        """Get all grandchildren."""
        grandchildren = set()
        for child_id in self.get_children(grandparent_id):
            grandchildren.update(self.get_children(child_id))
        return grandchildren
    
    def get_grandparents(self, grandchild_id: str) -> Set[str]:
        """Get all grandparents."""
        grandparents = set()
        for parent_id in self.get_parents(grandchild_id):
            grandparents.update(self.get_parents(parent_id))
        return grandparents
    
    def are_related(self, id1: str, id2: str, max_degree: int = 3) -> bool:
        """
        Check if two people are related within a certain degree.
        
        Args:
            id1: First person
            id2: Second person
            max_degree: Maximum relationship degree to check
            
        Returns:
            True if related within the degree
        """
        if id1 == id2:
            return True
        
        # Check direct relationships
        if id2 in self.get_parents(id1) or id2 in self.get_children(id1):
            return True
        if self.marriages.get(id1) == id2:
            return True
        if id2 in self.get_siblings(id1):
            return True
        
        if max_degree >= 2:
            # Grandparents/grandchildren
            if id2 in self.get_grandparents(id1) or id2 in self.get_grandchildren(id1):
                return True
            # Aunts/Uncles
            for parent_id in self.get_parents(id1):
                if id2 in self.get_siblings(parent_id):
                    return True
            # Nieces/Nephews
            for sibling_id in self.get_siblings(id1):
                if id2 in self.get_children(sibling_id):
                    return True
        
        if max_degree >= 3:
            # Cousins
            for parent_id in self.get_parents(id1):
                for aunt_uncle_id in self.get_siblings(parent_id):
                    if id2 in self.get_children(aunt_uncle_id):
                        return True
        
        return False
    
    def get_family_size(self, citizen_id: str) -> int:
        """Get total family size."""
        family = set()
        family.update(self.get_parents(citizen_id))
        family.update(self.get_children(citizen_id))
        family.update(self.get_siblings(citizen_id))
        spouse = self.get_spouse(citizen_id)
        if spouse:
            family.add(spouse)
        return len(family)


@dataclass
class HouseholdManager:
    """
    Manages all households in the city.
    """
    
    households: Dict[str, Household] = field(default_factory=dict)
    citizen_to_household: Dict[str, str] = field(default_factory=dict)
    family_tree: FamilyTree = field(default_factory=FamilyTree)
    
    _next_id: int = 1
    
    def create_household(
        self,
        name: str,
        household_type: HouseholdType = HouseholdType.SINGLE,
    ) -> Household:
        """Create a new household."""
        household_id = f"household_{self._next_id}"
        self._next_id += 1
        
        household = Household(
            id=household_id,
            name=name,
            household_type=household_type,
        )
        self.households[household_id] = household
        return household
    
    def add_citizen_to_household(
        self,
        citizen_id: str,
        citizen_name: str,
        household_id: str,
        role: FamilyRole,
        age: float = 25.0,
        is_dependent: bool = False,
    ) -> Optional[HouseholdMember]:
        """Add a citizen to an existing household."""
        household = self.households.get(household_id)
        if not household:
            return None
        
        # Remove from old household if any
        old_household_id = self.citizen_to_household.get(citizen_id)
        if old_household_id and old_household_id != household_id:
            old_household = self.households.get(old_household_id)
            if old_household:
                old_household.remove_member(citizen_id)
        
        # Add to new household
        member = household.add_member(
            citizen_id=citizen_id,
            name=citizen_name,
            role=role,
            age=age,
            is_dependent=is_dependent,
        )
        self.citizen_to_household[citizen_id] = household_id
        return member
    
    def get_household(self, household_id: str) -> Optional[Household]:
        """Get a household by ID."""
        return self.households.get(household_id)
    
    def get_citizen_household(self, citizen_id: str) -> Optional[Household]:
        """Get the household a citizen belongs to."""
        household_id = self.citizen_to_household.get(citizen_id)
        if household_id:
            return self.households.get(household_id)
        return None
    
    def create_couple_household(
        self,
        partner1_id: str,
        partner1_name: str,
        partner2_id: str,
        partner2_name: str,
        are_married: bool = False,
    ) -> Household:
        """Create a household for a couple."""
        name = f"The {partner1_name.split()[0]} Household"
        household = self.create_household(
            name=name,
            household_type=HouseholdType.COUPLE,
        )
        
        household.add_member(partner1_id, partner1_name, FamilyRole.HEAD)
        household.add_member(partner2_id, partner2_name, FamilyRole.SPOUSE)
        
        self.citizen_to_household[partner1_id] = household.id
        self.citizen_to_household[partner2_id] = household.id
        
        if are_married:
            self.family_tree.add_marriage(partner1_id, partner2_id)
        
        return household
    
    def add_child_to_family(
        self,
        parent1_id: str,
        parent2_id: Optional[str],
        child_id: str,
        child_name: str,
    ) -> Optional[Household]:
        """Add a newborn/child to a family."""
        household = self.get_citizen_household(parent1_id)
        if not household:
            return None
        
        # Add child to household
        household.add_member(
            citizen_id=child_id,
            name=child_name,
            role=FamilyRole.CHILD,
            age=0.0,
            is_dependent=True,
        )
        self.citizen_to_household[child_id] = household.id
        
        # Update family tree
        self.family_tree.add_parent_child(parent1_id, child_id)
        if parent2_id:
            self.family_tree.add_parent_child(parent2_id, child_id)
        
        # Get existing children for sibling relationships
        children = household.get_children()
        sibling_ids = [m.citizen_id for m in children]
        if len(sibling_ids) > 1:
            self.family_tree.add_siblings(sibling_ids)
        
        return household
    
    def child_moves_out(
        self,
        child_id: str,
        child_name: str,
    ) -> Household:
        """Handle a child moving out to their own household."""
        old_household = self.get_citizen_household(child_id)
        if old_household:
            old_household.remove_member(child_id)
        
        # Create new single household
        new_household = self.create_household(
            name=f"{child_name}'s Place",
            household_type=HouseholdType.SINGLE,
        )
        new_household.add_member(child_id, child_name, FamilyRole.HEAD)
        self.citizen_to_household[child_id] = new_household.id
        
        return new_household
    
    def dissolve_household(self, household_id: str) -> None:
        """Dissolve a household (e.g., after death or all members leave)."""
        household = self.households.get(household_id)
        if household:
            for member in household.members:
                self.citizen_to_household.pop(member.citizen_id, None)
            del self.households[household_id]
    
    def get_all_families_with_children(self) -> List[Household]:
        """Get all households with children."""
        return [
            h for h in self.households.values()
            if len(h.get_children()) > 0
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get household statistics."""
        total = len(self.households)
        if total == 0:
            return {"total": 0}
        
        type_counts = {}
        for household in self.households.values():
            type_name = household.household_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        total_people = sum(h.size for h in self.households.values())
        avg_size = total_people / total if total > 0 else 0
        
        return {
            "total_households": total,
            "total_people_housed": total_people,
            "average_size": avg_size,
            "by_type": type_counts,
            "families_with_children": len(self.get_all_families_with_children()),
        }
