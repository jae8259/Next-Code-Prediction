import re
from typing import List
from src.review_note import FunctionQuestion

# Functions to create questions for, based on the user's example
TARGET_FUNCTIONS = [
    "rdma_buffer_register",
    "ibv_post_recv",
    "rdma_accept",
    "process_rdma_cm_event",
    "rdma_ack_cm_event",
    "memcpy",
    "inet_ntoa",
]

def create_questions_from_file(file_path: str, context_lines: int = 5) -> List[FunctionQuestion]:
    """
    Parses a C file and creates a list of FunctionQuestion objects for targeted functions.
    """
    questions = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []

    for i, line in enumerate(lines):
        for func_name in TARGET_FUNCTIONS:
            # Simple regex to find function calls. This could be improved.
            # It looks for the function name followed by an opening parenthesis.
            if re.search(r'\b' + re.escape(func_name) + r'\b\s*\(', line):
                start = max(0, i - context_lines // 2)
                end = min(len(lines), i + context_lines // 2 + 1)
                
                context = "".join(lines[start:end])
                
                # To avoid creating duplicate questions if the same function is in the context window
                # of another found function, we check if we've already made a very similar question.
                if not any(q.answer == func_name and q.context.strip() == context.strip() for q in questions):
                    question = FunctionQuestion(context=context, answer=func_name)
                    questions.append(question)
    
    return questions
