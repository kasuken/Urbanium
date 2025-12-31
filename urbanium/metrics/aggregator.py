"""
MetricsAggregator - Aggregate metrics from multiple observers.

Provides unified access to all metrics and supports
multi-run analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import json

from urbanium.metrics.observer import MetricsObserver

if TYPE_CHECKING:
    from urbanium.engine.state import WorldState
    from urbanium.agents.citizen import Citizen


@dataclass
class RunResult:
    """Results from a single simulation run."""
    run_id: int
    seed: int
    total_ticks: int
    metrics: Dict[str, Any]
    history: Dict[str, List[Dict]]


@dataclass
class MetricsAggregator:
    """
    Aggregates metrics from multiple observers and runs.
    
    Supports:
    - Collecting from multiple observers
    - Storing results from multiple runs
    - Cross-run analysis
    - Export to various formats
    """
    
    observers: List[MetricsObserver] = field(default_factory=list)
    runs: List[RunResult] = field(default_factory=list)
    current_run_id: int = 0
    
    def add_observer(self, observer: MetricsObserver) -> None:
        """Add an observer to the aggregator."""
        self.observers.append(observer)
    
    def observe_all(
        self,
        tick: int,
        state: "WorldState",
        agents: List["Citizen"]
    ) -> Dict[str, Dict]:
        """Have all observers observe the current state."""
        results = {}
        for observer in self.observers:
            results[observer.name] = observer.observe(tick, state, agents)
        return results
    
    def get_current_metrics(self) -> Dict[str, Dict]:
        """Get current metrics from all observers."""
        return {
            observer.name: observer.get_results()
            for observer in self.observers
        }
    
    def finalize_run(self, seed: int, total_ticks: int) -> RunResult:
        """Finalize the current run and store results."""
        result = RunResult(
            run_id=self.current_run_id,
            seed=seed,
            total_ticks=total_ticks,
            metrics=self.get_current_metrics(),
            history={
                observer.name: observer.get_history()
                for observer in self.observers
            }
        )
        
        self.runs.append(result)
        self.current_run_id += 1
        
        return result
    
    def reset_observers(self) -> None:
        """Reset all observers for a new run."""
        for observer in self.observers:
            observer.reset()
    
    def get_run(self, run_id: int) -> Optional[RunResult]:
        """Get results from a specific run."""
        for run in self.runs:
            if run.run_id == run_id:
                return run
        return None
    
    def get_cross_run_stats(self, metric_path: str) -> Dict:
        """
        Get statistics for a metric across all runs.
        
        Args:
            metric_path: Path to metric, e.g., "employment.mean_employment_rate"
        """
        values = []
        
        for run in self.runs:
            parts = metric_path.split(".")
            value = run.metrics
            
            try:
                for part in parts:
                    value = value[part]
                values.append(value)
            except (KeyError, TypeError):
                continue
        
        if not values:
            return {"error": "No values found"}
        
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "std": self._std(values),
            "values": values,
        }
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def export_to_dict(self) -> Dict:
        """Export all results to a dictionary."""
        return {
            "runs": [
                {
                    "run_id": run.run_id,
                    "seed": run.seed,
                    "total_ticks": run.total_ticks,
                    "metrics": run.metrics,
                }
                for run in self.runs
            ]
        }
    
    def export_to_json(self, filepath: str) -> None:
        """Export all results to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.export_to_dict(), f, indent=2)
    
    def summary(self) -> str:
        """Generate a text summary of all runs."""
        lines = [
            f"Urbanium Metrics Summary",
            f"========================",
            f"Total runs: {len(self.runs)}",
            "",
        ]
        
        if self.runs:
            # Get key metrics from latest run
            latest = self.runs[-1]
            lines.append(f"Latest run (seed={latest.seed}, ticks={latest.total_ticks}):")
            
            for observer_name, metrics in latest.metrics.items():
                lines.append(f"  {observer_name}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        lines.append(f"    {key}: {value:.4f}")
                    else:
                        lines.append(f"    {key}: {value}")
        
        return "\n".join(lines)
