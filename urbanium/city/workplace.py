"""
Workplace System - Companies, jobs, and work relationships.

The workplace system handles:
- Companies and businesses
- Jobs and positions
- Coworker relationships
- Career progression
- Work schedules
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set, Tuple
import random


class IndustryType(Enum):
    """Types of industries/sectors."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    FINANCE = "finance"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    CONSTRUCTION = "construction"
    TRANSPORTATION = "transportation"
    GOVERNMENT = "government"
    ENTERTAINMENT = "entertainment"
    AGRICULTURE = "agriculture"
    SERVICE = "service"


class PositionLevel(Enum):
    """Job position levels."""
    ENTRY = 1
    JUNIOR = 2
    MID = 3
    SENIOR = 4
    LEAD = 5
    MANAGER = 6
    DIRECTOR = 7
    EXECUTIVE = 8


class WorkScheduleType(Enum):
    """Types of work schedules."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    SHIFT_WORK = "shift_work"
    FLEXIBLE = "flexible"
    REMOTE = "remote"


@dataclass
class Position:
    """A job position at a company."""
    
    title: str
    level: PositionLevel = PositionLevel.MID
    
    # Compensation
    base_salary: float = 40000.0
    salary_range: Tuple[float, float] = (35000.0, 50000.0)
    
    # Requirements
    required_skills: List[str] = field(default_factory=list)
    min_experience_years: float = 0.0
    min_education: str = "high_school"
    
    # Work details
    schedule_type: WorkScheduleType = WorkScheduleType.FULL_TIME
    hours_per_week: float = 40.0
    is_remote_possible: bool = False
    
    # Position metadata
    department: str = "general"
    reports_to: Optional[str] = None  # Position title they report to
    
    def calculate_salary(self, experience_years: float, performance: float) -> float:
        """Calculate salary based on experience and performance."""
        min_sal, max_sal = self.salary_range
        
        # Experience factor (0-1)
        exp_factor = min(1.0, experience_years / 10.0)
        
        # Performance factor
        perf_factor = max(0.0, min(1.0, performance))
        
        # Combined factor
        factor = exp_factor * 0.6 + perf_factor * 0.4
        
        return min_sal + (max_sal - min_sal) * factor


@dataclass
class Employee:
    """An employee at a company."""
    
    citizen_id: str
    name: str
    position: str
    
    # Employment details
    hire_date: datetime = field(default_factory=datetime.now)
    salary: float = 40000.0
    
    # Performance tracking
    performance_score: float = 0.5  # 0-1
    last_review_date: Optional[datetime] = None
    
    # Work relationships
    manager_id: Optional[str] = None
    direct_reports: List[str] = field(default_factory=list)
    
    # Time tracking
    hours_worked_this_week: float = 0.0
    vacation_days_remaining: float = 14.0
    sick_days_used: float = 0.0
    
    # Career
    promotions: int = 0
    warnings: int = 0
    
    @property
    def tenure_years(self) -> float:
        """Get years of tenure."""
        delta = datetime.now() - self.hire_date
        return delta.days / 365.0
    
    def give_raise(self, percentage: float) -> float:
        """Give a raise."""
        self.salary *= (1 + percentage)
        return self.salary
    
    def promote(self, new_position: str, new_salary: float) -> None:
        """Promote to a new position."""
        self.position = new_position
        self.salary = new_salary
        self.promotions += 1
        self.performance_score = 0.5  # Reset after promotion


@dataclass
class Company:
    """
    A company/business in the city.
    
    Attributes:
        id: Unique identifier
        name: Company name
        industry: Industry sector
        employees: All employees
        positions: Available position types
        location_id: Where the company is located
        founded: When the company was founded
    """
    
    id: str
    name: str
    industry: IndustryType = IndustryType.SERVICE
    
    # Employees
    employees: Dict[str, Employee] = field(default_factory=dict)
    max_employees: int = 50
    
    # Positions
    positions: Dict[str, Position] = field(default_factory=dict)
    open_positions: Dict[str, int] = field(default_factory=dict)  # Position -> count
    
    # Location
    location_id: Optional[str] = None
    address: str = ""
    
    # Company details
    founded: datetime = field(default_factory=datetime.now)
    revenue: float = 0.0
    reputation: float = 0.5  # 0-1
    
    # Work culture
    work_life_balance: float = 0.5  # 0-1
    growth_opportunities: float = 0.5  # 0-1
    compensation_competitiveness: float = 0.5  # 0-1
    
    # Schedule
    work_start_hour: int = 9
    work_end_hour: int = 17
    
    def hire(
        self,
        citizen_id: str,
        citizen_name: str,
        position: str,
        salary: Optional[float] = None,
    ) -> Optional[Employee]:
        """Hire a new employee."""
        if len(self.employees) >= self.max_employees:
            return None
        
        if citizen_id in self.employees:
            return None
        
        # Determine salary
        if salary is None:
            pos = self.positions.get(position)
            if pos:
                salary = pos.base_salary
            else:
                salary = 35000.0
        
        employee = Employee(
            citizen_id=citizen_id,
            name=citizen_name,
            position=position,
            salary=salary,
        )
        self.employees[citizen_id] = employee
        
        # Update open positions
        if position in self.open_positions:
            self.open_positions[position] = max(0, self.open_positions[position] - 1)
            if self.open_positions[position] == 0:
                del self.open_positions[position]
        
        return employee
    
    def fire(self, citizen_id: str, reason: str = "") -> Optional[Employee]:
        """Fire an employee."""
        employee = self.employees.pop(citizen_id, None)
        if employee:
            # Remove from any management chain
            if employee.manager_id and employee.manager_id in self.employees:
                manager = self.employees[employee.manager_id]
                if citizen_id in manager.direct_reports:
                    manager.direct_reports.remove(citizen_id)
            
            # Open the position
            pos = employee.position
            self.open_positions[pos] = self.open_positions.get(pos, 0) + 1
        
        return employee
    
    def resign(self, citizen_id: str) -> Optional[Employee]:
        """Handle employee resignation."""
        return self.fire(citizen_id, "resignation")
    
    def get_employee(self, citizen_id: str) -> Optional[Employee]:
        """Get an employee by ID."""
        return self.employees.get(citizen_id)
    
    def promote_employee(
        self,
        citizen_id: str,
        new_position: str,
        raise_percentage: float = 0.15,
    ) -> bool:
        """Promote an employee."""
        employee = self.employees.get(citizen_id)
        if not employee:
            return False
        
        pos = self.positions.get(new_position)
        if pos:
            new_salary = employee.salary * (1 + raise_percentage)
            new_salary = max(new_salary, pos.salary_range[0])
            employee.promote(new_position, new_salary)
        else:
            employee.give_raise(raise_percentage)
            employee.position = new_position
            employee.promotions += 1
        
        return True
    
    def give_performance_review(
        self,
        citizen_id: str,
        score: float,
        raise_if_good: bool = True,
    ) -> Optional[float]:
        """Give a performance review."""
        employee = self.employees.get(citizen_id)
        if not employee:
            return None
        
        old_score = employee.performance_score
        # Weighted average with new score
        employee.performance_score = old_score * 0.5 + score * 0.5
        employee.last_review_date = datetime.now()
        
        # Give raise if good performance
        if raise_if_good and score > 0.7:
            raise_pct = (score - 0.5) * 0.1  # 0-5% raise
            employee.give_raise(raise_pct)
            return raise_pct
        
        return 0.0
    
    def get_coworkers(self, citizen_id: str) -> List[Employee]:
        """Get coworkers of an employee."""
        return [
            emp for cid, emp in self.employees.items()
            if cid != citizen_id
        ]
    
    def get_manager(self, citizen_id: str) -> Optional[Employee]:
        """Get the manager of an employee."""
        employee = self.employees.get(citizen_id)
        if employee and employee.manager_id:
            return self.employees.get(employee.manager_id)
        return None
    
    def get_direct_reports(self, citizen_id: str) -> List[Employee]:
        """Get direct reports of an employee."""
        employee = self.employees.get(citizen_id)
        if not employee:
            return []
        return [
            self.employees[rid]
            for rid in employee.direct_reports
            if rid in self.employees
        ]
    
    def set_manager(self, employee_id: str, manager_id: str) -> bool:
        """Set the manager for an employee."""
        employee = self.employees.get(employee_id)
        manager = self.employees.get(manager_id)
        
        if not employee or not manager:
            return False
        
        # Remove from old manager
        if employee.manager_id and employee.manager_id in self.employees:
            old_manager = self.employees[employee.manager_id]
            if employee_id in old_manager.direct_reports:
                old_manager.direct_reports.remove(employee_id)
        
        # Set new manager
        employee.manager_id = manager_id
        if employee_id not in manager.direct_reports:
            manager.direct_reports.append(employee_id)
        
        return True
    
    def open_position(self, position: str, count: int = 1) -> None:
        """Open job positions."""
        self.open_positions[position] = self.open_positions.get(position, 0) + count
    
    def has_opening(self, position: Optional[str] = None) -> bool:
        """Check if there are open positions."""
        if position:
            return self.open_positions.get(position, 0) > 0
        return len(self.open_positions) > 0
    
    def get_all_openings(self) -> Dict[str, int]:
        """Get all open positions."""
        return dict(self.open_positions)
    
    def calculate_employee_satisfaction(self, citizen_id: str) -> float:
        """Calculate how satisfied an employee is."""
        employee = self.employees.get(citizen_id)
        if not employee:
            return 0.0
        
        satisfaction = 0.5
        
        # Salary satisfaction (compare to position range)
        pos = self.positions.get(employee.position)
        if pos:
            min_sal, max_sal = pos.salary_range
            sal_ratio = (employee.salary - min_sal) / (max_sal - min_sal + 1)
            satisfaction += sal_ratio * 0.2
        
        # Performance recognition
        satisfaction += employee.performance_score * 0.15
        
        # Company culture
        satisfaction += self.work_life_balance * 0.1
        satisfaction += self.growth_opportunities * 0.1
        
        # Tenure (some people get complacent, others loyal)
        if employee.tenure_years > 2:
            satisfaction += 0.05
        
        return max(0.0, min(1.0, satisfaction))
    
    @property
    def employee_count(self) -> int:
        """Get number of employees."""
        return len(self.employees)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get company summary."""
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry.value,
            "employees": self.employee_count,
            "max_employees": self.max_employees,
            "open_positions": dict(self.open_positions),
            "reputation": self.reputation,
            "work_life_balance": self.work_life_balance,
        }


