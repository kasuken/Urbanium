"""
Metrics module - Observers and aggregations.

Urbanium tracks measurable outcomes such as:
- Employment rate
- Wage distribution
- Rent index
- Commute time
- Social network clustering
- Inequality (Gini)
- Agent churn and bankruptcy
- Housing pressure

Results are analyzed across multiple runs and random seeds.
"""

from urbanium.metrics.observer import MetricsObserver
from urbanium.metrics.employment import EmploymentObserver
from urbanium.metrics.economic import EconomicObserver
from urbanium.metrics.social import SocialObserver
from urbanium.metrics.aggregator import MetricsAggregator

__all__ = [
    "MetricsObserver",
    "EmploymentObserver",
    "EconomicObserver",
    "SocialObserver",
    "MetricsAggregator",
]
