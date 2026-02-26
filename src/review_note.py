from abc import ABC, abstractmethod
import os
from datetime import datetime

class AbstractQuestion(ABC):
    """An abstract base class for a quiz question."""
    def __init__(self, context: str, answer: str):
        self.context = context
        self.answer = answer
        self.user_answer = ""

    @abstractmethod
    def get_question_text(self) -> str:
        """Returns the text of the question to be displayed."""
        pass

class FunctionQuestion(AbstractQuestion):
    """A question where the user has to guess a function name."""
    def get_question_text(self) -> str:
        return self.context.replace(self.answer, "____")

class ReviewNote:
    """Represents a review note."""
    def __init__(self, question: AbstractQuestion):
        self.question = question

    def generate_content(self) -> str:
        """Generates the content of the review note."""
        question_text = self.question.get_question_text()
        return f"{question_text}\na: {self.question.user_answer}\nans: {self.question.answer}"


class ReviewNoteFactory(ABC):
    """An abstract factory for creating review notes."""
    @abstractmethod
    def create_note(self, question: AbstractQuestion) -> ReviewNote:
        pass

class SimpleNoteFactory(ReviewNoteFactory):
    """A factory for creating simple text-based review notes."""
    def create_note(self, question: AbstractQuestion) -> ReviewNote:
        return ReviewNote(question)


class ReviewNoteGenerator:
    """Generates and saves review notes."""
    def __init__(self, note_factory: ReviewNoteFactory, review_dir: str = "review"):
        self.note_factory = note_factory
        self.review_dir = review_dir
        if not os.path.exists(self.review_dir):
            os.makedirs(self.review_dir)

    def generate_review_note(self, question: AbstractQuestion):
        """
        Creates a review note and saves it to a file.
        """
        note = self.note_factory.create_note(question)
        content = note.generate_content()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.review_dir, f"review_{timestamp}.txt")
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
