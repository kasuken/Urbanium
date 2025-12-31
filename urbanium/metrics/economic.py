"""
EconomicObserver - Track economic metrics.

Metrics:
- Wage distribution
- Rent index
- Gini coefficient (inequality)
- Bankruptcy rate
- Housing pressure
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING

from urbanium.metrics.observer import MetricsObserver

if TYPE_CHECKING:
    from urbanium.engine.state import WorldState
    from urbanium.agents.citizen import Citizen


@dataclass
class EconomicObserver(MetricsObserver):
    """
    Observes economic metrics including inequality.
    """
    
    name: str = "economic"
    
    # Track bankruptcies
    bankruptcy_count: int = 0
    
    def observe(
        self,
        tick: int,
        state: "WorldState",
        agents: List["Citizen"]
    ) -> Dict:
        """Observe economic metrics."""
        if not agents:
            return {}
        
        # Collect wealth data
        wealth_values = [a.resources.money for a in agents]
        
        # Basic statistics
        total_wealth = sum(wealth_values)
        mean_wealth = total_wealth / len(agents)
        min_wealth = min(wealth_values)
        max_wealth = max(wealth_values)
        
        # Calculate Gini coefficient
        gini = self._calculate_gini(wealth_values)
        
        # Count agents in poverty (less than 20% of mean wealth)
        poverty_threshold = mean_wealth * 0.2
        in_poverty = sum(1 for w in wealth_values if w < poverty_threshold)
        poverty_rate = in_poverty / len(agents)
        
        # Count bankruptcies (negative or near-zero wealth)
        current_bankrupt = sum(1 for w in wealth_values if w <= 0)
        
        # Housing statistics
        housed = sum(1 for a in agents if a.has_home)
        housing_rate = housed / len(agents)
        homeless = len(agents) - housed
        
        # Wealth distribution quintiles
        sorted_wealth = sorted(wealth_values)
        quintile_size = len(agents) // 5
        quintiles = []
        for i in range(5):
            start = i * quintile_size
            end = start + quintile_size if i < 4 else len(agents)
            q_wealth = sum(sorted_wealth[start:end])
            quintiles.append(q_wealth / total_wealth if total_wealth > 0 else 0.2)
        
        metrics = {
            "total_wealth": total_wealth,
            "mean_wealth": mean_wealth,
            "min_wealth": min_wealth,
            "max_wealth": max_wealth,
            "gini_coefficient": gini,
            "poverty_rate": poverty_rate,
            "in_poverty": in_poverty,
            "bankrupt_count": current_bankrupt,
            "housing_rate": housing_rate,
            "homeless_count": homeless,
            "wealth_bottom_20": quintiles[0],
            "wealth_top_20": quintiles[4],
        }
        
        self._record(tick, metrics)
        
        # Update aggregated results
        self.results = {
            "mean_gini": self.calculate_mean("gini_coefficient"),
            "gini_trend": self.calculate_trend("gini_coefficient"),
            "current_gini": gini,
            "mean_poverty_rate": self.calculate_mean("poverty_rate"),
            "current_poverty_rate": poverty_rate,
            "total_bankruptcies": self.bankruptcy_count,
        }
        
        return metrics
    
    def _calculate_gini(self, values: List[float]) -> float:
        """
        Calculate the Gini coefficient for wealth distribution.
        
        Gini = 0 means perfect equality
        Gini = 1 means perfect inequality
        """
        if not values or len(values) < 2:
            return 0.0
        
        # Sort values
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calculate cumulative sums
        cumsum = 0.0
        for i, v in enumerate(sorted_values):
            cumsum += (n - i) * v
        
        # Gini formula
        total = sum(sorted_values)
        if total == 0:
            return 0.0
        
        gini = (n + 1 - 2 * cumsum / total) / n
        return max(0.0, min(1.0, gini))
