from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Static, DirectoryTree
from textual.screen import Screen
from rich.text import Text

from src.screen.quiz_screen import QuizScreen

ASCII_LOGO = """
██████╗ ██╗      █████╗ ███╗   ██╗ ██████╗  ██████╗ ██████╗ 
██╔══██╗██║     ██╔══██╗████╗  ██║██╔════╝ ██╔═══██╗██╔══██╗
██████╔╝██║     ███████║██╔██╗ ██║██║  ███╗██║   ██║██║  ██║
██╔══██╗██║     ██╔══██║██║╚██╗██║██║   ██║██║   ██║██║  ██║
██████╔╝███████╗██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██████╔╝
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═════╝ 
"""

class FrontPage(Screen):
    """The front page of the application."""

    def compose(self) -> ComposeResult:
        logo = Text(ASCII_LOGO, justify="center")
        yield Container(
            Static(logo, id="logo"),
            DirectoryTree(str("samples"), id="file-tree"),
            id="front-page-container",
        )
        yield Footer()

    def on_directory_tree_file_selected(
        self,
        event: DirectoryTree.FileSelected,
    ) -> None:
        """Called when the user clicks a file in the directory tree."""
        event.stop()
        self.app.push_screen(QuizScreen(file_path=event.path))
