# UPDATEME With additional components in `tui/components/`
# See Textual documentation at:
# https://textual.textualize.io/tutorial/
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Label

from art import text2art

from python_project.tui.themes import AppCustomThemes

CSS_DIRECTORY = Path(__file__).parent / "css"

class TerminalApp(App):
    """Textual app to serve as the Python Project interface."""

    CSS_PATH = [
        CSS_DIRECTORY / "demo.tcss", # UPDATEME by removing when no longer needed
        CSS_DIRECTORY / "noctis.tcss",
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # UPDATEME by replacing with your own widgets
        yield Label(text2art("Python Project", "tarty1"), classes="title")
        yield Label("[i][b]Awesome `python-project` is a Python cli/package created with https://gitlab.com/galactipy/galactipy.[/]", classes="description")
        yield Footer()

    def on_mount(self) -> None:
        """Execute instructions when launching the interface."""
        for theme in AppCustomThemes:
            self.register_theme(theme.value)

        self.theme = "noctis"


if __name__ == "__main__":
    app = TerminalApp()
    app.run()