@dataclass
class JobMarket:
    """
    Manages the job market - all companies and job seekers.
    """
    
    companies: Dict[str, Company] = field(default_factory=dict)
    citizen_to_company: Dict[str, str] = field(default_factory=dict)
    
    _next_id: int = 1
    
    def create_company(
        self,
        name: str,
        industry: IndustryType,
        max_employees: int = 50,
    ) -> Company:
        """Create a new company."""
        company_id = f"company_{self._next_id}"
        self._next_id += 1
        
        company = Company(
            id=company_id,
            name=name,
            industry=industry,
            max_employees=max_employees,
        )
        self.companies[company_id] = company
        return company
    
    def get_company(self, company_id: str) -> Optional[Company]:
        """Get a company by ID."""
        return self.companies.get(company_id)
    
    def get_citizen_employer(self, citizen_id: str) -> Optional[Company]:
        """Get the company a citizen works for."""
        company_id = self.citizen_to_company.get(citizen_id)
        if company_id:
            return self.companies.get(company_id)
        return None
    
    def get_citizen_job(self, citizen_id: str) -> Optional[Employee]:
        """Get a citizen's job information."""
        company = self.get_citizen_employer(citizen_id)
        if company:
            return company.get_employee(citizen_id)
        return None
    
    def is_employed(self, citizen_id: str) -> bool:
        """Check if a citizen is employed."""
        return citizen_id in self.citizen_to_company
    
    def hire_citizen(
        self,
        citizen_id: str,
        citizen_name: str,
        company_id: str,
        position: str,
        salary: Optional[float] = None,
    ) -> Optional[Employee]:
        """Hire a citizen at a company."""
        company = self.companies.get(company_id)
        if not company:
            return None
        
        # Leave current job if employed
        self.fire_citizen(citizen_id)
        
        employee = company.hire(citizen_id, citizen_name, position, salary)
        if employee:
            self.citizen_to_company[citizen_id] = company_id
        
        return employee
    
    def fire_citizen(self, citizen_id: str) -> Optional[Tuple[Company, Employee]]:
        """Fire a citizen from their current job."""
        company_id = self.citizen_to_company.pop(citizen_id, None)
        if company_id:
            company = self.companies.get(company_id)
            if company:
                employee = company.fire(citizen_id)
                if employee:
                    return (company, employee)
        return None
    
    def resign_citizen(self, citizen_id: str) -> Optional[Tuple[Company, Employee]]:
        """Handle a citizen resigning."""
        return self.fire_citizen(citizen_id)
    
    def find_jobs(
        self,
        industry: Optional[IndustryType] = None,
        position: Optional[str] = None,
        min_salary: Optional[float] = None,
    ) -> List[Tuple[Company, str, Position]]:
        """
        Find available jobs.
        
        Args:
            industry: Filter by industry
            position: Filter by position title
            min_salary: Minimum salary
            
        Returns:
            List of (Company, position_name, Position) tuples
        """
        results = []
        
        for company in self.companies.values():
            if industry and company.industry != industry:
                continue
            
            for pos_name, count in company.open_positions.items():
                if count <= 0:
                    continue
                
                if position and pos_name != position:
                    continue
                
                pos = company.positions.get(pos_name)
                if pos and min_salary and pos.base_salary < min_salary:
                    continue
                
                results.append((company, pos_name, pos if pos else Position(title=pos_name)))
        
        return results
    
    def get_industry_statistics(self) -> Dict[str, Any]:
        """Get employment statistics by industry."""
        stats = {}
        
        for company in self.companies.values():
            industry = company.industry.value
            if industry not in stats:
                stats[industry] = {
                    "companies": 0,
                    "employees": 0,
                    "open_positions": 0,
                }
            stats[industry]["companies"] += 1
            stats[industry]["employees"] += company.employee_count
            stats[industry]["open_positions"] += sum(company.open_positions.values())
        
        return stats
    
    def get_unemployment_rate(self, total_workforce: int) -> float:
        """Calculate unemployment rate."""
        employed = len(self.citizen_to_company)
        if total_workforce <= 0:
            return 0.0
        unemployed = max(0, total_workforce - employed)
        return unemployed / total_workforce
    
    def get_coworkers(self, citizen_id: str) -> List[str]:
        """Get IDs of a citizen's coworkers."""
        company = self.get_citizen_employer(citizen_id)
        if not company:
            return []
        return [
            emp.citizen_id
            for emp in company.get_coworkers(citizen_id)
        ]
    
    def get_all_companies_in_industry(
        self,
        industry: IndustryType,
    ) -> List[Company]:
        """Get all companies in an industry."""
        return [
            c for c in self.companies.values()
            if c.industry == industry
        ]
    
    def get_total_employees(self) -> int:
        """Get total number of employed people."""
        return len(self.citizen_to_company)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get job market summary."""
        total_openings = sum(
            sum(c.open_positions.values())
            for c in self.companies.values()
        )
        
        return {
            "total_companies": len(self.companies),
            "total_employed": self.get_total_employees(),
            "total_openings": total_openings,
            "by_industry": self.get_industry_statistics(),
        }
