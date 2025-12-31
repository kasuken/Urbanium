"""
MetricsObserver - Base class for metrics observers.

Observers collect metrics at each tick without modifying state.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from urbanium.engine.state import WorldState
    from urbanium.agents.citizen import Citizen


@dataclass
class MetricsObserver(ABC):
    """
    Base class for metrics observers.
    
    Observers are called at the end of each tick to record metrics.
    They should never modify world or agent state.
    """
    
    name: str = "base_observer"
    
    # Historical data
    history: List[Dict] = field(default_factory=list)
    
    # Aggregated results
    results: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def observe(
        self,
        tick: int,
        state: "WorldState",
        agents: List["Citizen"]
    ) -> Dict:
        """
        Observe the current state and record metrics.
        
        Args:
            tick: The current tick number
            state: The world state snapshot
            agents: List of all agents
            
        Returns:
            Dict of metrics collected this tick
        """
        pass
    
    def get_results(self) -> Dict:
        """Get aggregated results."""
        return self.results
    
    def get_history(self) -> List[Dict]:
        """Get full historical data."""
        return self.history
    
    def get_latest(self) -> Dict:
        """Get the most recent observation."""
        return self.history[-1] if self.history else {}
    
    def reset(self) -> None:
        """Reset the observer."""
        self.history = []
        self.results = {}
    
    def _record(self, tick: int, metrics: Dict) -> None:
        """Record metrics for a tick."""
        self.history.append({
            "tick": tick,
            **metrics
        })
    
    def calculate_mean(self, key: str) -> float:
        """Calculate the mean of a metric over history."""
        values = [h.get(key) for h in self.history if key in h]
        return sum(values) / len(values) if values else 0.0
    
    def calculate_trend(self, key: str, window: int = 10) -> float:
        """Calculate the trend (change) of a metric."""
        if len(self.history) < window:
            return 0.0
        
        recent = [h.get(key, 0) for h in self.history[-window:]]
        older = [h.get(key, 0) for h in self.history[-2*window:-window]]
        
        if not older:
            return 0.0
        
        return (sum(recent) / len(recent)) - (sum(older) / len(older))
