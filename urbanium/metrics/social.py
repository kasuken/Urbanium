"""
SocialObserver - Track social network metrics.

Metrics:
- Network density
- Average connections
- Clustering coefficient
- Social isolation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, TYPE_CHECKING

from urbanium.metrics.observer import MetricsObserver

if TYPE_CHECKING:
    from urbanium.engine.state import WorldState
    from urbanium.agents.citizen import Citizen


@dataclass
class SocialObserver(MetricsObserver):
    """
    Observes social network metrics.
    """
    
    name: str = "social"
    
    def observe(
        self,
        tick: int,
        state: "WorldState",
        agents: List["Citizen"]
    ) -> Dict:
        """Observe social network metrics."""
        if not agents:
            return {}
        
        # Collect network data
        total_connections = 0
        connection_counts = []
        isolated = 0
        
        for agent in agents:
            num_connections = agent.social.network_size
            connection_counts.append(num_connections)
            total_connections += num_connections
            
            if num_connections == 0:
                isolated += 1
        
        # Basic statistics
        avg_connections = sum(connection_counts) / len(agents)
        max_connections = max(connection_counts) if connection_counts else 0
        min_connections = min(connection_counts) if connection_counts else 0
        
        # Network density (actual / possible connections)
        max_possible = len(agents) * (len(agents) - 1)  # Directed graph
        density = total_connections / max_possible if max_possible > 0 else 0.0
        
        # Isolation rate
        isolation_rate = isolated / len(agents)
        
        # Average tie strength
        total_strength = sum(
            agent.social.average_tie_strength
            for agent in agents
        )
        avg_tie_strength = total_strength / len(agents)
        
        # Total social capital
        total_social_capital = sum(
            agent.social.get_social_capital()
            for agent in agents
        )
        avg_social_capital = total_social_capital / len(agents)
        
        # Strong ties count (strength > 0.7)
        strong_ties = sum(
            len(agent.social.get_strong_ties())
            for agent in agents
        )
        
        metrics = {
            "total_connections": total_connections,
            "avg_connections": avg_connections,
            "max_connections": max_connections,
            "min_connections": min_connections,
            "network_density": density,
            "isolated_count": isolated,
            "isolation_rate": isolation_rate,
            "avg_tie_strength": avg_tie_strength,
            "avg_social_capital": avg_social_capital,
            "strong_ties_count": strong_ties,
        }
        
        self._record(tick, metrics)
        
        # Update aggregated results
        self.results = {
            "mean_density": self.calculate_mean("network_density"),
            "density_trend": self.calculate_trend("network_density"),
            "current_density": density,
            "mean_isolation_rate": self.calculate_mean("isolation_rate"),
            "current_isolation_rate": isolation_rate,
        }
        
        return metrics
