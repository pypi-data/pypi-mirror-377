"""Button widget implementations for tkinter/ttk mocks."""

from typing import Optional, Any, Callable
import logging
from unittest.mock import MagicMock

from ..constants import NORMAL, DISABLED
from .base import Widget, InvalidStateError

# Set up logger
logger = logging.getLogger(__name__)

class Button(Widget):
    """Mock Button widget.
    
    Attributes:
        _command: Callback function to execute when button is clicked
        
    Example:
        >>> def on_click(): print("Button clicked!")
        >>> button = Button(command=on_click)
        >>> button.invoke()
        Button clicked!
    """
    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._command: Optional[Callable] = kwargs.get('command', None)
        self._text = kwargs.get('text', '')
        self.invoke = MagicMock(side_effect=self._invoke)
        
    def _invoke(self) -> None:
        """Execute button command.
        
        Raises:
            InvalidStateError: If button is disabled
        """
        if self._state == DISABLED:
            raise InvalidStateError("Cannot invoke button in DISABLED state")
        if self._command:
            self._command()
            logger.debug("Button command executed")
            
    def _configure(self, **kwargs: Any) -> None:
        """Handle button configuration.
        
        Args:
            **kwargs: Configuration options for the button
        """
        super()._configure(**kwargs)
        if 'command' in kwargs:
            self._command = kwargs['command']
        if 'text' in kwargs:
            self._text = kwargs['text']
