import logging

from src.parser.python_parser import create_questions_from_python_file as create_py_questions
from src.parser.c_treesitter_parser import create_questions_from_file as create_c_treesitter_questions

logger = logging.getLogger(__name__)

class ParserFactory:
    def get_parser(self, parser_type: str):
        logger.info(f"ParserFactory: Returning parser for type: {parser_type}")
        if parser_type == "c_treesitter":
            return create_c_treesitter_questions
        elif parser_type == "python":
            return create_py_questions
        else:
            logger.error(f"Unknown parser type: {parser_type}. Please use 'c_treesitter' for C/C++ files.")
            raise ValueError(f"Unknown parser type: {parser_type}. Please use 'c_treesitter' for C/C++ files.")
