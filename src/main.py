from textual.app import App
from src.screen.front_page import FrontPage
from src.screen.quiz_screen import QuizScreen

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
    app = QuizApp()
    app.run()
