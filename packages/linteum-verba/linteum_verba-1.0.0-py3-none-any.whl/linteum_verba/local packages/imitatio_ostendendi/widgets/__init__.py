"""Widget package for tkinter/ttk mocks."""

from unittest.mock import MagicMock

from .base import Widget, WidgetError, InvalidStateError
from .text import Text
from .entry import Entry
from .buttons import Button
from .frames import Frame, LabelFrame

# Define aliases for mock classes expected by the test suite
MockTk = MagicMock
MockCanvas = MagicMock
MockTkinter = MagicMock
MockWidget = Widget
MockFrame = Frame
MockLabel = MagicMock
MockScrollbar = MagicMock


__all__ = [
    'Widget',
    'WidgetError',
    'InvalidStateError',
    'Text',
    'Entry',
    'Button',
    'Frame',
    'LabelFrame',
    'MockTk',
    'MockCanvas',
    'MockTkinter',
    'MockWidget',
    'MockFrame',
    'MockLabel',
    'MockScrollbar',
]
