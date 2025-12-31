"""
Multi-agent system for autonomous citizen simulation.

Provides event-driven, concurrent agent execution where each
citizen operates independently and can interact with others.
"""

from urbanium.multiagent.messaging import MessageBus, Message, MessageType
from urbanium.multiagent.runner import AgentRunner, AgentState
from urbanium.multiagent.interactions import (
    Interaction,
    InteractionType,
    InteractionManager,
)
from urbanium.multiagent.coordinator import (
    SimulationCoordinator,
    SimulationConfig,
    run_multiagent_simulation,
)

__all__ = [
    "MessageBus",
    "Message", 
    "MessageType",
    "AgentRunner",
    "AgentState",
    "Interaction",
    "InteractionType",
    "InteractionManager",
    "SimulationCoordinator",
    "SimulationConfig",
    "run_multiagent_simulation",
]
