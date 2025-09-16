"""Imitatio Ostendendi - Mock widgets for tkinter/ttk testing."""

from .widgets import (
    Widget, Text, Entry, Button, Frame, LabelFrame,
    WidgetError, InvalidStateError
)
from .constants import (
    NORMAL, DISABLED, READONLY, VERTICAL, HORIZONTAL,
    OK, YES, NO, END, WORD, BOTH, X, Y
)

__version__ = "0.2.1"

__all__ = [
    'Widget',
    'Text',
    'Entry',
    'Button',
    'Frame',
    'LabelFrame',
    'WidgetError',
    'InvalidStateError',
    'NORMAL',
    'DISABLED',
    'READONLY',
    'VERTICAL',
    'HORIZONTAL',
    'OK',
    'YES',
    'NO',
    'END',
    'WORD',
    'BOTH',
    'X',
    'Y',
]
