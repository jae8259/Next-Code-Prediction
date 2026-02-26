from __future__ import annotations

from typing import List, Optional, Set, Tuple
from pathlib import Path

from src.review.review_note import FunctionQuestion

# Minimal Tree-sitter-based parser that reuses prebuilt grammars.
# No grammar repo, no compilation, no ABI mismatch headaches.
try:
    from tree_sitter_languages import get_parser, get_language
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Missing dependencies. Install with: pip install tree_sitter tree_sitter_languages"
    ) from e


# Keep the denylist conservative; callers can extend/override via kwargs.
DEFAULT_DENYLIST: Set[str] = {
    'printf', 'fprintf', 'sprintf', 'snprintf',
    'bzero', 'sizeof',
    'strlen', 'strncpy', 'strtol',
    'calloc', 'malloc', 'realloc', 'free',
    'memcpy', 'memmove', 'memset', 'memcmp',
    'ntohs', 'htons', 'inet_ntoa',
    'getopt', 'exit',
    'rdma_error', 'debug',
}


def _detect_lang(file_path: str) -> str:
    suf = Path(file_path).suffix.lower()
    if suf in {'.cc', '.cpp', '.cxx', '.hpp', '.hh', '.hxx'}:
        return 'cpp'
    return 'c'


def _read_lines_and_bytes(file_path: str) -> Tuple[list[str], bytes]:
    data = Path(file_path).read_bytes()
    # Context slicing: use UTF-8 text, replacing errors.
    text = data.decode('utf-8', errors='replace')
    lines = text.splitlines(keepends=True)
    # For node slicing: use the same bytes Tree-sitter parsed.
    code_bytes = text.encode('utf-8', errors='replace')
    return lines, code_bytes


def _extract_called_functions(code_bytes: bytes, lang: str) -> list[Tuple[str, int]]:
    """Return list of (callee_name, call_line_1_based) for free-function calls foo(...)."""
    parser = get_parser(lang)
    tree = parser.parse(code_bytes)
    root = tree.root_node
    language = get_language(lang)

    q = language.query(r"""
      (call_expression function: (identifier) @fn)
    """)

    out: list[Tuple[str, int]] = []
    for node, _ in q.captures(root):
        name = code_bytes[node.start_byte:node.end_byte].decode(
            'utf-8', errors='replace')
        line_1b = node.start_point[0] + 1
        out.append((name, line_1b))
    return out


def _extract_defined_functions(code_bytes: bytes, lang: str) -> Set[str]:
    """Return set of free-function names defined in this file (best-effort)."""
    parser = get_parser(lang)
    tree = parser.parse(code_bytes)
    root = tree.root_node
    language = get_language(lang)

    # Works well for C; usually ok for C++ free functions too.
    q = language.query(r"""
      (function_definition
        declarator: (function_declarator
          declarator: (identifier) @name))
    """)

    defs: Set[str] = set()
    for node, _ in q.captures(root):
        defs.add(code_bytes[node.start_byte:node.end_byte].decode(
            'utf-8', errors='replace'))
    return defs


def create_questions_from_file(
    file_path: str,
    *,
    context_lines: int = 5,
    subtract_defined: bool = True,
    denylist: Optional[Set[str]] = None,
    max_questions: Optional[int] = None,
) -> List[FunctionQuestion]:
    """Parse a C/C++ file and produce FunctionQuestion(context, answer).

    Default behavior matches your stated goal: "subtract functions".
    That is, it returns function calls that are NOT defined in the same file.

    - Extracts free-function calls: foo(...)
    - (Optional) subtract_defined=True => calls - defs
    """

    lines, code_bytes = _read_lines_and_bytes(file_path)
    lang = _detect_lang(file_path)

    deny = set(DEFAULT_DENYLIST)
    if denylist:
        deny |= set(denylist)

    calls = _extract_called_functions(code_bytes, lang)
    defs: Set[str] = set()
    if subtract_defined:
        defs = _extract_defined_functions(code_bytes, lang)

    half = max(0, context_lines // 2)
    questions: List[FunctionQuestion] = []
    seen: Set[Tuple[str, str]] = set()

    for func_name, line_num in calls:
        if not func_name or func_name in deny:
            continue
        # cheap macro-ish filter
        if func_name.isupper():
            continue
        if subtract_defined and func_name in defs:
            continue

        # line_num is 1-based, lines list is 0-based
        i = line_num - 1
        start = max(0, i - half)
        end = min(len(lines), i + half + 1)
        context = ''.join(lines[start:end])

        key = (func_name, context.strip())
        if key in seen:
            continue
        seen.add(key)

        questions.append(FunctionQuestion(context=context, answer=func_name))
        if max_questions is not None and len(questions) >= max_questions:
            break

    return questions
