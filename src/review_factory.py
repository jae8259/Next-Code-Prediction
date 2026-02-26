from src.review.review_note import ReviewNoteGenerator, SimpleNoteFactory

class ReviewFactory:
    def get_review_generator(self, review_type: str) -> ReviewNoteGenerator:
        if review_type == "simple":
            return ReviewNoteGenerator(SimpleNoteFactory())
        else:
            raise ValueError(f"Unknown review type: {review_type}")
