"""
AI Decision Model - LLM-based decision making for agents.

Integrates with the existing decision model system to provide
AI-powered decision making with structured output.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging
import time

from urbanium.agents.decision import DecisionModel, DecisionStrategy
from urbanium.ai.client import AIClient, AIConfig
from urbanium.ai.prompts import PromptBuilder
from urbanium.ai.schemas import DecisionOutput, ActionChoice

if TYPE_CHECKING:
    from urbanium.agents.citizen import Citizen
    from urbanium.actions.base import Action

logger = logging.getLogger(__name__)


@dataclass
class AIDecisionModel(DecisionModel):
    """
    AI-powered decision model using LLM.
    
    Uses an OpenAI-compatible API to make decisions based on
    agent state, with structured output for reliability.
    
    Falls back to utility-based decisions if AI fails.
    """
    
    strategy: DecisionStrategy = DecisionStrategy.UTILITY  # Fallback
    
    # AI components
    ai_client: Optional[AIClient] = None
    prompt_builder: PromptBuilder = field(default_factory=PromptBuilder)
    
    # Configuration
    use_ai: bool = True
    fallback_on_error: bool = True
    log_decisions: bool = True
    
    # Cache for determinism (same state = same decision)
    decision_cache: Dict[str, DecisionOutput] = field(default_factory=dict)
    use_cache: bool = False  # Disable for more dynamic behavior
    
    # Statistics
    ai_decisions: int = 0
    fallback_decisions: int = 0
    
    def __post_init__(self):
        """Initialize the decision model."""
        super().__post_init__()
        
        if self.ai_client is None and self.use_ai:
            try:
                self.ai_client = AIClient()
            except ImportError:
                logger.warning("OpenAI package not available, AI decisions disabled")
                self.use_ai = False
    
    @classmethod
    def create(
        cls,
        config: Optional[AIConfig] = None,
        fallback_on_error: bool = True,
    ) -> "AIDecisionModel":
        """
        Create an AI decision model with the given configuration.
        
        Args:
            config: AI client configuration
            fallback_on_error: Whether to fall back to utility on errors
            
        Returns:
            Configured AIDecisionModel
        """
        try:
            client = AIClient(config) if config else AIClient()
            return cls(
                ai_client=client,
                use_ai=True,
                fallback_on_error=fallback_on_error,
            )
        except ImportError:
            logger.warning("Creating non-AI decision model (openai not installed)")
            return cls(use_ai=False)
    
    def select_action(
        self,
        citizen: "Citizen",
        local_state: Dict,
        available_actions: List["Action"],
    ) -> Optional["Action"]:
        """
        Select an action using AI or fallback.
        
        Args:
            citizen: The citizen making the decision
            local_state: The local world state
            available_actions: List of valid actions
            
        Returns:
            The selected action, or None
        """
        if not available_actions:
            return None
        
        # Try AI decision
        if self.use_ai and self.ai_client:
            try:
                return self._select_by_ai(citizen, local_state, available_actions)
            except Exception as e:
                logger.error(f"AI decision failed: {e}")
                self.fallback_decisions += 1
                
                if not self.fallback_on_error:
                    raise
        
        # Fallback to parent's utility-based selection
        return super().select_action(citizen, local_state, available_actions)
    
    def _select_by_ai(
        self,
        citizen: "Citizen",
        local_state: Dict,
        available_actions: List["Action"],
    ) -> Optional["Action"]:
        """
        Select action using AI with structured output.
        """
        start_time = time.monotonic()
        # Check cache
        if self.use_cache:
            cache_key = self._get_cache_key(citizen, local_state)
            if cache_key in self.decision_cache:
                cached = self.decision_cache[cache_key]
                return self._get_action_by_choice(cached.chosen_action, available_actions)
        
        # Build prompt
        prompt = self.prompt_builder.build_decision_prompt(
            citizen,
            local_state,
            available_actions,
        )
        system_prompt = self.prompt_builder.get_system_prompt()
        
        # Get structured response
        decision = self.ai_client.generate_structured(
            prompt=prompt,
            response_model=DecisionOutput,
            system_prompt=system_prompt,
        )

        # Hard timeout guard to prevent getting stuck if the provider hangs
        elapsed = time.monotonic() - start_time
        if elapsed > (self.ai_client.config.timeout * 1.5):
            raise TimeoutError(
                f"AI decision exceeded timeout ({elapsed:.1f}s > {self.ai_client.config.timeout * 1.5:.1f}s)"
            )
        
        # Log decision
        if self.log_decisions:
            logger.info(
                f"AI Decision for {citizen.name}: {decision.chosen_action.value} "
                f"(confidence: {decision.confidence:.2f})"
            )
            logger.debug(f"Reasoning: {decision.explanation}")
        
        # Cache if enabled
        if self.use_cache:
            self.decision_cache[cache_key] = decision
        
        # Store decision on citizen for explainability
        citizen.action_history.append({
            "tick": local_state.get("time", 0),
            "ai_decision": {
                "action": decision.chosen_action.value,
                "confidence": decision.confidence,
                "reasoning": decision.explanation,
                "assessment": decision.current_assessment,
            }
        })
        
        self.ai_decisions += 1
        
        # Map choice to action
        return self._get_action_by_choice(decision.chosen_action, available_actions)
    
    def _get_action_by_choice(
        self,
        choice: ActionChoice,
        available_actions: List["Action"],
    ) -> Optional["Action"]:
        """Map an ActionChoice to an actual Action object."""
        if choice == ActionChoice.NONE:
            return None
        
        for action in available_actions:
            if action.action_type.value == choice.value:
                return action
        
        # If chosen action not available, return first available
        logger.warning(f"Chosen action {choice.value} not available, using fallback")
        return available_actions[0] if available_actions else None
    
    def _get_cache_key(self, citizen: "Citizen", local_state: Dict) -> str:
        """Generate a cache key from citizen state."""
        # Include key state elements for caching
        needs = tuple(sorted(citizen.needs.get_all().items()))
        resources = (
            round(citizen.resources.money, 0),
            round(citizen.resources.energy, 0),
        )
        time = local_state.get("time", 0)
        
        return f"{citizen.id}:{needs}:{resources}:{time}"
    
    def get_statistics(self) -> Dict:
        """Get decision statistics."""
        total = self.ai_decisions + self.fallback_decisions
        return {
            "total_decisions": total,
            "ai_decisions": self.ai_decisions,
            "fallback_decisions": self.fallback_decisions,
            "ai_rate": self.ai_decisions / total if total > 0 else 0,
        }


def create_ai_decision_model(
    base_url: str = "http://localhost:1234/v1",
    api_key: str = "lm-studio",
    model: str = "local-model",
    temperature: float = 0.1,
) -> AIDecisionModel:
    """
    Convenience function to create an AI decision model.
    
    Args:
        base_url: API endpoint URL
        api_key: API key
        model: Model name
        temperature: Sampling temperature
        
    Returns:
        Configured AIDecisionModel
    """
    config = AIConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
    )
    return AIDecisionModel.create(config)
