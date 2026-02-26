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
    setup_logging()
    app = QuizApp()
    app.run()
