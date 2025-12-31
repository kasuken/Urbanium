"""
JobSearchAction - Search for employment.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from urbanium.actions.base import Action, ActionType

if TYPE_CHECKING:
    from urbanium.engine.world import World
    from urbanium.agents.citizen import Citizen
    from urbanium.engine.economy import JobType


@dataclass
class JobSearchAction(Action):
    """
    Search for a job.
    
    Prerequisites:
    - Must not be currently employed (or seeking better job)
    - Must have enough energy
    
    Effects:
    - May find a job (probabilistic based on market and skills)
    - Consume energy
    - Small cost (transport, materials)
    """
    
    action_type: ActionType = ActionType.JOB_SEARCH
    energy_cost: float = 15.0
    money_cost: float = 5.0  # Transport, printing, etc.
    duration: int = 4
    
    # Job search parameters
    target_job_type: Optional[str] = None  # Specific job type to search for
    accept_any: bool = False  # Accept any available job
    
    def check_prerequisites(self, citizen: "Citizen", local_state: dict) -> bool:
        """Check if citizen can search for jobs."""
        # Must have enough energy
        if citizen.resources.energy < self.energy_cost:
            return False
        
        # Must afford the cost
        if not citizen.resources.can_afford(self.money_cost):
            return False
        
        return True
    
    def execute(self, world: "World", agent_id: str) -> dict:
        """Execute job search and return results."""
        rng = world.get_random()
        
        # Get available jobs
        available_jobs = world.economy.get_available_jobs()
        
        if not available_jobs:
            return {
                "success": True,
                "found_job": False,
                "reason": "No jobs available",
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
        
        # Filter by target type if specified
        if self.target_job_type:
            available_jobs = [
                job for job in available_jobs
                if job.job_type.value == self.target_job_type
            ]
        
        if not available_jobs:
            return {
                "success": True,
                "found_job": False,
                "reason": "No matching jobs",
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
        
        # Calculate success probability
        # Based on: number of jobs, citizen's skills, competition
        base_probability = min(0.3, len(available_jobs) * 0.1)
        
        # TODO: Factor in skills match
        # TODO: Factor in competition
        
        if rng.random() < base_probability:
            # Found a job!
            job = rng.choice(available_jobs)
            world.economy.fill_job(job.id, agent_id)
            
            return {
                "success": True,
                "found_job": True,
                "job_id": job.id,
                "employer_id": job.employer_id,
                "wage": job.wage,
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
                "needs_satisfied": {
                    "financial": 50.0,
                    "esteem": 30.0,
                },
            }
        else:
            return {
                "success": True,
                "found_job": False,
                "reason": "Search unsuccessful",
                "money_change": -self.money_cost,
                "energy_change": -self.energy_cost,
            }
    
    def get_expected_effects(self) -> dict:
        """Get expected effects for decision making."""
        # Expected value considering probability
        return {
            "money_change": -self.money_cost,
            "energy_change": -self.energy_cost,
            "needs_satisfied": {
                "financial": 15.0,  # Expected value (probability * satisfaction)
            },
        }
