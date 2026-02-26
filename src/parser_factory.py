from src.parser.c_parser import create_questions_from_file as create_c_questions
from src.parser.python_parser import create_questions_from_python_file as create_py_questions

class ParserFactory:
    def get_parser(self, parser_type: str):
        if parser_type == "c":
            return create_c_questions
        elif parser_type == "python":
            return create_py_questions
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")
