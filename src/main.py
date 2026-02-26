import argparse

from src.screen.front_page import FrontPage
from textual.app import App
from src.screen.quiz_screen import QuizScreen
from src.logger import setup_logging


class QuizApp(App):
    """A terminal quiz app for C and Python code."""

    BINDINGS = [
        ("escape", "quit", "Quit App"),
    ]

    MODES = {
        "front": FrontPage,
        "quiz": QuizScreen,
    }

    def on_mount(self) -> None:
        self.push_screen(FrontPage())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A terminal quiz app for C and Python code.")
    parser.add_argument("--log", action="store_true", help="Enable logging to file and console.")
    args = parser.parse_args()

    setup_logging(args.log)
    app = QuizApp()
    app.run()
