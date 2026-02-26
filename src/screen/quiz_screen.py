import random
import subprocess
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static
from textual.screen import Screen
from rich.syntax import Syntax

from src.parser.c_parser import create_questions_from_file as create_c_questions
from src.parser.python_parser import create_questions_from_python_file as create_py_questions
from src.review.review_note import ReviewNoteGenerator, SimpleNoteFactory


class QuizScreen(Screen):
    """The main quiz screen."""

    CSS_PATH = "../style/app.css"
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("up", "scroll_up", "Scroll Up"),
        ("down", "scroll_down", "Scroll Down"),
    ]

    def load_questions(self, path: Path):
        if path.suffix == ".c":
            return create_c_questions(str(path))
        elif path.suffix == ".py":
            return create_py_questions(str(path))
        else:
            # Maybe handle other file types or show an error
            return []

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        with open(file_path, "r") as f:
            self.file_lines = f.readlines()
        self.questions = self.load_questions(file_path)
        random.shuffle(self.questions)
        self.question_index = 0
        self.review_generator = ReviewNoteGenerator(SimpleNoteFactory())
        self.showing_answer = False
        self.start_line = 0
        self.end_line = 0

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
        if self.questions:
            self.next_question()
        else:
            self.query_one("#status").update("No questions found for this file type. Press Escape to go back.")
            self.query_one("#answer-input").disabled = True


    def next_question(self):
        """Loads and displays the next question."""
        self.showing_answer = False
        self.query_one("#status").update()
        self.query_one("#answer-input").disabled = False

        if self.question_index < len(self.questions):
            question = self.questions[self.question_index]
            
            # Find the line number of the answer
            answer_line = -1
            for i, line in enumerate(self.file_lines):
                if question.answer in line:
                    answer_line = i
                    break
            
            self.start_line = max(0, answer_line - 5)
            self.end_line = min(len(self.file_lines), self.start_line + 10)

            code_slice = "".join(self.file_lines[self.start_line:self.end_line])
            code_with_blank = code_slice.replace(question.answer, "■■■■■")
            
            code_widget = self.query_one("#code", Static)
            code_widget.update(Syntax(code_with_blank, "c" if self.file_path.suffix == '.c' else 'python', theme="monokai", line_numbers=True, start_line=self.start_line + 1))
            
            self.query_one("#answer-input").value = ""
            self.query_one("#answer-input").focus()
            self.question_index += 1
        else:
            self.query_one("#status").update("Quiz finished! Press Escape to go back.")
            self.query_one("#answer-input").disabled = True

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle answer submission."""
        if self.showing_answer:
            self.next_question()
            return

        answer = message.value.strip()
        question = self.questions[self.question_index - 1]
        question.user_answer = answer

        if answer == question.answer:
            self.query_one("#status").update("[green]Correct![/green] Press Enter to continue.")
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

    def key_c(self):
        if self.showing_answer:
            self.next_question()

    def key_m(self):
        if not self.showing_answer:
            return
        question = self.questions[self.question_index - 1]
        try:
            process = subprocess.run(["man", question.answer], capture_output=True, text=True, check=True)
            manual_content = process.stdout
            self.app.bell()
            self.query_one("#status").update(f"Showing man page for {question.answer}. Check terminal output. Press 'c' to continue.")
            print("\n" + "="*80)
            print(manual_content)
            print("="*80)
            print("Scroll up to view the manual. Press 'c' in the app to continue.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.query_one("#status").update(f"No manual provided for [b]{question.answer}[/b]. Press 'c' to continue.")

    def key_r(self):
        if not self.showing_answer:
            return
        question = self.questions[self.question_index - 1]
        if question.user_answer != question.answer and not getattr(question, 'review_note_created', False):
            note_path = self.review_generator.generate_review_note(question)
            self.query_one("#status").update(f"Review note saved to {note_path}. Press 'c' to continue.")
            question.review_note_created = True

    def action_scroll_up(self) -> None:
        if self.start_line > 0:
            self.start_line = max(0, self.start_line - 1)
            self.end_line = self.start_line + 10
            self._update_code_display()

    def action_scroll_down(self) -> None:
        if self.end_line < len(self.file_lines):
            self.end_line = min(len(self.file_lines), self.end_line + 1)
            self.start_line = self.end_line - 10
            self._update_code_display()

    def _update_code_display(self) -> None:
        question = self.questions[self.question_index - 1]
        code_slice = "".join(self.file_lines[self.start_line:self.end_line])
        code_with_blank = code_slice.replace(question.answer, "■■■■■")
        
        code_widget = self.query_one("#code", Static)
        code_widget.update(Syntax(code_with_blank, "c" if self.file_path.suffix == '.c' else 'python', theme="monokai", line_numbers=True, start_line=self.start_line + 1))
