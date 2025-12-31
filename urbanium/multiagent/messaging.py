"""
Message bus for inter-agent communication.

Provides async message passing between autonomous agents.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Set
from collections import defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can send."""
    
    # Social interactions
    GREET = auto()
    CHAT = auto()
    INVITE = auto()
    ACCEPT = auto()
    DECLINE = auto()
    
    # Economic interactions
    TRADE_OFFER = auto()
    TRADE_ACCEPT = auto()
    TRADE_REJECT = auto()
    HIRE_OFFER = auto()
    SERVICE_REQUEST = auto()
    
    # Information sharing
    SHARE_INFO = auto()
    ASK_INFO = auto()
    GOSSIP = auto()
    
    # Coordination
    MEET_REQUEST = auto()
    LOCATION_UPDATE = auto()
    
    # System
    BROADCAST = auto()
    DIRECT = auto()
    ACK = auto()


@dataclass
class Message:
    """
    A message between agents.
    
    Attributes:
        id: Unique message identifier
        sender_id: ID of sending agent
        receiver_id: ID of receiving agent (None for broadcast)
        message_type: Type of message
        content: Message payload
        timestamp: When the message was sent
        requires_response: Whether sender expects a response
        expires_at: Optional expiration time
        metadata: Additional message metadata
    """
    
    sender_id: str
    message_type: MessageType
    content: Dict[str, Any]
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    receiver_id: Optional[str] = None  # None = broadcast
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_broadcast(self) -> bool:
        """Check if this is a broadcast message."""
        return self.receiver_id is None


class MessageBus:
    """
    Central message bus for agent communication.
    
    Supports:
    - Direct messages between agents
    - Broadcast messages to all agents
    - Topic-based subscriptions
    - Async message delivery
    """
    
    def __init__(self):
        """Initialize the message bus."""
        # Agent inboxes (agent_id -> queue of messages)
        self._inboxes: Dict[str, asyncio.Queue] = {}
        
        # Message handlers by type
        self._handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        
        # Subscriptions (topic -> set of agent_ids)
        self._subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # All registered agents
        self._agents: Set[str] = set()
        
        # Message history for debugging
        self._history: List[Message] = []
        self._max_history: int = 1000
        
        # Statistics
        self.messages_sent: int = 0
        self.messages_delivered: int = 0
        
        self._lock = asyncio.Lock()
    
    async def register_agent(self, agent_id: str) -> asyncio.Queue:
        """
        Register an agent with the message bus.
        
        Args:
            agent_id: Unique agent identifier
            
        Returns:
            The agent's message inbox queue
        """
        async with self._lock:
            if agent_id not in self._inboxes:
                self._inboxes[agent_id] = asyncio.Queue()
                self._agents.add(agent_id)
                logger.debug(f"Agent {agent_id} registered with message bus")
            return self._inboxes[agent_id]
    
    async def unregister_agent(self, agent_id: str):
        """Remove an agent from the message bus."""
        async with self._lock:
            self._inboxes.pop(agent_id, None)
            self._agents.discard(agent_id)
            
            # Remove from all subscriptions
            for subscribers in self._subscriptions.values():
                subscribers.discard(agent_id)
    
    async def send(self, message: Message) -> bool:
        """
        Send a message.
        
        Args:
            message: The message to send
            
        Returns:
            True if message was delivered
        """
        if message.is_expired():
            logger.debug(f"Message {message.id} expired before delivery")
            return False
        
        self.messages_sent += 1
        
        # Store in history
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        if message.is_broadcast():
            return await self._broadcast(message)
        else:
            return await self._direct_send(message)
    
    async def _direct_send(self, message: Message) -> bool:
        """Send a direct message to one agent."""
        if message.receiver_id not in self._inboxes:
            logger.warning(f"Agent {message.receiver_id} not found")
            return False
        
        await self._inboxes[message.receiver_id].put(message)
        self.messages_delivered += 1
        
        logger.debug(
            f"Message {message.message_type.name} from {message.sender_id} "
            f"to {message.receiver_id}"
        )
        return True
    
    async def _broadcast(self, message: Message) -> bool:
        """Broadcast message to all agents except sender."""
        delivered = 0
        
        for agent_id, inbox in self._inboxes.items():
            if agent_id != message.sender_id:
                await inbox.put(message)
                delivered += 1
        
        self.messages_delivered += delivered
        logger.debug(
            f"Broadcast {message.message_type.name} from {message.sender_id} "
            f"to {delivered} agents"
        )
        return delivered > 0
    
    async def send_to_nearby(
        self,
        message: Message,
        location: str,
        agent_locations: Dict[str, str],
    ) -> int:
        """
        Send message to agents at the same location.
        
        Args:
            message: The message to send
            location: The location to broadcast to
            agent_locations: Map of agent_id -> location
            
        Returns:
            Number of agents reached
        """
        delivered = 0
        
        for agent_id, agent_location in agent_locations.items():
            if agent_id != message.sender_id and agent_location == location:
                if agent_id in self._inboxes:
                    await self._inboxes[agent_id].put(message)
                    delivered += 1
        
        self.messages_delivered += delivered
        return delivered
    
    def subscribe(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic."""
        self._subscriptions[topic].add(agent_id)
    
    def unsubscribe(self, agent_id: str, topic: str):
        """Unsubscribe an agent from a topic."""
        self._subscriptions[topic].discard(agent_id)
    
    async def publish(self, topic: str, message: Message) -> int:
        """
        Publish a message to all subscribers of a topic.
        
        Returns:
            Number of subscribers reached
        """
        delivered = 0
        
        for agent_id in self._subscriptions.get(topic, set()):
            if agent_id in self._inboxes and agent_id != message.sender_id:
                await self._inboxes[agent_id].put(message)
                delivered += 1
        
        self.messages_delivered += delivered
        return delivered
    
    def get_online_agents(self) -> Set[str]:
        """Get set of all registered agent IDs."""
        return self._agents.copy()
    
    def get_statistics(self) -> Dict:
        """Get message bus statistics."""
        return {
            "registered_agents": len(self._agents),
            "messages_sent": self.messages_sent,
            "messages_delivered": self.messages_delivered,
            "topics": len(self._subscriptions),
            "history_size": len(self._history),
        }
