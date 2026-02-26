import toml
from pathlib import Path

from src.parser_factory import ParserFactory
from src.review_factory import ReviewFactory
from src.manual_hooks import ManualHookFactory, ManualHook # Import ManualHook for type hinting

class ConfigParser:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        return toml.loads(self.config_path.read_text())

    def get_parser(self):
        parser_type = self.config.get("parser", {}).get("type", "python") # Default to python parser
        return ParserFactory().get_parser(parser_type)

    def get_review_generator(self) -> ReviewFactory:
        review_type = self.config.get("review", {}).get("type", "simple") # Default to simple review
        return ReviewFactory().get_review_generator(review_type)

    def get_manual_hook(self) -> ManualHook:
        hook_type = self.config.get("manual_hook", {}).get("type", "man") # Default to man hook
        return ManualHookFactory().get_hook(hook_type)
