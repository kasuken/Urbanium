"""
Agent runner for autonomous agent execution.

Each agent runs in its own async task, making decisions and 
interacting independently.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, TYPE_CHECKING, Callable
import logging
import random

from urbanium.multiagent.messaging import MessageBus, Message, MessageType
from urbanium.multiagent.interactions import (
    InteractionManager,
    InteractionType,
    Interaction,
)

if TYPE_CHECKING:
    from urbanium.agents.citizen import Citizen
    from urbanium.engine.world import World
    from urbanium.ai.decision import AIDecisionModel

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """States an agent can be in."""
    
    IDLE = auto()           # Doing nothing, ready for action
    THINKING = auto()       # Making a decision
    ACTING = auto()         # Executing an action
    INTERACTING = auto()    # In an interaction with another agent
    WAITING = auto()        # Waiting for something
    RESTING = auto()        # Sleeping/resting
    BUSY = auto()           # Otherwise occupied


@dataclass
class AgentContext:
    """
    Runtime context for an agent.
    
    Contains everything an agent needs to operate autonomously.
    """
    
    citizen: "Citizen"
    world: "World"
    message_bus: MessageBus
    interaction_manager: InteractionManager
    
    # Optional AI decision model
    ai_model: Optional["AIDecisionModel"] = None
    
    # Agent's message inbox
    inbox: Optional[asyncio.Queue] = None
    
    # Current state
    state: AgentState = AgentState.IDLE
    current_interaction: Optional[Interaction] = None
    
    # Timing
    last_action_time: datetime = field(default_factory=datetime.now)
    last_decision_time: datetime = field(default_factory=datetime.now)
    
    # Configuration
    think_interval: float = 1.0      # Seconds between decisions
    action_interval: float = 0.5     # Minimum seconds between actions
    social_probability: float = 0.3  # Chance to initiate social interaction


class AgentRunner:
    """
    Runs an agent autonomously in an async task.
    
    The agent:
    1. Processes incoming messages
    2. Makes decisions based on current state
    3. Executes actions
    4. Initiates interactions with nearby agents
    """
    
    def __init__(
        self,
        context: AgentContext,
        on_action: Optional[Callable] = None,
        on_interaction: Optional[Callable] = None,
    ):
        """
        Initialize the agent runner.
        
        Args:
            context: Agent context with all dependencies
            on_action: Callback when agent takes an action
            on_interaction: Callback when agent interacts
        """
        self.context = context
        self.on_action = on_action
        self.on_interaction = on_interaction
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Statistics
        self.actions_taken: int = 0
        self.messages_processed: int = 0
        self.interactions_initiated: int = 0
    
    @property
    def citizen(self) -> "Citizen":
        """Get the citizen this runner controls."""
        return self.context.citizen
    
    @property
    def agent_id(self) -> str:
        """Get the agent's ID."""
        return self.context.citizen.id
    
    async def start(self):
        """Start the agent's autonomous loop."""
        if self._running:
            return
        
        # Register with message bus
        self.context.inbox = await self.context.message_bus.register_agent(
            self.agent_id
        )
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        
        logger.info(f"Agent {self.citizen.name} started")
    
    async def stop(self):
        """Stop the agent's autonomous loop."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.context.message_bus.unregister_agent(self.agent_id)
        logger.info(f"Agent {self.citizen.name} stopped")
    
    async def _run_loop(self):
        """Main agent loop."""
        while self._running:
            try:
                # Process any pending messages
                await self._process_messages()
                
                # If not busy, think and maybe act
                if self.context.state in (AgentState.IDLE, AgentState.WAITING):
                    await self._think_and_act()
                
                # Maybe initiate social interaction
                if self.context.state == AgentState.IDLE:
                    await self._maybe_interact()
                
                # Small delay to prevent spinning
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Agent {self.agent_id} error: {e}")
                await asyncio.sleep(1.0)  # Back off on error
    
    async def _process_messages(self):
        """Process pending messages from inbox."""
        if not self.context.inbox:
            return
        
        # Process all available messages without blocking
        while not self.context.inbox.empty():
            try:
                message = self.context.inbox.get_nowait()
                await self._handle_message(message)
                self.messages_processed += 1
            except asyncio.QueueEmpty:
                break
    
    async def _handle_message(self, message: Message):
        """Handle a single message."""
        if message.is_expired():
            return
        
        logger.debug(
            f"Agent {self.citizen.name} received {message.message_type.name} "
            f"from {message.sender_id}"
        )
        
        # Handle different message types
        if message.message_type == MessageType.GREET:
            await self._respond_to_greeting(message)
        
        elif message.message_type == MessageType.CHAT:
            await self._respond_to_chat(message)
        
        elif message.message_type == MessageType.INVITE:
            await self._respond_to_invite(message)
        
        elif message.message_type == MessageType.TRADE_OFFER:
            await self._respond_to_trade(message)
        
        elif message.message_type == MessageType.MEET_REQUEST:
            await self._respond_to_meet_request(message)
    
    async def _respond_to_greeting(self, message: Message):
        """Respond to a greeting based on personality."""
        # More extraverted agents are more likely to respond warmly
        warmth = self.citizen.traits.extraversion * 0.5 + 0.5
        
        if random.random() < warmth:
            response = Message(
                sender_id=self.agent_id,
                receiver_id=message.sender_id,
                message_type=MessageType.GREET,
                content={
                    "response": "hello",
                    "mood": self.citizen.needs.get_overall_satisfaction(),
                },
            )
            await self.context.message_bus.send(response)
    
    async def _respond_to_chat(self, message: Message):
        """Respond to a chat message."""
        # Decide whether to continue conversation
        social_need = self.citizen.needs.social
        willingness = social_need * 0.5 + self.citizen.traits.agreeableness * 0.3
        
        if random.random() < willingness:
            # Continue conversation
            await self._start_conversation(message.sender_id)
    
    async def _respond_to_invite(self, message: Message):
        """Respond to an invitation."""
        # Check if we want to accept based on needs and personality
        social_need = self.citizen.needs.social
        openness = self.citizen.traits.openness
        
        accept_chance = social_need * 0.4 + openness * 0.3 + 0.2
        
        response_type = MessageType.ACCEPT if random.random() < accept_chance else MessageType.DECLINE
        
        response = Message(
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=response_type,
            content={"invite_id": message.content.get("invite_id")},
        )
        await self.context.message_bus.send(response)
    
    async def _respond_to_trade(self, message: Message):
        """Evaluate and respond to a trade offer."""
        offer = message.content
        
        # Simple evaluation - would this trade benefit us?
        benefit = offer.get("value_to_receiver", 0) - offer.get("cost_to_receiver", 0)
        
        if benefit > 0 or (benefit >= 0 and random.random() < 0.5):
            response_type = MessageType.TRADE_ACCEPT
        else:
            response_type = MessageType.TRADE_REJECT
        
        response = Message(
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=response_type,
            content={"trade_id": offer.get("trade_id")},
        )
        await self.context.message_bus.send(response)
    
    async def _respond_to_meet_request(self, message: Message):
        """Respond to a meeting request."""
        # Check if we're available
        if self.context.state != AgentState.IDLE:
            response_type = MessageType.DECLINE
        else:
            # Decide based on relationship and needs
            relationship = self.context.interaction_manager.get_relationship_score(
                self.agent_id, message.sender_id
            )
            accept_chance = 0.3 + relationship * 0.4 + self.citizen.needs.social * 0.3
            response_type = MessageType.ACCEPT if random.random() < accept_chance else MessageType.DECLINE
        
        response = Message(
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=response_type,
            content={"request_id": message.content.get("request_id")},
        )
        await self.context.message_bus.send(response)
    
    async def _think_and_act(self):
        """Make a decision and potentially take action."""
        now = datetime.now()
        
        # Check if enough time has passed since last decision
        elapsed = (now - self.context.last_decision_time).total_seconds()
        if elapsed < self.context.think_interval:
            return
        
        self.context.state = AgentState.THINKING
        self.context.last_decision_time = now
        
        try:
            # Get local state for decision making
            local_state = self._get_local_state()
            
            # Get available actions
            available_actions = self._get_available_actions()
            
            # Make decision (using AI if available)
            action = await self._decide_action(local_state, available_actions)
            
            if action:
                await self._execute_action(action, local_state)
            
        finally:
            self.context.state = AgentState.IDLE
    
    def _get_local_state(self) -> Dict:
        """Get the local world state visible to this agent."""
        world = self.context.world
        
        return {
            "time": world.state.current_tick if hasattr(world, 'state') else 0,
            "location": self.citizen.current_location,
            "nearby_agents": self._get_nearby_agents(),
            "economy": {
                "available_jobs": len(getattr(world, 'job_market', [])),
            },
        }
    
    def _get_nearby_agents(self) -> List[str]:
        """Get IDs of agents at the same location."""
        online = self.context.message_bus.get_online_agents()
        
        # For now, all online agents are "nearby" - can be refined with location
        return [aid for aid in online if aid != self.agent_id]
    
    def _get_available_actions(self) -> List:
        """Get actions available to this agent."""
        # Import here to avoid circular imports
        from urbanium.actions import get_all_actions
        
        all_actions = get_all_actions()
        return [a for a in all_actions if a.check_prerequisites(self.citizen, {})]
    
    async def _decide_action(self, local_state: Dict, available_actions: List) -> Optional[Any]:
        """Decide which action to take."""
        if not available_actions:
            return None
        
        # Use AI model if available
        if self.context.ai_model and self.context.ai_model.use_ai:
            try:
                # Run AI decision in thread pool to not block
                loop = asyncio.get_event_loop()
                action = await loop.run_in_executor(
                    None,
                    self.context.ai_model.select_action,
                    self.citizen,
                    local_state,
                    available_actions,
                )
                return action
            except Exception as e:
                logger.warning(f"AI decision failed: {e}, using fallback")
        
        # Fallback: use citizen's decision model
        if hasattr(self.citizen, 'decision_model') and self.citizen.decision_model:
            return self.citizen.decision_model.select_action(
                self.citizen, local_state, available_actions
            )
        
        # Last resort: random action
        return random.choice(available_actions) if available_actions else None
    
    async def _execute_action(self, action: Any, local_state: Dict):
        """Execute an action."""
        self.context.state = AgentState.ACTING
        
        try:
            # Execute the action
            result = action.execute(self.citizen, local_state)
            
            self.actions_taken += 1
            self.context.last_action_time = datetime.now()
            
            # Callback if provided
            if self.on_action:
                self.on_action(self.citizen, action, result)
            
            logger.debug(f"Agent {self.citizen.name} executed {action.action_type.name}")
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
        
        finally:
            self.context.state = AgentState.IDLE
    
    async def _maybe_interact(self):
        """Maybe initiate a social interaction."""
        # Check social need and personality
        social_need = 1.0 - self.citizen.needs.social  # Higher when need is low
        extraversion = self.citizen.traits.extraversion
        
        interact_chance = (
            self.context.social_probability *
            social_need * 0.5 +
            extraversion * 0.3
        )
        
        if random.random() > interact_chance:
            return
        
        # Find someone to interact with
        nearby = self._get_nearby_agents()
        if not nearby:
            return
        
        target_id = random.choice(nearby)
        
        # Check if we can interact
        if not self.context.interaction_manager.can_interact(
            self.agent_id, target_id, InteractionType.CONVERSATION
        ):
            return
        
        # Initiate interaction
        await self._start_conversation(target_id)
    
    async def _start_conversation(self, other_id: str):
        """Start a conversation with another agent."""
        self.context.state = AgentState.INTERACTING
        
        try:
            # Start the interaction
            interaction = self.context.interaction_manager.start_interaction(
                interaction_type=InteractionType.CONVERSATION,
                initiator_id=self.agent_id,
                participant_ids=[self.agent_id, other_id],
                context={
                    "initiator_mood": self.citizen.needs.get_overall_satisfaction(),
                    "topic": random.choice(["weather", "work", "local_news", "personal"]),
                },
            )
            
            self.context.current_interaction = interaction
            self.interactions_initiated += 1
            
            # Send greeting message
            greeting = Message(
                sender_id=self.agent_id,
                receiver_id=other_id,
                message_type=MessageType.GREET,
                content={
                    "interaction_id": interaction.id,
                    "greeting_type": "casual",
                },
                requires_response=True,
            )
            await self.context.message_bus.send(greeting)
            
            # Callback if provided
            if self.on_interaction:
                self.on_interaction(self.citizen, interaction)
            
            # Wait briefly for response, then complete
            await asyncio.sleep(0.5)
            
            # Complete interaction (in reality, would wait for response)
            self.context.interaction_manager.complete_interaction(
                interaction.id,
                outcome="completed",
                effects={
                    "social_boost": 0.05,
                },
            )
            
            # Apply social benefit
            self.citizen.needs.social = min(1.0, self.citizen.needs.social + 0.05)
            
        finally:
            self.context.state = AgentState.IDLE
            self.context.current_interaction = None
    
    def get_statistics(self) -> Dict:
        """Get agent statistics."""
        return {
            "agent_id": self.agent_id,
            "name": self.citizen.name,
            "state": self.context.state.name,
            "actions_taken": self.actions_taken,
            "messages_processed": self.messages_processed,
            "interactions_initiated": self.interactions_initiated,
        }
