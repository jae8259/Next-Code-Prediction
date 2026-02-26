import logging

from src.review.review_note import ReviewNoteGenerator, SimpleNoteFactory

logger = logging.getLogger(__name__)

class ReviewFactory:
    def get_review_generator(self, review_type: str) -> ReviewNoteGenerator:
        logger.info(f"ReviewFactory: Returning review generator for type: {review_type}")
        if review_type == "simple":
            return ReviewNoteGenerator(SimpleNoteFactory())
        else:
            logger.error(f"Unknown review type: {review_type}")
            raise ValueError(f"Unknown review type: {review_type}")
