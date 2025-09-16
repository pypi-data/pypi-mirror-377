"""Entry widget implementation for tkinter/ttk mocks."""

from typing import Optional, Any, Union
import logging
from unittest.mock import MagicMock

from ..constants import NORMAL, DISABLED, END
from .base import Widget, InvalidStateError

# Set up logger
logger = logging.getLogger(__name__)

class Entry(Widget):
    """Mock Entry widget for single-line text input.
    
    Attributes:
        _text: Current text content
        _textvariable: Associated StringVar
        
    Example:
        >>> entry = Entry()
        >>> entry.insert(0, "Hello")
        >>> entry.insert(END, ", World!")
        >>> print(entry.get())
        Hello, World!
    """
    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._text = ""
        self._textvariable = kwargs.get('textvariable', None)
        if self._textvariable:
            self._text = str(self._textvariable.get())
            
        # Mock common methods
        self.delete = MagicMock(side_effect=self._delete)
        self.insert = MagicMock(side_effect=self._insert)
        self.get = MagicMock(side_effect=lambda: self._text)
        
    def _delete(self, first: Union[str, int], last: Optional[Union[str, int]] = None) -> None:
        """Delete text from entry.
        
        Args:
            first: Starting index
            last: Ending index (optional)
            
        Raises:
            InvalidStateError: If widget is disabled
        """
        if self._state == DISABLED:
            raise InvalidStateError("Cannot delete text in DISABLED state")
            
        try:
            # Convert indices
            if isinstance(first, str) and first.lower() == END.lower():
                start = len(self._text)
            else:
                start = int(first)
                
            if last is None:
                end = start + 1
            elif isinstance(last, str) and last.lower() == END.lower():
                end = len(self._text)
            else:
                end = int(last)
                
            # Delete the text
            self._text = self._text[:start] + self._text[end:]
            if self._textvariable:
                self._textvariable.set(self._text)
            logger.debug(f"Deleted text from {start} to {end}")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error in Entry._delete: {e}")
            raise
            
    def _insert(self, index: Union[str, int], string: str) -> None:
        """Insert text into entry.
        
        Args:
            index: Position to insert text
            string: Text to insert
            
        Raises:
            InvalidStateError: If widget is disabled
        """
        if self._state == DISABLED:
            raise InvalidStateError("Cannot insert text in DISABLED state")
            
        try:
            if isinstance(index, str) and index.lower() == END.lower():
                pos = len(self._text)
            else:
                pos = int(index)
                
            self._text = self._text[:pos] + string + self._text[pos:]
            if self._textvariable:
                self._textvariable.set(self._text)
            logger.debug(f"Inserted text at position {pos}")
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error in Entry._insert: {e}")
            raise
