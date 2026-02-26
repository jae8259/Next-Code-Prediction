import ast
import operator
import sys
import argparse
import os

# Blanking levels
BLANK_FUNCTION_NAME_ARGS = 1
BLANK_WHOLE_FUNCTION = 2

class CodeBlanker(ast.NodeVisitor):
    def __init__(self, original_code, blanking_level):
        self.original_code_lines = original_code.splitlines(keepends=True)
        self.blanks = []
        self.blanking_level = blanking_level

    def visit_FunctionDef(self, node):
        if self.blanking_level == BLANK_WHOLE_FUNCTION:
            # Blank the entire function definition
            self._add_blank_target(
                start_lineno=node.lineno - 1,
                start_col_offset=node.col_offset,
                end_lineno=node.end_lineno - 1,
                end_col_offset=node.end_col_offset,
                identifier=node.name,
                blank_type="whole_function"
            )
        elif self.blanking_level == BLANK_FUNCTION_NAME_ARGS:
            # Blank the function name only
            func_def_line = self.original_code_lines[node.lineno - 1]
            name_start_col = func_def_line.find(node.name, node.col_offset)
            name_end_col = name_start_col + len(node.name)

            self._add_blank_target(
                start_lineno=node.lineno - 1,
                start_col_offset=name_start_col,
                end_lineno=node.lineno - 1,
                end_col_offset=name_end_col,
                identifier=node.name,
                blank_type="function_name"
            )

            # Blank function arguments
            for arg_node in node.args.args:
                self._add_blank_target(
                    start_lineno=arg_node.lineno - 1,
                    start_col_offset=arg_node.col_offset,
                    end_lineno=arg_node.end_lineno - 1,
                    end_col_offset=arg_node.end_col_offset,
                    identifier=arg_node.arg,
                    blank_type="function_argument"
                )

        self.generic_visit(node)

    def _add_blank_target(self, start_lineno, start_col_offset, end_lineno, end_col_offset, identifier, blank_type):
        original_text_lines = []
        if start_lineno == end_lineno:
            original_text_lines.append(self.original_code_lines[start_lineno][start_col_offset:end_col_offset])
        else:
            original_text_lines.append(self.original_code_lines[start_lineno][start_col_offset:])
            for i in range(start_lineno + 1, end_lineno):
                original_text_lines.append(self.original_code_lines[i])
            # Handle cases where end_col_offset is 0, meaning it blanks till the end of line
            # or if it's a multi-line blank, it might end before the end of the line
            if end_col_offset > 0: # Only append if there's actual content to append from the end line
                original_text_lines.append(self.original_code_lines[end_lineno][:end_col_offset])
            else:
                # If end_col_offset is 0 and it's not a single line blank, it implies the rest of the line is blanked
                # This could happen if the blank ends exactly at the start of the last line
                pass

        original_text = "".join(original_text_lines).strip()

        self.blanks.append({
            'start_lineno': start_lineno,
            'start_col_offset': start_col_offset,
            'end_lineno': end_lineno,
            'end_col_offset': end_col_offset,
            'original_text': original_text,
            'identifier': identifier,
            'blank_type': blank_type,
            'placeholder': '_______'
        })


def generate_blank_quiz(code_string, blanking_level=BLANK_FUNCTION_NAME_ARGS):
    tree = ast.parse(code_string)
    blanker = CodeBlanker(code_string, blanking_level)
    blanker.visit(tree)

    # Sort blanks by their position in reverse order to avoid issues with
    # shifting indices when performing replacements.
    sorted_blanks = sorted(
        blanker.blanks,
        key=operator.itemgetter('start_lineno', 'start_col_offset'),
        reverse=True
    )

    blanked_code_lines = list(blanker.original_code_lines) # Make a mutable copy

    for blank in sorted_blanks:
        start_lineno = blank['start_lineno']
        start_col = blank['start_col_offset']
        end_lineno = blank['end_lineno']
        end_col = blank['end_col_offset']
        placeholder = blank['placeholder']

        if start_lineno == end_lineno:
            line = blanked_code_lines[start_lineno]
            blanked_code_lines[start_lineno] = \
                line[:start_col] + placeholder + line[end_col:]
        else:
            # Handle multi-line blanks
            # Replace the part of the starting line with the placeholder
            blanked_code_lines[start_lineno] = \
                blanked_code_lines[start_lineno][:start_col] + placeholder

            # Blank out full intermediate lines (if any)
            for i in range(start_lineno + 1, end_lineno):
                blanked_code_lines[i] = '\n' # Replace with a newline to signify blanked content, preserving line count

            # Replace the part of the ending line after the blank
            if end_col > 0:
                blanked_code_lines[end_lineno] = blanked_code_lines[end_lineno][end_col:]
            else: # If end_col is 0, it means the blank extends to the end of the line
                blanked_code_lines[end_lineno] = '\n' # Replace the whole line with a newline


    return "".join(blanked_code_lines), blanker.blanks

def run_quiz(blanked_code, blanks):
    score = 0
    total_blanks = len(blanks)

    print("\n--- Starting Quiz ---")
    print("Fill in the blanks. Type 'quit' to exit at any time.")
    print("-" * 30)

    # Create a dynamic representation of the code for progressive filling
    current_code_lines = blanked_code.splitlines(keepends=True)

    for i, blank in enumerate(blanks):
        # Clear screen for a cleaner presentation
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"\nBlank {i+1} of {total_blanks}:")
        print("--------------------")
        
        # Display current state of the code
        print("".join(current_code_lines))

        user_answer = input(f"Your answer for '{blank['identifier']}' ({blank['blank_type']}): ").strip()
        
        if user_answer.lower() == 'quit':
            print("Quiz exited.")
            return

        if user_answer == blank['original_text']:
            print("Correct!")
            score += 1
            # Update the current_code_lines to show the filled blank
            start_lineno = blank['start_lineno']
            start_col = blank['start_col_offset']
            end_lineno = blank['end_lineno']
            end_col = blank['end_col_offset']

            if start_lineno == end_lineno:
                line = current_code_lines[start_lineno]
                current_code_lines[start_lineno] = \
                    line[:start_col] + user_answer + line[end_col:]
            else:
                # For multi-line blanks, this is a simplified fill.
                # It replaces the placeholder on the first line and then adds original content.
                # A more complex solution might rebuild the block.
                current_code_lines[start_lineno] = \
                    current_code_lines[start_lineno][:start_col] + user_answer

                # Restore intermediate lines and end line content
                original_blank_lines = blank['original_text'].splitlines(keepends=True)
                for j in range(len(original_blank_lines)):
                    if (start_lineno + j) <= end_lineno:
                         current_code_lines[start_lineno + j] = original_blank_lines[j]
                    
        else:
            print(f"Incorrect. The correct answer was: '{blank['original_text']}'")
        input("Press Enter to continue...") # Pause for user to read feedback

    print("-" * 30)
    print(f"Quiz complete! Your final score: {score}/{total_blanks}")
    print("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and play a blank code quiz.")
    parser.add_argument("file", help="Path to the Python code file.")
    parser.add_argument("--level", type=int, default=BLANK_FUNCTION_NAME_ARGS,
                        help=f"Blanking level: {BLANK_FUNCTION_NAME_ARGS} for function names/args, "
                             f"{BLANK_WHOLE_FUNCTION} for whole functions. Default: {BLANK_FUNCTION_NAME_ARGS}")

    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"Generating quiz for '{args.file}' with blanking level {args.level}...")
    blanked_code, blanks = generate_blank_quiz(code_content, blanking_level=args.level)
    run_quiz(blanked_code, blanks)
