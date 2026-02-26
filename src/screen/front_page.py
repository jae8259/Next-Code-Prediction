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
        else: # If config.toml does not exist, use defaults based on file extension
            suffix = file_path.suffix.lstrip('.')
            if suffix == 'c':
                parser_func = ParserFactory().get_parser("c_treesitter")
            elif suffix == 'py':
                parser_func = ParserFactory().get_parser("python")
            else:
                self.query_one("#status").update(f"No config.toml found and unknown file type for: {file_path}")
                return

            review_generator = ReviewFactory().get_review_generator("simple")
            manual_hook = ManualHookFactory().get_hook("man")
            
        # If parser_func is still None at this point, it means config.toml existed but didn't specify a parser,
        # or there was an error in config parsing that was caught. In such cases, we should not proceed.
        if parser_func is None:
            self.query_one("#status").update(f"Could not determine parser for file: {file_path}")
            return

        self.app.push_screen(
            QuizScreen(
                file_path=file_path,
                parser_func=parser_func,
                review_generator=review_generator,
                manual_hook=manual_hook
            )
        )
