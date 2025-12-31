"""
EmploymentObserver - Track employment metrics.

Metrics:
- Employment rate
- Unemployment duration
- Job turnover
- Job type distribution
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING

from urbanium.metrics.observer import MetricsObserver

if TYPE_CHECKING:
    from urbanium.engine.state import WorldState
    from urbanium.agents.citizen import Citizen


@dataclass
class EmploymentObserver(MetricsObserver):
    """
    Observes employment-related metrics.
    """
    
    name: str = "employment"
    
    # Track unemployment duration per agent
    unemployment_duration: Dict[str, int] = field(default_factory=dict)
    
    def observe(
        self,
        tick: int,
        state: "WorldState",
        agents: List["Citizen"]
    ) -> Dict:
        """Observe employment metrics."""
        if not agents:
            return {}
        
        # Count employed and unemployed
        employed = sum(1 for a in agents if a.is_employed)
        unemployed = len(agents) - employed
        
        # Calculate employment rate
        employment_rate = employed / len(agents)
        
        # Update unemployment duration tracking
        for agent in agents:
            if not agent.is_employed:
                self.unemployment_duration[agent.id] = \
                    self.unemployment_duration.get(agent.id, 0) + 1
            else:
                # Reset if employed
                if agent.id in self.unemployment_duration:
                    del self.unemployment_duration[agent.id]
        
        # Calculate average unemployment duration
        avg_unemployment_duration = 0.0
        if self.unemployment_duration:
            avg_unemployment_duration = sum(self.unemployment_duration.values()) / len(self.unemployment_duration)
        
        # Long-term unemployed (more than 30 ticks)
        long_term_unemployed = sum(1 for d in self.unemployment_duration.values() if d > 30)
        
        metrics = {
            "employed_count": employed,
            "unemployed_count": unemployed,
            "employment_rate": employment_rate,
            "unemployment_rate": 1 - employment_rate,
            "avg_unemployment_duration": avg_unemployment_duration,
            "long_term_unemployed": long_term_unemployed,
        }
        
        self._record(tick, metrics)
        
        # Update aggregated results
        self.results = {
            "mean_employment_rate": self.calculate_mean("employment_rate"),
            "employment_trend": self.calculate_trend("employment_rate"),
            "current_employment_rate": employment_rate,
            "current_unemployed": unemployed,
        }
        
        return metrics
