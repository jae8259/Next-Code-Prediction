import os
import subprocess
import random

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static
from rich.syntax import Syntax
from pathlib import Path
from textual.binding import Binding

from src.c_parser import create_questions_from_file
from src.review_note import ReviewNoteGenerator, SimpleNoteFactory

ROOT_DIR = Path(__file__).parent.parent
SOURCE_CODE_PATH = ROOT_DIR / "samples/rdma-example/src/rdma_server.c"

class QuizApp(App):
    """A terminal quiz app for C code."""

    CSS_PATH = "app.css"
    BINDINGS = [
        Binding("c", "next_question", "Continue", show=True),
        Binding("m", "show_manual", "Manual", show=True),
        Binding("r", "make_review_note", "Review Note", show=True),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("escape", "quit", "Quit", show=False, priority=True),
        Binding("k", "scroll_up", "Scroll Up", show=False, priority=True),
        Binding("j", "scroll_down", "Scroll Down", show=False, priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.questions = create_questions_from_file(str(SOURCE_CODE_PATH))
        random.shuffle(self.questions)
        self.question_index = 0
        self.review_generator = ReviewNoteGenerator(SimpleNoteFactory())
        self.showing_answer = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="quiz-container"):
            with Container(id="code-view"):
                yield Static(id="code")
            yield Input(placeholder="Your answer...", id="answer-input")
            yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        self.next_question()

    def next_question(self):
        """Loads and displays the next question."""
        self.showing_answer = False
        self.query_one("#status").update()
        self.query_one("#answer-input").disabled = False


        if self.question_index < len(self.questions):
            question = self.questions[self.question_index]
            
            # Highlight the blank
            code = question.context.replace(question.answer, "[b red]____[/b red]")

            code_widget = self.query_one("#code", Static)
            code_widget.update(Syntax(code, "c", theme="monokai", line_numbers=True))
            
            self.query_one("#answer-input").value = ""
            self.query_one("#answer-input").focus()
            self.question_index += 1
        else:
            self.query_one("#status").update("Quiz finished! Press Ctrl+C to exit.")
            self.query_one("#answer-input").disabled = True


    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle answer submission."""
        if self.showing_answer:
            self.action_next_question()
            return

        answer = message.value.strip()
        question = self.questions[self.question_index - 1]
        question.user_answer = answer

        if answer == question.answer:
            self.query_one("#status").update("[green]Correct![/green] Press 'c' to continue.")
            self.showing_answer = True
        else:
            status_message = (
                f"[red]Incorrect.[/red]\n"
                f"Your answer: {answer}\n"
                f"Correct answer: [b]{question.answer}[/b]\n\n"
                "Press 'c' to continue, 'm' for manual, or 'r' for a review note."
            )
            self.query_one("#status").update(status_message)
            self.showing_answer = True
        
        self.query_one("#answer-input").disabled = True

    def action_next_question(self) -> None:
        if self.showing_answer:
            self.next_question()

    def action_make_review_note(self) -> None:
        if not self.showing_answer:
            return
        question = self.questions[self.question_index - 1]
        # Only allow review notes for incorrect answers
        if question.user_answer != question.answer and not getattr(question, 'review_note_created', False):
            note_path = self.review_generator.generate_review_note(question)
            self.query_one("#status").update(f"Review note saved to {note_path}. Press 'c' to continue.")
            question.review_note_created = True


    def action_show_manual(self) -> None:
        if not self.showing_answer:
            return
        question = self.questions[self.question_index - 1]
        try:
            process = subprocess.run(["man", question.answer], capture_output=True, text=True, check=True)
            manual_content = process.stdout
            # For now, just print to a log. A modal screen would be better.
            self.app.bell()
            self.query_one("#status").update(f"Showing man page for {question.answer}. Check terminal output. Press 'c' to continue.")
            print("\n" + "="*80)
            print(manual_content)
            print("="*80)
            print("Scroll up to view the manual. Press 'c' in the app to continue.")

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.query_one("#status").update(f"No manual provided for [b]{question.answer}[/b]. Press 'c' to continue.")

    def action_scroll_up(self) -> None:
        self.query_one("#code-view").scroll_up()

    def action_scroll_down(self) -> None:
        self.query_one("#code-view").scroll_down()


if __name__ == "__main__":
    app = QuizApp()
    app.run()
