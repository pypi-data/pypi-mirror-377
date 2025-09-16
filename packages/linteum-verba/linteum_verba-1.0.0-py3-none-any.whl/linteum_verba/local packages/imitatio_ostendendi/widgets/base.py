"""Base widget implementation for tkinter/ttk mocks."""

from typing import Optional, Any, Callable, Dict, List, Union
import logging
from unittest.mock import MagicMock

from ..constants import NORMAL, DISABLED

# Set up logger
logger = logging.getLogger(__name__)

class WidgetError(Exception):
    """Base exception for widget-related errors."""
    pass

class InvalidStateError(WidgetError):
    """Exception raised when widget is in invalid state."""
    pass

class Widget:
    """Base class for all mock widgets.
    
    Attributes:
        _state: Current state of the widget (NORMAL or DISABLED)
        pack: MagicMock for pack geometry manager
        grid: MagicMock for grid geometry manager
        place: MagicMock for place geometry manager
        
    Example:
        >>> widget = Widget(state=NORMAL)
        >>> widget.pack(side='top', fill='x')
        >>> widget.configure(state=DISABLED)
    """
    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        self._state = kwargs.get('state', NORMAL)
        self._bindings: Dict[str, List[Callable]] = {}
        self.pack = MagicMock()
        self.grid = MagicMock()
        self.place = MagicMock()
        self.configure = MagicMock(side_effect=self._configure)
        self.bind = MagicMock(side_effect=self._bind)
        self.unbind = MagicMock(side_effect=self._unbind)
        
    def _configure(self, **kwargs: Any) -> None:
        """Handle widget configuration.
        
        Args:
            **kwargs: Configuration options for the widget
        
        Raises:
            InvalidStateError: If an invalid state is provided
        """
        if 'state' in kwargs:
            state = kwargs['state']
            if state not in (NORMAL, DISABLED):
                raise InvalidStateError(f"Invalid state: {state}")
            self._state = state
            
    def _bind(self, sequence: str, func: Callable, add: bool = False) -> None:
        """Bind function to event sequence.
        
        Args:
            sequence: Event sequence to bind to
            func: Callback function
            add: If True, add this binding to existing bindings
        """
        if sequence not in self._bindings:
            self._bindings[sequence] = []
        if add:
            self._bindings[sequence].append(func)
        else:
            self._bindings[sequence] = [func]
            
    def _unbind(self, sequence: str) -> None:
        """Remove all bindings for event sequence.
        
        Args:
            sequence: Event sequence to unbind
        """
        if sequence in self._bindings:
            del self._bindings[sequence]
