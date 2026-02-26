import logging

from src.parser.c_parser import create_questions_from_file as create_c_questions
from src.parser.python_parser import create_questions_from_python_file as create_py_questions

logger = logging.getLogger(__name__)

class ParserFactory:
    def get_parser(self, parser_type: str):
        logger.info(f"ParserFactory: Returning parser for type: {parser_type}")
        if parser_type == "c":
            return create_c_questions
        elif parser_type == "python":
            return create_py_questions
        else:
            logger.error(f"Unknown parser type: {parser_type}")
            raise ValueError(f"Unknown parser type: {parser_type}")
