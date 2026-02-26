import ast
from typing import List
from src.review.review_note import FunctionQuestion

class FuncCallVisitor(ast.NodeVisitor):
    def __init__(self, lines):
        self.lines = lines
        self.questions = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            line_num = node.lineno

            # Avoid very common built-in functions
            if func_name in ['print', 'len', 'isinstance', 'getattr', 'setattr', 'hasattr', 'open', 'range']:
                return

            context_lines = 5
            start = max(0, line_num - context_lines // 2 - 1)
            end = min(len(self.lines), line_num + context_lines // 2)
            
            context = "".join(self.lines[start:end])
            
            if not any(q.answer == func_name and q.context.strip() == context.strip() for q in self.questions):
                question = FunctionQuestion(context=context, answer=func_name)
                self.questions.append(question)
        self.generic_visit(node)


def create_questions_from_python_file(file_path: str, **kwargs) -> List[FunctionQuestion]:
    """
    Parses a Python file using the AST module and creates a list of FunctionQuestion objects.
    """
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
            lines = source_code.splitlines(True) # Keep endings for accurate context
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []

    try:
        tree = ast.parse(source_code)
        visitor = FuncCallVisitor(lines)
        visitor.visit(tree)
        return visitor.questions
    except SyntaxError as e:
        print(f"Error parsing Python code in {file_path}: {e}")
        return []

