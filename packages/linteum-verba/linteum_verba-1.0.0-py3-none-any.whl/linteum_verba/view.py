"""
Linteum Verba - Rich Text Editor
View Module (MVC)
"""
import tkinter as tk
from tkinter import font as tkfont
import logging
from typing import List, Dict, Tuple, Optional, Any, Set

logger = logging.getLogger(__name__)


class EditorView:
    """
    Handles all UI rendering. It is a passive component that only draws
    what the Controller tells it to. It has no knowledge of the app's logic.
    """

    def __init__(self, parent):
        logger.info("Initializing EditorView")
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.context_menu = tk.Menu(self.frame, tearoff=0)

        self.canvas = tk.Canvas(self.frame, bg="#282c34", highlightthickness=0)
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Font and layout configuration
        self.font = tkfont.Font(family="JetBrains Mono", size=12)
        self.line_height = self.font.metrics("linespace") + 4
        self.char_width = self.font.measure("0")
        self.top_margin = 5
        self.left_margin = 5
        self.line_number_width = 40
        self.fold_indicator_width = 20
        self.icon_width = 20
        self.horizontal_buffer = 10
        self.text_x_offset = (
            self.left_margin + self.line_number_width +
            self.fold_indicator_width + self.icon_width + self.horizontal_buffer
        )

        # Colors
        self.colors = {
            "background": "#282c34",
            "text": "#abb2bf",
            "line_number": "#636d83",
            "cursor": "#528bff",
            "selection": "#3e4451",
            "fold_indicator": "#61afef",
            "icon": "#d19a66",  # A shade of orange for the icon
            "checkmark": "#98c379",  # A shade of green for the checkmark
            "selected_text": "#d4d4d4"  # Light gray for selected text
        }

    def render(self, model_state: Dict[str, Any]):
        """Renders the entire editor view based on the provided model state."""
        self.canvas.delete("all")
        self._draw_line_numbers(model_state['visible_lines'])
        self._draw_selection(model_state['visible_lines'], model_state['selection'])
        self._draw_text(model_state['visible_lines'], model_state['highlights'], model_state['selection'])
        self._draw_cursor(model_state['visible_lines'], model_state['cursor_pos'])
        self._draw_fold_indicators(
            model_state['visible_lines'], model_state['foldable_lines'], model_state['folded_lines']
        )
        self._draw_line_icons(model_state['visible_lines'], model_state['line_icons'])

    def _draw_line_numbers(self, visible_lines: List[Tuple[int, str]]):
        """Draws the line numbers."""
        for i, (actual_line, _) in enumerate(visible_lines):
            y = self.top_margin + i * self.line_height
            self.canvas.create_text(
                self.left_margin, y, anchor="nw",
                text=f"{actual_line + 1: >4}",
                fill=self.colors['line_number'],
                font=self.font
            )

    def _draw_text(self, visible_lines: List[Tuple[int, str]],
                   highlights: Dict[int, List[Tuple[int, int, str]]],
                   selection: Optional[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Draws the text with syntax highlighting, handling selected text color."""
        sel_start, sel_end = selection if selection else ((-1, -1), (-1, -1))

        for i, (actual_line, line_text) in enumerate(visible_lines):
            y = self.top_margin + i * self.line_height
            
            line_highlights = highlights.get(actual_line, [(0, len(line_text), self.colors['text'])])

            for start, end, color in line_highlights:
                # Determine if this segment is selected
                is_selected = not (
                    actual_line < sel_start[0] or actual_line > sel_end[0] or
                    (actual_line == sel_start[0] and end <= sel_start[1]) or
                    (actual_line == sel_end[0] and start >= sel_end[1])
                )

                final_color = self.colors['selected_text'] if is_selected else color

                x = self.text_x_offset + start * self.char_width
                self.canvas.create_text(
                    x, y, anchor="nw",
                    text=line_text[start:end],
                    fill=final_color,
                    font=self.font,
                    tags="text"
                )

    def _draw_selection(self, visible_lines: List[Tuple[int, str]],
                        selection: Optional[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Draws the text selection."""
        if not selection:
            return

        (start_line, start_col), (end_line, end_col) = selection
        for i, (actual_line, line_text) in enumerate(visible_lines):
            if start_line <= actual_line <= end_line:
                y1 = self.top_margin + i * self.line_height
                y2 = y1 + self.line_height

                line_start_col = start_col if actual_line == start_line else 0
                line_end_col = end_col if actual_line == end_line else len(line_text)

                x1 = self.text_x_offset + line_start_col * self.char_width
                x2 = self.text_x_offset + line_end_col * self.char_width

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors['selection'], outline="")

    def _draw_cursor(self, visible_lines: List[Tuple[int, str]], cursor_pos: Tuple[int, int]):
        """Draws the cursor."""
        cursor_line, cursor_col = cursor_pos
        for i, (actual_line, _) in enumerate(visible_lines):
            if actual_line == cursor_line:
                x = self.text_x_offset + cursor_col * self.char_width
                y1 = self.top_margin + i * self.line_height
                y2 = y1 + self.line_height
                self.canvas.create_line(x, y1, x, y2, fill=self.colors['cursor'], width=2)
                break

    def _draw_fold_indicators(self, visible_lines: List[Tuple[int, str]],
                              foldable_lines: Set[int], folded_lines: Set[int]):
        """Draws the fold indicators (+/-)."""
        for i, (actual_line, _) in enumerate(visible_lines):
            if actual_line in foldable_lines:
                y = self.top_margin + i * self.line_height + self.line_height / 2
                x = self.left_margin + self.line_number_width + self.fold_indicator_width / 2
                symbol = "-" if actual_line in folded_lines else "+"
                self.canvas.create_text(
                    x, y, text=symbol, fill=self.colors['fold_indicator'],
                    font=self.font, tags="fold_indicator"
                )

    def _draw_line_icons(self, visible_lines: List[Tuple[int, str]], line_icons: Dict[int, str]):
        """Draws the line status icons."""
        for i, (actual_line, _) in enumerate(visible_lines):
            y = self.top_margin + i * self.line_height + self.line_height / 2
            x = self.left_margin + self.line_number_width + self.fold_indicator_width + self.icon_width / 2

            icon = line_icons.get(actual_line)
            if icon == 'breakpoint':
                # Draw a red circle for a breakpoint
                self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=self.colors['icon'], outline="")
            else:
                # Draw a green checkmark by default
                self.canvas.create_text(x, y, text="✓", fill=self.colors['checkmark'], font=self.font)

    def get_clipboard_text(self) -> str:
        """Gets text from the clipboard."""
        try:
            return self.frame.clipboard_get()
        except tk.TclError:
            return ""

    def set_clipboard_text(self, text: str):
        """Sets text to the clipboard."""
        self.frame.clipboard_clear()
        self.frame.clipboard_append(text)

    def get_position_from_event(self, event) -> Tuple[Optional[int], Optional[int], str]:
        """Converts a mouse event's coordinates to a (line, col, area) position."""
        x, y = event.x, event.y
        
        line = int((self.canvas.canvasy(y) - self.top_margin) / self.line_height)
        line = max(0, line)

        if x < self.left_margin + self.line_number_width:
            return line, None, "line_number_area"
        elif x < self.left_margin + self.line_number_width + self.fold_indicator_width:
            return line, None, "fold_indicator_area"
        elif x < self.text_x_offset:
            return line, None, "icon_area"
        else:
            col = int((self.canvas.canvasx(x) - self.text_x_offset) / self.char_width)
            col = max(0, col)
            return line, col, "text_area"
