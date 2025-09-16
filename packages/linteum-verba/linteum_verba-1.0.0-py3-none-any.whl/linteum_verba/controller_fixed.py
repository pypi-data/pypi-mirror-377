"""
Linteum Verba - Controller Module (MVC)
"""
import logging
from typing import Optional
from linteum_verba.model import EditorModel
from linteum_verba.view import EditorView
from linteum_verba.event_bus import EventBus

logger = logging.getLogger(__name__)


class EditorController:
    """
    Acts as the intermediary between the EditorModel and EditorView.
    It handles user input events and updates both the model and view accordingly.
    """

    def __init__(self, model: EditorModel, view: EditorView, event_bus: EventBus):
        logger.info("Initializing EditorController")
        self.model = model
        self.view = view
        self.event_bus = event_bus

        # Bind UI events
        self._bind_events()

    def _bind_events(self):
        """Binds all UI events to their respective handler methods."""
        self.view.canvas.bind("<Key>", self.on_key_press)
        self.view.canvas.bind("<Button-1>", self.on_mouse_click)
        self.view.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.view.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.view.canvas.bind("<Delete>", self.on_delete)
        self.view.canvas.bind("<Control-c>", self.on_copy)
        self.view.canvas.bind("<Control-v>", self.on_paste)
        self.view.canvas.bind("<Control-x>", self.on_cut)
        self.view.canvas.bind("<BackSpace>", self.on_backspace)

        self.view.canvas.focus_set()
        self.view.canvas.bind("<Button-3>", self.on_right_click)

    def update_view(self):
        """Fetches the latest state from the model and tells the view to render it."""
        model_state = {
            'visible_lines': self.model.get_visible_lines(),
            'highlights': self.model.get_syntax_highlighting(),
            'selection': self.model.get_normalized_selection(),
            'cursor_pos': self.model.cursor_pos,
            'folded_lines': self.model.folded_lines,
            'foldable_lines': self.model.get_foldable_lines(),
            'line_icons': self.model.get_line_icons()
        }
        self.view.render(model_state)

    def on_key_press(self, event):
        """Handles character key presses."""
        if event.char:
            self.model.insert_text(event.char)
            self.update_view()

    def on_backspace(self, event):
        """Handles the Backspace key."""
        if self.model.selection:
            self.model.delete_selection()
        else:
            end = self.model.cursor_pos
            if end == (0, 0):
                return  # Nothing to delete
            self.model.move_cursor(delta_col=-1)
            start = self.model.cursor_pos
            self.model.delete_text(start, end)
        self.update_view()

    def on_delete(self, event):
        """Handles the Delete key."""
        if self.model.selection:
            self.model.delete_selection()
        else:
            start = self.model.cursor_pos
            if start == (len(self.model.lines) - 1, len(self.model.lines[-1])):
                return  # Nothing to delete
            end_line = start[0]
            end_col = start[1] + 1
            if end_col > len(self.model.lines[end_line]):
                if end_line + 1 < len(self.model.lines):
                    end_line += 1
                    end_col = 0
                else:
                    return  # Nothing to delete
            end = (end_line, end_col)
            self.model.delete_text(start, end)
        self.update_view()

    def on_mouse_click(self, event):
        """Handles mouse clicks."""
        line, col, area = self.view.get_position_from_event(event)
        if line is not None:
            if area == "line_number_area":
                # Handle line number clicks
                self.model.clear_selection()
                if col is None:
                    # Select entire line
                    start_pos = (line, 0)
                    end_pos = (line, len(self.model.lines[line]))
                    self.model.set_selection(start_pos, end_pos)
            elif area == "fold_indicator_area":
                # Handle fold indicator clicks
                if col is None:
                    self.model.toggle_fold(line)
            elif area == "icon_area":
                # Handle icon clicks
                if col is None:
                    self._on_line_icon_click(line)
            else:
                # Handle text area clicks
                self.model.clear_selection()
                self.model.cursor_pos = (line, col)
        self.update_view()

    def on_mouse_drag(self, event):
        """Handles mouse drag for text selection."""
        line, col, area = self.view.get_position_from_event(event)
        if line is not None and area == "text_area" and col is not None:
            start_line, start_col = self.model.cursor_pos
            end_line, end_col = line, col
            self.model.set_selection((start_line, start_col), (end_line, end_col))
        self.update_view()

    def on_mouse_wheel(self, event):
        """Handles mouse wheel scrolling."""
        # This would typically scroll the view
        pass

    def on_copy(self, event):
        """Handles copy operation."""
        selected_text = self.model.get_selected_text()
        if selected_text:
            self.view.set_clipboard_text(selected_text)

    def on_paste(self, event):
        """Handles paste operation."""
        clipboard_text = self.view.get_clipboard_text()
        if clipboard_text:
            self.model.insert_text(clipboard_text)
        self.update_view()

    def on_cut(self, event):
        """Handles cut operation."""
        selected_text = self.model.get_selected_text()
        if selected_text:
            self.view.set_clipboard_text(selected_text)
            self.model.delete_selection()
        self.update_view()

    def on_right_click(self, event):
        """Handles right-click for context menu."""
        line, col, area = self.view.get_position_from_event(event)
        if line is not None:
            # Position cursor at click location
            if area == "text_area" and col is not None:
                self.model.cursor_pos = (line, col)
                self.model.clear_selection()

            # Show context menu
            self._show_context_menu(event.x_root, event.y_root)

        self.update_view()

    def _show_context_menu(self, x, y):
        """Shows the context menu at the specified position."""
        self.view.context_menu.delete(0, "end")  # Clear existing menu items

        # Add menu items
        self.view.context_menu.add_command(label="Cut", command=self.on_cut)
        self.view.context_menu.add_command(label="Copy", command=self.on_copy)
        self.view.context_menu.add_command(label="Paste", command=self.on_paste)
        self.view.context_menu.add_separator()
        self.view.context_menu.add_command(label="Select All", command=self.select_all)

        # Show the menu
        try:
            self.view.context_menu.tk_popup(x, y)
        finally:
            self.view.context_menu.grab_release()

    def select_all(self):
        """Selects all text in the editor."""
        if self.model.lines:
            start_pos = (0, 0)
            end_pos = (len(self.model.lines) - 1, len(self.model.lines[-1]))
            self.model.set_selection(start_pos, end_pos)
        self.update_view()

    def _on_line_icon_click(self, line_idx: int):
        """Handles clicks on line icons."""
        # This could show a context menu or perform other actions
        pass

    # Public API methods
    def set_language(self, language: str):
        """Sets the syntax highlighting language."""
        self.model.set_language(language)
        self.update_view()

    def toggle_fold(self, line_idx: int):
        """Toggles the fold state of a line."""
        self.model.toggle_fold(line_idx)
        self.update_view()

    def get_foldable_lines(self):
        """Returns the set of foldable lines."""
        return self.model.get_foldable_lines()

    def set_line_icon(self, line_idx: int, icon: Optional[str]):
        """Sets an icon for a line."""
        self.model.set_line_icon(line_idx, icon)
        self.update_view()
