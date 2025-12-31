"""
Memory System - How citizens remember and recall experiences.

Citizens have:
- Episodic Memory: Specific events and experiences
- Semantic Memory: Facts about people, places, and things
- Working Memory: Currently active thoughts and goals

Memories decay over time but can be reinforced through recall.
Important or emotional memories last longer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set
import math
import random


class MemoryType(Enum):
    """Types of memories."""
    EPISODIC = auto()    # Events: "I met John at the park"
    SEMANTIC = auto()    # Facts: "John works at the bank"
    EMOTIONAL = auto()   # Feelings: "I felt happy when..."
    PROCEDURAL = auto()  # Skills: "How to cook pasta"


class MemoryTag(Enum):
    """Tags for categorizing memories."""
    SOCIAL = auto()
    WORK = auto()
    FAMILY = auto()
    ROMANTIC = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    IMPORTANT = auto()
    MUNDANE = auto()
    LOCATION = auto()
    PERSON = auto()


@dataclass
class Memory:
    """
    A single memory unit.
    
    Attributes:
        id: Unique memory identifier
        memory_type: Type of memory (episodic, semantic, etc.)
        content: The memory content/description
        timestamp: When the memory was formed
        importance: How important this memory is (0-1)
        emotional_valence: Positive or negative (-1 to 1)
        emotional_intensity: How emotionally charged (0-1)
        tags: Categories this memory belongs to
        related_entities: People, places, things involved
        strength: Current memory strength (decays over time)
        access_count: How many times this memory was recalled
        last_accessed: When this memory was last recalled
    """
    
    content: str
    memory_type: MemoryType
    
    id: str = field(default_factory=lambda: f"mem_{random.randint(100000, 999999)}")
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    emotional_valence: float = 0.0  # -1 (negative) to 1 (positive)
    emotional_intensity: float = 0.0  # 0 to 1
    tags: Set[MemoryTag] = field(default_factory=set)
    related_entities: Dict[str, str] = field(default_factory=dict)  # id -> type (person, place, etc.)
    strength: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def recall(self) -> None:
        """Recall this memory, strengthening it."""
        self.access_count += 1
        self.last_accessed = datetime.now()
        # Recalling strengthens the memory
        self.strength = min(1.0, self.strength + 0.1)
    
    def decay(self, time_passed_hours: float) -> None:
        """Apply time-based decay to memory strength."""
        # Important and emotional memories decay slower
        decay_rate = 0.01 * (1 - self.importance * 0.5) * (1 - self.emotional_intensity * 0.3)
        self.strength = max(0.0, self.strength - decay_rate * time_passed_hours)
    
    @property
    def is_positive(self) -> bool:
        """Check if this is a positive memory."""
        return self.emotional_valence > 0.2
    
    @property
    def is_negative(self) -> bool:
        """Check if this is a negative memory."""
        return self.emotional_valence < -0.2
    
    @property
    def is_forgotten(self) -> bool:
        """Check if memory has decayed too much."""
        return self.strength < 0.1
    
    def get_recall_probability(self) -> float:
        """Calculate probability of spontaneous recall."""
        # Based on strength, importance, recency
        recency_factor = 1.0
        if self.last_accessed:
            hours_since = (datetime.now() - self.last_accessed).total_seconds() / 3600
            recency_factor = math.exp(-hours_since / 24)  # Decay over 24 hours
        
        return self.strength * 0.4 + self.importance * 0.3 + recency_factor * 0.3


@dataclass
class MemorySystem:
    """
    Complete memory system for a citizen.
    
    Manages storage, retrieval, and decay of memories.
    """
    
    # Memory storage
    memories: List[Memory] = field(default_factory=list)
    
    # Semantic knowledge about entities
    entity_knowledge: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Working memory (current focus)
    working_memory: List[str] = field(default_factory=list)  # Memory IDs
    working_memory_capacity: int = 7  # Miller's Law
    
    # Configuration
    max_memories: int = 1000
    decay_rate: float = 0.01
    
    def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        emotional_intensity: float = 0.0,
        tags: Optional[Set[MemoryTag]] = None,
        related_entities: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Add a new memory.
        
        Args:
            content: What happened/what is remembered
            memory_type: Type of memory
            importance: How important (0-1)
            emotional_valence: Positive or negative (-1 to 1)
            emotional_intensity: How emotional (0-1)
            tags: Memory categories
            related_entities: People, places, things involved
            context: Additional context
            
        Returns:
            The created Memory
        """
        memory = Memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional_valence,
            emotional_intensity=emotional_intensity,
            tags=tags or set(),
            related_entities=related_entities or {},
            context=context or {},
        )
        
        self.memories.append(memory)
        
        # Prune if too many memories
        if len(self.memories) > self.max_memories:
            self._prune_memories()
        
        return memory
    
    def remember_event(
        self,
        what: str,
        who: Optional[List[str]] = None,
        where: Optional[str] = None,
        emotion: str = "neutral",
        importance: float = 0.5,
    ) -> Memory:
        """
        Convenience method to remember an event.
        
        Args:
            what: What happened
            who: People involved (IDs)
            where: Location
            emotion: Emotional response
            importance: How important
            
        Returns:
            The created Memory
        """
        # Determine emotional valence from emotion string
        emotion_map = {
            "happy": (0.7, 0.6),
            "joy": (0.9, 0.8),
            "love": (0.9, 0.9),
            "excited": (0.6, 0.7),
            "content": (0.4, 0.3),
            "neutral": (0.0, 0.1),
            "sad": (-0.6, 0.6),
            "angry": (-0.7, 0.8),
            "fear": (-0.5, 0.7),
            "disgust": (-0.6, 0.5),
            "anxious": (-0.4, 0.6),
            "lonely": (-0.5, 0.5),
        }
        valence, intensity = emotion_map.get(emotion, (0.0, 0.1))
        
        # Build related entities
        entities = {}
        if who:
            for person_id in who:
                entities[person_id] = "person"
        if where:
            entities[where] = "location"
        
        # Determine tags
        tags = set()
        if valence > 0:
            tags.add(MemoryTag.POSITIVE)
        elif valence < 0:
            tags.add(MemoryTag.NEGATIVE)
        if importance > 0.7:
            tags.add(MemoryTag.IMPORTANT)
        if who:
            tags.add(MemoryTag.SOCIAL)
            tags.add(MemoryTag.PERSON)
        if where:
            tags.add(MemoryTag.LOCATION)
        
        return self.add_memory(
            content=what,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            emotional_valence=valence,
            emotional_intensity=intensity,
            tags=tags,
            related_entities=entities,
        )
    
    def learn_fact(
        self,
        about_entity: str,
        entity_type: str,
        fact_key: str,
        fact_value: Any,
    ) -> None:
        """
        Learn a semantic fact about an entity.
        
        Args:
            about_entity: ID of the entity
            entity_type: Type (person, place, etc.)
            fact_key: What aspect (e.g., "works_at", "likes")
            fact_value: The value
        """
        if about_entity not in self.entity_knowledge:
            self.entity_knowledge[about_entity] = {"type": entity_type}
        
        self.entity_knowledge[about_entity][fact_key] = fact_value
        
        # Also create a semantic memory
        self.add_memory(
            content=f"{about_entity} {fact_key}: {fact_value}",
            memory_type=MemoryType.SEMANTIC,
            importance=0.3,
            related_entities={about_entity: entity_type},
        )
    
    def get_knowledge(self, entity_id: str) -> Dict[str, Any]:
        """Get all known facts about an entity."""
        return self.entity_knowledge.get(entity_id, {})
    
    def recall_about(
        self,
        entity_id: str,
        limit: int = 10,
    ) -> List[Memory]:
        """
        Recall memories related to an entity.
        
        Args:
            entity_id: ID of person, place, or thing
            limit: Maximum memories to return
            
        Returns:
            List of relevant memories, sorted by strength
        """
        relevant = [
            m for m in self.memories
            if entity_id in m.related_entities and not m.is_forgotten
        ]
        
        # Sort by strength and importance
        relevant.sort(key=lambda m: m.strength * m.importance, reverse=True)
        
        # Recall strengthens memories
        for m in relevant[:limit]:
            m.recall()
        
        return relevant[:limit]
    
    def recall_by_tag(
        self,
        tag: MemoryTag,
        limit: int = 10,
    ) -> List[Memory]:
        """Recall memories with a specific tag."""
        relevant = [
            m for m in self.memories
            if tag in m.tags and not m.is_forgotten
        ]
        relevant.sort(key=lambda m: m.strength, reverse=True)
        
        for m in relevant[:limit]:
            m.recall()
        
        return relevant[:limit]
    
    def recall_recent(self, limit: int = 10) -> List[Memory]:
        """Recall recent memories."""
        recent = sorted(
            [m for m in self.memories if not m.is_forgotten],
            key=lambda m: m.timestamp,
            reverse=True,
        )
        return recent[:limit]
    
    def recall_emotional(
        self,
        positive: bool = True,
        limit: int = 10,
    ) -> List[Memory]:
        """Recall emotionally charged memories."""
        emotional = [
            m for m in self.memories
            if not m.is_forgotten and m.emotional_intensity > 0.3
            and ((positive and m.is_positive) or (not positive and m.is_negative))
        ]
        emotional.sort(key=lambda m: m.emotional_intensity, reverse=True)
        return emotional[:limit]
    
    def get_impression_of(self, person_id: str) -> Dict[str, Any]:
        """
        Get overall impression of a person based on memories.
        
        Returns:
            Dict with relationship assessment
        """
        memories = self.recall_about(person_id)
        knowledge = self.get_knowledge(person_id)
        
        if not memories and not knowledge:
            return {"known": False}
        
        # Calculate average emotional experience
        if memories:
            avg_valence = sum(m.emotional_valence for m in memories) / len(memories)
            avg_intensity = sum(m.emotional_intensity for m in memories) / len(memories)
            memory_count = len(memories)
        else:
            avg_valence = 0
            avg_intensity = 0
            memory_count = 0
        
        # Determine impression
        if avg_valence > 0.5:
            impression = "positive"
        elif avg_valence > 0.2:
            impression = "friendly"
        elif avg_valence < -0.5:
            impression = "negative"
        elif avg_valence < -0.2:
            impression = "unfriendly"
        else:
            impression = "neutral"
        
        return {
            "known": True,
            "impression": impression,
            "average_valence": avg_valence,
            "emotional_intensity": avg_intensity,
            "memory_count": memory_count,
            "knowledge": knowledge,
        }
    
    def update(self, time_passed_hours: float = 1.0) -> None:
        """
        Update memory system (apply decay).
        
        Args:
            time_passed_hours: How much time has passed
        """
        for memory in self.memories:
            memory.decay(time_passed_hours)
        
        # Remove completely forgotten memories
        self.memories = [m for m in self.memories if not m.is_forgotten]
    
    def _prune_memories(self) -> None:
        """Remove weakest memories when over capacity."""
        # Keep important and recent memories
        self.memories.sort(
            key=lambda m: m.strength * 0.4 + m.importance * 0.4 + m.emotional_intensity * 0.2,
            reverse=True,
        )
        self.memories = self.memories[:self.max_memories]
    
    def get_working_memory(self) -> List[Memory]:
        """Get memories currently in working memory."""
        return [
            m for m in self.memories
            if m.id in self.working_memory
        ]
    
    def focus_on(self, memory_id: str) -> None:
        """Bring a memory into working memory."""
        if memory_id not in self.working_memory:
            self.working_memory.append(memory_id)
            if len(self.working_memory) > self.working_memory_capacity:
                self.working_memory.pop(0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of memory system state."""
        return {
            "total_memories": len(self.memories),
            "episodic": len([m for m in self.memories if m.memory_type == MemoryType.EPISODIC]),
            "semantic": len([m for m in self.memories if m.memory_type == MemoryType.SEMANTIC]),
            "known_entities": len(self.entity_knowledge),
            "positive_memories": len([m for m in self.memories if m.is_positive]),
            "negative_memories": len([m for m in self.memories if m.is_negative]),
            "average_strength": sum(m.strength for m in self.memories) / len(self.memories) if self.memories else 0,
        }
