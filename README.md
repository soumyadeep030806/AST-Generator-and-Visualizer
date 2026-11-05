# Abstract Syntax Tree Generator & Visualizer (Python)

A college-level Compiler Design project built with Python, Tkinter, and a recursive-descent parser. The app accepts a supported expression, tokenizes it, constructs an AST, and draws the tree.

## Requirements
- Python 3.9 or newer recommended
- Tkinter (included with most standard Windows Python installations)
- Visual Studio Code (recommended editor)

No third-party Python packages are required.

## Run in VS Code
1. Extract `AST_Generator_Visualizer_Python.zip`.
2. Open the extracted folder in VS Code (`File` → `Open Folder`).
3. Open `main.py`.
4. Select your Python interpreter using `Ctrl+Shift+P` → `Python: Select Interpreter`.
5. Open Terminal → New Terminal.
6. Run:

   ```bash
   python main.py
   ```

   On some Windows installations, use:

   ```bash
   py main.py
   ```

A desktop GUI window titled **AST Studio** should open.

## Example inputs
- `a+b`
- `a+b*c`
- `(a+b)*c`
- `x = 4 + 5 * 2`
- `result = (a + 12) * 3 - -b / 2`
- `answer = -a + +b`

## How it works
1. `Lexer.tokenize()` converts source text to tokens.
2. `Parser.parse_assignment()` handles simple assignments.
3. `Parser.parse_expression()` handles `+` and `-`.
4. `Parser.parse_term()` handles `*` and `/`, giving them higher precedence.
5. `Parser.parse_factor()` handles unary signs, numbers, identifiers, and parentheses.
6. `ASTNode` stores node type, value, and children.
7. `ASTVisualizerApp.draw_tree()` recursively draws edges and nodes on a Tkinter Canvas.
8. Tabs show the tree, tokens, and AST JSON.

## Grammar (simplified)
```text
assignment  -> expression ["=" assignment]
expression  -> term { ("+" | "-") term }
term        -> factor { ("*" | "/") factor }
factor      -> ("+" | "-") factor
             | NUMBER
             | IDENTIFIER
             | "(" assignment ")"
```

Assignment is only allowed when the left side is a single identifier.

## Error handling
The app reports empty input, invalid characters, missing operands, missing closing parentheses, unexpected trailing tokens, and invalid assignment targets.

## Limitations
This is an educational expression parser, not a full parser for Python/C/Java. It currently supports arithmetic expressions and a simple assignment form. It does not support function calls, arrays, strings, comparisons, logical operators, control flow, or multiple statements.

## Suggested test cases
| Input | Expected behavior |
|---|---|
| `a+b` | `+` root with `a` and `b` children |
| `a+b*c` | `+` root; `*` is the right child |
| `(a+b)*c` | `*` root; `+` is the left child |
| `(a+b` | Error: missing closing parenthesis |
| empty input | Error: input is empty |
| `a+*b` | Error: expected an operand |
| `2 @ 3` | Error: unexpected character |

## Future improvements
- Add zooming, panning, and scrollbars for large trees.
- Export tree diagrams as PNG or SVG.
- Add syntax highlighting and line/column diagnostics.
- Add more grammar rules and support multiple statements.
- Add automated unit tests and optional expression evaluation.

## Project files
- `main.py`: complete application.
- `README.md`: setup, design, grammar, test cases, and limitations.
