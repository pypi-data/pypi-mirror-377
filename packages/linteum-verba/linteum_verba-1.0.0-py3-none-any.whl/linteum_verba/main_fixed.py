"""
Linteum Verba - Main Application Entry Point
"""
import logging
from tkinter import Tk
from linteum_verba.model import EditorModel
from linteum_verba.view import EditorView
from linteum_verba.controller import EditorController
from linteum_verba.config_manager import ConfigManager
from linteum_verba.logging_config import configure_logging
from linteum_verba.event_bus import EventBus

class LinteumVerbaApp:
    """Main application class for Linteum Verba"""
    def __init__(self, root):
        self.root = root
        self.root.title("Linteum Verba")
        self.root.geometry("1024x768")

        # Configure logging
        configure_logging()

        # Initialize configuration manager
        self.config_manager = ConfigManager()

        # Create Event Bus
        event_bus = EventBus()

        # Create MVC components
        self.model = EditorModel(event_bus=event_bus)
        self.view = EditorView(root)
        self.controller = EditorController(self.model, self.view, event_bus=event_bus)

        # Create menu bar
        self.create_menu_bar()

        # Current file path
        self.current_file = None

        # Load sample code and perform initial render
        self.root.after(100, self.load_sample_code)
        self.root.after(200, self.controller.update_view)

    def create_menu_bar(self):
        """Create the application menu bar"""
        from tkinter import Menu
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Edit menu
        edit_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.controller.on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.controller.on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.controller.on_paste, accelerator="Ctrl+V")

        # View menu
        view_menu = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Language", command=self.show_language_menu)

        # Bind shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_file_as())

    def show_language_menu(self):
        """Show language selection menu"""
        from tkinter import Menu
        language_menu = Menu(self.root, tearoff=0)
        supported_languages = ["Python", "JavaScript", "HTML", "CSS", "XML", "JSON", "Text"]
        for lang in supported_languages:
            language_menu.add_command(
                label=lang, command=lambda lang_name=lang.lower(): self.controller.set_language(lang_name)
            )
        # Show menu at cursor position
        try:
            language_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            language_menu.grab_release()

    def new_file(self):
        """Create a new file"""
        from tkinter import messagebox
        if self.model.get_text() and messagebox.askyesno("New File", "Do you want to save changes?"):
            self.save_file()

        self.model.set_text("")
        self.current_file = None
        self.root.title("Linteum Verba - Untitled")
        self.controller.update_view()

    def open_file(self):
        """Open a file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.model.set_text(content)
            self.current_file = file_path
            self.root.title(f"Linteum Verba - {file_path}")
            self.controller.update_view()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.model.get_text())
                return True
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        """Save the current file with a new name"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".py")
        if not file_path:
            return False

        self.current_file = file_path
        self.root.title(f"Linteum Verba - {file_path}")
        return self.save_file()

    def exit_app(self):
        """Exit the application"""
        from tkinter import messagebox
        if self.model.get_text() and messagebox.askyesno("Exit", "Save changes before exiting?"):
            self.save_file()
        self.root.destroy()

    def load_sample_code(self):
        """Load sample Python code into the editor"""
        sample_code = (
            "class Greeter:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n\n"
            "    def greet(self):\n"
            "        print(f'Hello, {self.name}!')\n\n"
            "if __name__ == '__main__':\n"
            "    greeter = Greeter('World')\n"
            "    greeter.greet()\n"
        )
        self.model.set_text(sample_code)
        self.controller.update_view()
        logging.info("Sample code loaded.")


def main():
    """Main entry point for the application"""
    root = Tk()
    LinteumVerbaApp(root)  # The app instance is not needed
    root.mainloop()


if __name__ == "__main__":
    main()
