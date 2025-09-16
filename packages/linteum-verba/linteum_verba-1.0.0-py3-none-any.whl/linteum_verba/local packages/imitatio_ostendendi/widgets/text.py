"""Text widget implementation for tkinter/ttk mocks."""

from typing import Optional, Any, Dict, Union
import logging
from unittest.mock import MagicMock

from ..constants import NORMAL, DISABLED, END
from .base import Widget, InvalidStateError

# Set up logger
logger = logging.getLogger(__name__)

class Text(Widget):
    """Mock Text widget for multiline text editing and display.
    
    Attributes:
        _text: Current text content
        _tags: Dictionary of text tags and their properties
        
    Example:
        >>> text = Text()
        >>> text.insert("1.0", "Hello, World!")
        >>> text.tag_configure("bold", font=("Helvetica", "12", "bold"))
        >>> text.tag_add("bold", "1.0", "1.5")
        >>> print(text.get("1.0", END))
        Hello, World!
    """
    def __init__(self, master: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._text = ""
        self._tags: Dict[str, Dict[str, Any]] = {}
        self._marks: Dict[str, int] = {"insert": 0, "current": 0}
        
        # Mock common methods
        self.delete = MagicMock(side_effect=self._delete)
        self.insert = MagicMock(side_effect=self._insert)
        self.get = MagicMock(side_effect=self._get)
        self.tag_configure = MagicMock(side_effect=self._tag_configure)
        self.tag_add = MagicMock(side_effect=self._tag_add)
        self.tag_remove = MagicMock(side_effect=self._tag_remove)
        self.mark_set = MagicMock(side_effect=self._mark_set)
        self.see = MagicMock()
        self.yview = MagicMock()
        self.yview_moveto = MagicMock()
        self.yview_scroll = MagicMock()
        
    def _parse_index(self, index: Union[str, int]) -> int:
        """Convert tkinter text index to integer position.
        
        Args:
            index: Text index in tkinter format (e.g., "1.0", END)
            
        Returns:
            Integer position in text
            
        Raises:
            ValueError: If index format is invalid
        """
        if isinstance(index, int):
            return index
        if isinstance(index, str):
            if index.lower() == END.lower():
                return len(self._text)
            if index == "1.0":
                return 0
            if "." in index:
                try:
                    line, char = map(int, index.split("."))
                    # Simple line.char to position conversion
                    lines = self._text.split("\n")
                    pos = sum(len(l) + 1 for l in lines[:line-1])
                    return pos + char
                except ValueError:
                    pass
        raise ValueError(f"Invalid index format: {index}")
        
    def _delete(self, first: Union[str, int], last: Optional[Union[str, int]] = None) -> None:
        """Delete text from widget.
        
        Args:
            first: Starting index
            last: Ending index (optional)
            
        Raises:
            InvalidStateError: If widget is disabled
        """
        if self._state == DISABLED:
            raise InvalidStateError("Cannot delete text in DISABLED state")
            
        try:
            start = self._parse_index(first)
            end = self._parse_index(last) if last is not None else start + 1
            
            if start > end:
                start, end = end, start
                
            self._text = self._text[:start] + self._text[end:]
            logger.debug(f"Deleted text from {start} to {end}")
            
        except ValueError as e:
            logger.error(f"Error in Text._delete: {e}")
            raise
            
    def _insert(self, index: Union[str, int], text: str, *tags: str) -> None:
        """Insert text into widget.
        
        Args:
            index: Position to insert text
            text: Text to insert
            *tags: Tags to apply to inserted text
            
        Raises:
            InvalidStateError: If widget is disabled
        """
        if self._state == DISABLED:
            raise InvalidStateError("Cannot insert text in DISABLED state")
            
        try:
            pos = self._parse_index(index)
            self._text = self._text[:pos] + text + self._text[pos:]
            logger.debug(f"Inserted text at position {pos}")
            
            # Apply tags if provided
            end_pos = pos + len(text)
            for tag in tags:
                self._tag_add(tag, pos, end_pos)
                
        except ValueError as e:
            logger.error(f"Error in Text._insert: {e}")
            raise
            
    def _get(self, start: Union[str, int] = "1.0", end: Union[str, int] = END) -> str:
        """Get text from widget.
        
        Args:
            start: Starting index
            end: Ending index
            
        Returns:
            Text content between start and end indices
        """
        try:
            start_pos = self._parse_index(start)
            end_pos = self._parse_index(end)
            return self._text[start_pos:end_pos]
        except ValueError as e:
            logger.error(f"Error in Text._get: {e}")
            raise
            
    def _mark_set(self, mark: str, index: Union[str, int]) -> None:
        """Set mark at specified index.
        
        Args:
            mark: Mark name
            index: Position to set mark
        """
        try:
            pos = self._parse_index(index)
            self._marks[mark] = pos
            logger.debug(f"Set mark {mark} at position {pos}")
        except ValueError as e:
            logger.error(f"Error in Text._mark_set: {e}")
            raise
            
    def _tag_configure(self, tag_name: str, **kwargs: Any) -> None:
        """Configure tag properties.
        
        Args:
            tag_name: Name of tag to configure
            **kwargs: Tag configuration options
        """
        if tag_name not in self._tags:
            self._tags[tag_name] = {}
        self._tags[tag_name].update(kwargs)
        logger.debug(f"Configured tag {tag_name} with {kwargs}")
            
    def _tag_add(self, tag_name: str, start: Union[str, int], end: Union[str, int]) -> None:
        """Add tag to text range.
        
        Args:
            tag_name: Name of tag to add
            start: Starting index
            end: Ending index
        """
        if tag_name not in self._tags:
            self._tags[tag_name] = {}
        logger.debug(f"Added tag {tag_name} from {start} to {end}")
            
    def _tag_remove(self, tag_name: str, start: Union[str, int], end: Union[str, int]) -> None:
        """Remove tag from text range.
        
        Args:
            tag_name: Name of tag to remove
            start: Starting index
            end: Ending index
        """
        if tag_name in self._tags:
            del self._tags[tag_name]
            logger.debug(f"Removed tag {tag_name} from {start} to {end}")
