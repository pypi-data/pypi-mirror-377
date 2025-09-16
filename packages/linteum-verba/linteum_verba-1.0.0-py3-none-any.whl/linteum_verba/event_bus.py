"""
Event Bus and Event Definitions for the Linteum Verba Editor
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Base class for all events."""
    sender: Any

@dataclass
class ContentLoadedEvent(Event):
    """Fired when new content is loaded into the editor."""
    file_path: Optional[str] = None

@dataclass
class TextContentChangedEvent(Event):
    """Fired when the text content of the editor changes."""
    change_type: str
    start_pos: Optional[tuple]
    end_pos: Optional[tuple]
    text: str = ""

@dataclass
class LineFoldedEvent(Event):
    """Fired when a line is folded."""
    line_idx: int

@dataclass
class LineUnfoldedEvent(Event):
    """Fired when a line is unfolded."""
    line_idx: int

@dataclass
class IconChangedEvent(Event):
    """Fired when an icon on a line is changed."""
    line_idx: int
    icon: Optional[str] = None

class EventBus:
    """A simple event bus for dispatching events to listeners."""
    def __init__(self):
        self._subscribers = defaultdict(list)
        logger.info("EventBus instance created.")

    def subscribe(self, event_type: type, listener: Callable):
        """Subscribe a listener to an event type."""
        self._subscribers[event_type].append(listener)

    def unsubscribe(self, event_type: type, listener: Callable):
        """Unsubscribe a listener from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(listener)

    def publish(self, event: Event):
        """Publish an event to all subscribed listeners."""
        event_type = type(event)
        if event_type in self._subscribers:
            for listener in self._subscribers[event_type]:
                listener(event)
