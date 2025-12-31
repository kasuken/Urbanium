"""
Scenarios module - Initial conditions and experiments.

Scenarios define:
- Initial world state
- Population parameters
- Geographic structure
- Economic conditions
- Experiment configurations
"""

from urbanium.scenarios.base import Scenario
from urbanium.scenarios.simple_city import SimpleCityScenario

__all__ = [
    "Scenario",
    "SimpleCityScenario",
]
