import toml
from pathlib import Path
import logging

from src.parser_factory import ParserFactory
from src.review_factory import ReviewFactory
from src.manual_hooks import ManualHookFactory, ManualHook # Import ManualHook for type hinting

logger = logging.getLogger(__name__)

class ConfigParser:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        logger.info(f"Loaded configuration from: {config_path}")

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        return toml.loads(self.config_path.read_text())

    def get_parser(self):
        parser_type = self.config.get("parser", {}).get("type", "python") # Default to python parser
        logger.info(f"Loading parser of type: {parser_type}")
        return ParserFactory().get_parser(parser_type)

    def get_review_generator(self) -> ReviewFactory:
        review_type = self.config.get("review", {}).get("type", "simple") # Default to simple review
        logger.info(f"Loading review generator of type: {review_type}")
        return ReviewFactory().get_review_generator(review_type)

    def get_manual_hook(self) -> ManualHook:
        hook_type = self.config.get("manual_hook", {}).get("type", "man") # Default to man hook
        logger.info(f"Loading manual hook of type: {hook_type}")
        return ManualHookFactory().get_hook(hook_type)
