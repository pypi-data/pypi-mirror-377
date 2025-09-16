"""
Linteum Verba - Model Module (MVC)
"""
import logging
from typing import List, Dict, Tuple, Optional, Any, Set

from pygments import lexers
from pygments.token import Token
from linteum_verba.event_bus import (
    EventBus, ContentLoadedEvent, LineFoldedEvent,
    LineUnfoldedEvent, IconChangedEvent, TextContentChangedEvent
)

logger = logging.getLogger(__name__)


class EditorModel:
    """
    Manages the editor's state, including text, cursor, selection, and syntax.
    This class is completely independent of the UI.
    """

    def __init__(self, event_bus: EventBus, text: str = "", file_path: Optional[str] = None):
        logger.info("Initializing EditorModel")
        self.event_bus = event_bus
        self.lines: List[str] = text.split("\n") if text else [""]
        self.cursor_pos: Tuple[int, int] = (0, 0)  # (line, col)
        self.selection: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None

        self.folded_lines: Set[int] = set()
        self.line_metadata: Dict[int, Dict[str, Any]] = {}
        self.line_icons: Dict[int, str] = {}  # {line_idx: 'icon_name'}

        self.lexer = lexers.get_lexer_by_name("python")
        self.token_colors = {
            Token.Keyword: "#569CD6",
            Token.Name.Class: "#4EC9B0",
            Token.Name.Function: "#DCDCAA",
            Token.Literal.String: "#CE9178",
            Token.Literal.Number: "#B5CEA8",
            Token.Comment: "#6A9955",
            Token.Operator: "#D4D4D4",
            Token.Punctuation: "#D4D4D4",
            Token: "#D4D4D4",
        }

    def set_text(self, text: str, file_path: Optional[str] = None):
        """Sets the entire text content and resets state."""
        logger.info(f"Setting text content (length: {len(text)})")
        self.lines = text.split("\n")
        self.cursor_pos = (0, 0)
        self.selection = None
        self.folded_lines = set()
        self.line_icons = {}
        self._update_metadata()
        self.event_bus.publish(ContentLoadedEvent(sender=self, file_path=file_path))

    def get_text(self) -> str:
        """Returns the full text content."""
        return "\n".join(self.lines)

    def insert_text(self, text: str, at: Optional[Tuple[int, int]] = None):
        """Inserts text at the given position or the current cursor position."""
        if self.selection:
            self.delete_selection()

        pos = at or self.cursor_pos
        line_num, col = pos
        current_line = self.lines[line_num]

        if "\n" in text:
            parts = text.split("\n")
            self.lines[line_num] = current_line[:col] + parts[0]
            remaining_lines = [
                part + current_line[col:] if i == len(parts) - 1 else part
                for i, part in enumerate(parts[1:])
            ]
            self.lines[line_num+1:line_num+1] = remaining_lines
            new_line = line_num + len(parts) - 1
            new_col = len(parts[-1])
        else:
            self.lines[line_num] = current_line[:col] + text + current_line[col:]
            new_line = line_num
            new_col = col + len(text)

        self.cursor_pos = (new_line, new_col)
        self._update_metadata()
        self.event_bus.publish(TextContentChangedEvent(sender=self, change_type='insert', start_pos=pos, end_pos=self.cursor_pos, text=text))

    def delete_text(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Deletes text between two positions."""
        (start_line, start_col), (end_line, end_col) = self._normalize_range(start, end)

        if start_line == end_line:
            self.lines[start_line] = self.lines[start_line][:start_col] + self.lines[start_line][end_col:]
        else:
            self.lines[start_line] = self.lines[start_line][:start_col] + self.lines[end_line][end_col:]
            del self.lines[start_line + 1:end_line + 1]

        self.cursor_pos = (start_line, start_col)
        self._update_metadata()

    def delete_selection(self) -> None:
        """Deletes the currently selected text."""
        if not self.selection:
            return

        normalized_selection = self.get_normalized_selection()
        if not normalized_selection:
            return

        start, end = normalized_selection
        deleted_text = self.get_text_in_range(start, end)
        self.delete_text(start, end)
        self.selection = None
        self.event_bus.publish(TextContentChangedEvent(sender=self, change_type='delete_selection', start_pos=start, end_pos=end, text=deleted_text))

    def move_cursor(self, delta_line: int = 0, delta_col: int = 0):
        """Moves the cursor by a given delta."""
        line, col = self.cursor_pos
        line += delta_line
        col += delta_col

        line = max(0, min(len(self.lines) - 1, line))
        col = max(0, min(len(self.lines[line]), col))

        self.cursor_pos = (line, col)

    def set_selection(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Sets the text selection."""
        self.selection = (start_pos, end_pos)

    def clear_selection(self):
        """Clears the text selection."""
        self.selection = None

    def get_selected_text(self) -> Optional[str]:
        """Returns the currently selected text."""
        if self.selection is None:
            return None
        return self.get_text_in_range(*self.selection)

    def has_selection(self) -> bool:
        """Checks if there is an active text selection."""
        return self.selection is not None

    def get_normalized_selection(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Returns the selection with start always before end."""
        if not self.selection:
            return None
        (start, end) = self.selection
        if start > end:
            return (end, start)
        return (start, end)

    def get_text_in_range(self, start: Tuple[int, int], end: Tuple[int, int]) -> str:
        """Returns the text within a given range."""
        (start_line, start_col), (end_line, end_col) = self._normalize_range(start, end)
        if start_line == end_line:
            return self.lines[start_line][start_col:end_col]
        else:
            lines = [self.lines[start_line][start_col:]]
            lines.extend(self.lines[start_line + 1:end_line])
            lines.append(self.lines[end_line][:end_col])
            return "\n".join(lines)

    def _normalize_range(self, start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Ensures that the start position is before the end position."""
        if start > end:
            return end, start
        return start, end

    def set_language(self, language_name: str):
        """Sets the syntax highlighting language."""
        try:
            self.lexer = lexers.get_lexer_by_name(language_name)
            logger.info(f"Language set to {language_name}")
            self._update_metadata()  # Re-tokenize with the new lexer
            self.event_bus.publish(TextContentChangedEvent(sender=self, change_type='language', start_pos=None, end_pos=None, text=language_name))
        except lexers.ClassNotFound:
            logger.error(f"Lexer for '{language_name}' not found.")

    def _update_metadata(self):
        """Updates metadata like fold levels for all lines."""
        self.line_metadata = {}
        for i, line in enumerate(self.lines):
            self.line_metadata[i] = {
                'fold_level': len(line) - len(line.lstrip(' '))
            }

    def _get_fold_level(self, line_idx: int) -> int:
        """Gets the indentation level of a line."""
        if line_idx in self.line_metadata:
            return self.line_metadata[line_idx].get('fold_level', 0)
        return 0

    def _can_fold(self, line_idx: int) -> bool:
        """Checks if a line can be folded (i.e., has an indented block after it)."""
        if line_idx >= len(self.lines) - 1:
            return False

        current_level = self._get_fold_level(line_idx)
        # Check if the next line is more indented
        if self._get_fold_level(line_idx + 1) > current_level:
            return True

        return False

    def toggle_fold(self, line_idx: int):
        """Toggles the fold state of a given line."""
        logger.debug(f"Attempting to toggle fold for line {line_idx}")
        if not self._can_fold(line_idx):
            logger.warning(f"Line {line_idx} is not foldable.")
            return

        if line_idx in self.folded_lines:
            self.folded_lines.remove(line_idx)
            logger.info(f"Unfolded line {line_idx}")
            self.event_bus.publish(LineUnfoldedEvent(sender=self, line_idx=line_idx))
        else:
            self.folded_lines.add(line_idx)
            logger.info(f"Folded line {line_idx}")
            self.event_bus.publish(LineFoldedEvent(sender=self, line_idx=line_idx))
        # No need to call _update_metadata() as fold levels don't change

    def is_folded(self, line_idx: int) -> bool:
        """Checks if a line is currently folded."""
        return line_idx in self.folded_lines

    def fold_line(self, line_idx: int):
        """Programmatically folds a line."""
        if self._can_fold(line_idx) and line_idx not in self.folded_lines:
            self.folded_lines.add(line_idx)
            logger.info(f"Programmatically folded line {line_idx}")
            self.event_bus.publish(LineFoldedEvent(sender=self, line_idx=line_idx))

    def unfold_line(self, line_idx: int):
        """Programmatically unfolds a line."""
        if line_idx in self.folded_lines:
            self.folded_lines.remove(line_idx)
            logger.info(f"Programmatically unfolded line {line_idx}")
            self.event_bus.publish(LineUnfoldedEvent(sender=self, line_idx=line_idx))

    def has_children(self, line_idx: int) -> bool:
        """Checks if a line has indented child lines."""
        if line_idx >= len(self.lines) - 1:
            return False

        current_level = self._get_fold_level(line_idx)
        next_level = self._get_fold_level(line_idx + 1)
        return next_level > current_level

    def is_foldable(self, line_idx: int) -> bool:
        """Checks if a line is foldable."""
        return self._can_fold(line_idx)

    def get_foldable_lines(self) -> Set[int]:
        """Returns a set of all line indices that are foldable."""
        return {i for i in range(len(self.lines)) if self._can_fold(i)}

    def set_line_icon(self, line_idx: int, icon: Optional[str]):
        """Sets or removes an icon for a given line."""
        if icon:
            self.line_icons[line_idx] = icon
            logger.info(f"Set icon '{icon}' for line {line_idx}")
        elif line_idx in self.line_icons:
            del self.line_icons[line_idx]
            logger.info(f"Removed icon from line {line_idx}")
        self.event_bus.publish(IconChangedEvent(sender=self, line_idx=line_idx, icon=icon if icon is not None else ''))

    def get_line_icons(self) -> Dict[int, str]:
        """Returns the dictionary of line icons."""
        return self.line_icons

    def get_visible_lines(self) -> List[Tuple[int, str]]:
        """Returns a list of (actual_line_index, line_text) for visible lines."""
        visible = []
        for i, line in enumerate(self.lines):
            if not self._is_line_hidden(i):
                visible.append((i, line))
        return visible

    def _is_line_hidden(self, line_idx: int) -> bool:
        """Checks if a line is hidden inside a folded block."""
        # A line cannot be hidden by folds if there are no folded lines.
        if not self.folded_lines:
            return False

        # Find the closest preceding line with a lower indentation level that is folded.
        for i in range(line_idx - 1, -1, -1):
            potential_parent_level = self._get_fold_level(i)
            current_level = self._get_fold_level(line_idx)

            if potential_parent_level < current_level:
                # This is a potential parent. Is it folded?
                if i in self.folded_lines:
                    # Yes, it's folded. So, the current line is hidden.
                    return True
                # If it's not folded, we need to check its parents.
                # This recursive check is handled by continuing the loop.

        return False

    def _highlight_line(self, line: str) -> List[Tuple[int, int, str]]:
        """Highlights a single line."""
        tokens = list(self.lexer.get_tokens(line))
        highlights = []
        pos = 0
        for token_type, value in tokens:
            color = self._get_token_color(token_type)
            end_pos = pos + len(value)
            highlights.append((pos, end_pos, color))
            pos = end_pos
        return highlights

    def get_syntax_highlighting(self) -> Dict[int, List[Tuple[int, int, str]]]:
        """Returns syntax highlighting for all lines."""
        highlights = {}
        for i, line in enumerate(self.lines):
            highlights[i] = self._highlight_line(line)
        return highlights

    def _get_token_color(self, token_type) -> str:
        """Gets the color for a given Pygments token."""
        while token_type not in self.token_colors:
            token_type = token_type.parent
            if token_type is None:
                return self.token_colors[Token]
        return self.token_colors[token_type]
