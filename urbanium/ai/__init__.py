"""
AI module - LLM-based decision making for agents.

Supports OpenAI-compatible APIs (OpenAI, LM Studio, Ollama, etc.)
with structured output for reliable, parseable responses.
"""

from urbanium.ai.client import AIClient, AIConfig
from urbanium.ai.decision import AIDecisionModel
from urbanium.ai.prompts import PromptBuilder
from urbanium.ai.schemas import DecisionOutput, ActionChoice

__all__ = [
    "AIClient",
    "AIConfig",
    "AIDecisionModel",
    "PromptBuilder",
    "DecisionOutput",
    "ActionChoice",
]
