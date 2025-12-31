"""
Events - Scheduled and random events in the simulation.

Events can be scheduled or triggered by conditions, affecting
the world state and agent behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Any
from enum import Enum


class EventType(Enum):
    """Types of events."""
    ECONOMIC = "economic"
    WEATHER = "weather"
    SOCIAL = "social"
    INFRASTRUCTURE = "infrastructure"
    POLICY = "policy"


class EventPriority(Enum):
    """Priority levels for events."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """An event that can occur in the simulation."""
    id: str
    name: str
    event_type: EventType
    priority: EventPriority = EventPriority.MEDIUM
    scheduled_tick: Optional[int] = None
    duration: int = 1
    effects: Dict = field(default_factory=dict)
    conditions: Dict = field(default_factory=dict)
    
    # Runtime state
    active: bool = False
    started_tick: Optional[int] = None


@dataclass
class EventSystem:
    """
    Manages events in the simulation.
    
    Handles scheduling, triggering, and processing of events.
    """
    
    events: Dict[str, Event] = field(default_factory=dict)
    scheduled_events: Dict[int, List[str]] = field(default_factory=dict)
    active_events: List[str] = field(default_factory=list)
    
    # Event handlers
    handlers: Dict[str, Callable[[Event, Any], None]] = field(default_factory=dict)
    
    # History
    event_history: List[Dict] = field(default_factory=list)
    
    def initialize(self) -> None:
        """Initialize the event system."""
        self.events = {}
        self.scheduled_events = {}
        self.active_events = []
    
    def schedule_event(self, event: Event, tick: int) -> None:
        """Schedule an event for a specific tick."""
        event.scheduled_tick = tick
        self.events[event.id] = event
        
        if tick not in self.scheduled_events:
            self.scheduled_events[tick] = []
        self.scheduled_events[tick].append(event.id)
    
    def register_handler(self, event_type: EventType, handler: Callable[[Event, Any], None]) -> None:
        """Register a handler for an event type."""
        self.handlers[event_type.value] = handler
    
    def process_scheduled(self, current_tick: int) -> List[Event]:
        """Process all events scheduled for the current tick."""
        processed = []
        
        # Start scheduled events
        if current_tick in self.scheduled_events:
            for event_id in self.scheduled_events[current_tick]:
                event = self.events.get(event_id)
                if event:
                    self._start_event(event, current_tick)
                    processed.append(event)
        
        # Update active events
        completed = []
        for event_id in self.active_events:
            event = self.events.get(event_id)
            if event and event.started_tick:
                if current_tick >= event.started_tick + event.duration:
                    self._end_event(event, current_tick)
                    completed.append(event_id)
        
        # Remove completed events from active list
        for event_id in completed:
            self.active_events.remove(event_id)
        
        return processed
    
    def _start_event(self, event: Event, tick: int) -> None:
        """Start an event."""
        event.active = True
        event.started_tick = tick
        self.active_events.append(event.id)
        
        # Call handler if registered
        handler = self.handlers.get(event.event_type.value)
        if handler:
            handler(event, "start")
        
        # Record in history
        self.event_history.append({
            "event_id": event.id,
            "action": "started",
            "tick": tick
        })
    
    def _end_event(self, event: Event, tick: int) -> None:
        """End an event."""
        event.active = False
        
        # Call handler if registered
        handler = self.handlers.get(event.event_type.value)
        if handler:
            handler(event, "end")
        
        # Record in history
        self.event_history.append({
            "event_id": event.id,
            "action": "ended",
            "tick": tick
        })
    
    def trigger_event(self, event: Event, current_tick: int) -> None:
        """Immediately trigger an event."""
        self.events[event.id] = event
        self._start_event(event, current_tick)
    
    def get_active_events(self) -> List[Event]:
        """Get all currently active events."""
        return [
            self.events[event_id]
            for event_id in self.active_events
            if event_id in self.events
        ]
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Get all events of a specific type."""
        return [
            event for event in self.events.values()
            if event.event_type == event_type
        ]
