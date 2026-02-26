from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Static, DirectoryTree
from textual.screen import Screen
from rich.text import Text
from pathlib import Path

from src.screen.quiz_screen import QuizScreen
from src.config_parser import ConfigParser
from src.parser_factory import ParserFactory
from src.review_factory import ReviewFactory
from src.manual_hooks import ManualHookFactory

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
        
        file_path = Path(event.path)
        config_path = file_path.parent / "config.toml"
        
        parser_func = None
        review_generator = None
        manual_hook = None

        if config_path.exists():
            try:
                config_parser = ConfigParser(config_path)
                parser_func = config_parser.get_parser()
                review_generator = config_parser.get_review_generator()
                manual_hook = config_parser.get_manual_hook()
            except ValueError as e:
                # Handle unknown types, perhaps show an error message on screen
                self.query_one("#status").update(f"Configuration Error: {e}")
                return
        
        # Fallback to defaults if config.toml not found or to use general defaults
        if parser_func is None:
            parser_func = ParserFactory().get_parser(file_path.suffix.lstrip('.'))
        if review_generator is None:
            review_generator = ReviewFactory().get_review_generator("simple")
        if manual_hook is None:
            manual_hook = ManualHookFactory().get_hook("man")

        self.app.push_screen(
            QuizScreen(
                file_path=file_path,
                parser_func=parser_func,
                review_generator=review_generator,
                manual_hook=manual_hook
            )
        )
