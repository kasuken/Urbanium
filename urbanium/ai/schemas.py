"""
Structured output schemas for AI decision making.

Uses Pydantic models to define and validate AI responses.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ActionChoice(str, Enum):
    """Available actions that can be chosen."""
    WORK_SHIFT = "work_shift"
    REST = "rest"
    EAT = "eat"
    COMMUTE = "commute"
    SOCIALIZE = "socialize"
    JOB_SEARCH = "job_search"
    HOUSING_CHANGE = "housing_change"
    NONE = "none"  # Skip this tick


class ReasoningStep(BaseModel):
    """A single step in the agent's reasoning process."""
    observation: str = Field(description="What the agent observes about their situation")
    consideration: str = Field(description="What factor or need is being considered")
    weight: float = Field(ge=0.0, le=1.0, description="Importance of this consideration (0-1)")


class DecisionOutput(BaseModel):
    """
    Structured output for agent decision making.
    
    This schema ensures AI responses are parseable and include
    the reasoning process for explainability.
    """
    
    # Reasoning (for explainability)
    current_assessment: str = Field(
        description="Brief assessment of the agent's current situation"
    )
    reasoning_steps: List[ReasoningStep] = Field(
        description="Step-by-step reasoning process",
        min_length=1,
        max_length=5,
    )
    
    # Decision
    chosen_action: ActionChoice = Field(
        description="The action the agent decides to take"
    )
    action_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional parameters for the chosen action"
    )
    
    # Confidence and alternatives
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in this decision (0-1)"
    )
    alternative_action: Optional[ActionChoice] = Field(
        default=None,
        description="Second-best action if primary fails"
    )
    
    # Explanation
    explanation: str = Field(
        description="Human-readable explanation of why this action was chosen"
    )


class NeedPriority(BaseModel):
    """Priority assessment for a specific need."""
    need_type: str = Field(description="Type of need (food, rest, social, etc.)")
    urgency: float = Field(ge=0.0, le=1.0, description="How urgent this need is (0-1)")
    satisfaction_level: float = Field(ge=0.0, le=1.0, description="Current satisfaction (0-1)")


class SituationAnalysis(BaseModel):
    """
    Detailed situation analysis before decision making.
    
    Used for complex scenarios requiring deeper analysis.
    """
    
    # Current state assessment
    overall_wellbeing: float = Field(
        ge=0.0, le=1.0,
        description="Overall wellbeing score (0-1)"
    )
    immediate_concerns: List[str] = Field(
        description="List of immediate concerns or needs",
        max_length=5,
    )
    need_priorities: List[NeedPriority] = Field(
        description="Prioritized list of needs",
        max_length=6,
    )
    
    # Resource assessment
    financial_status: str = Field(
        description="Assessment of financial situation (critical/low/stable/good)"
    )
    energy_status: str = Field(
        description="Assessment of energy level (exhausted/tired/normal/energized)"
    )
    
    # Context
    time_of_day: str = Field(description="Current time period")
    available_actions: List[ActionChoice] = Field(
        description="Actions available given current constraints"
    )
    
    # Recommendations
    recommended_action: ActionChoice = Field(
        description="Recommended action based on analysis"
    )
    reasoning: str = Field(
        description="Explanation of recommendation"
    )


class LongTermGoal(BaseModel):
    """A long-term goal for the agent."""
    goal: str = Field(description="Description of the goal")
    priority: float = Field(ge=0.0, le=1.0, description="Priority of this goal (0-1)")
    progress: float = Field(ge=0.0, le=1.0, description="Progress toward goal (0-1)")


class AgentPlan(BaseModel):
    """
    Multi-step plan for achieving goals.
    
    Used for GOAP-style planning with AI.
    """
    
    # Goals
    current_goals: List[LongTermGoal] = Field(
        description="Current active goals",
        max_length=3,
    )
    
    # Immediate plan
    next_actions: List[ActionChoice] = Field(
        description="Planned sequence of next actions",
        min_length=1,
        max_length=5,
    )
    
    # Reasoning
    plan_reasoning: str = Field(
        description="Why this sequence of actions was chosen"
    )
    expected_outcome: str = Field(
        description="What the agent expects to achieve"
    )
    
    # Contingency
    if_plan_fails: str = Field(
        description="What to do if the plan doesn't work"
    )
