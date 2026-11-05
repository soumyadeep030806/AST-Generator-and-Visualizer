"""
Abstract Syntax Tree (AST) Generator & Visualizer
Educational Python project using Tkinter and a recursive-descent parser.

Supported:
- Numbers (integers and decimals)
- Alphanumeric identifiers
- +, -, *, / operators
- Unary + and -
- Parentheses
- Simple assignments (x = expression)
- Visual tree, token list, AST JSON, and parser error messages

Run: python main.py
"""

import json
import re
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Token:
    kind: str
    value: str
    position: int


@dataclass
class ASTNode:
    kind: str
    value: str
    children: List["ASTNode"] = field(default_factory=list)

    def to_dict(self):
        return {
            "kind": self.kind,
            "value": self.value,
            "children": [child.to_dict() for child in self.children],
        }


class Lexer:
    """Converts source text into a stream of tokens."""

    TOKEN_RE = re.compile(
        r"(?P<NUMBER>(?:\d+\.\d+|\d+|\.\d+))"
        r"|(?P<IDENTIFIER>[A-Za-z_][A-Za-z0-9_]*)"
        r"|(?P<OP>[+\-*/=()])"
        r"|(?P<SPACE>\s+)"
        r"|(?P<INVALID>.)"
    )

    def tokenize(self, source: str) -> List[Token]:
        tokens = []
        for match in self.TOKEN_RE.finditer(source):
            kind = match.lastgroup
            value = match.group()
            pos = match.start()
            if kind == "SPACE":
                continue
            if kind == "INVALID":
                raise SyntaxError(
                    f"Unexpected character {value!r} at position {pos + 1}."
                )
            tokens.append(Token(kind, value, pos))
        tokens.append(Token("EOF", "EOF", len(source)))
        return tokens


class Parser:
    """Recursive-descent parser with precedence encoded in grammar methods."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def current(self) -> Token:
        return self.tokens[self.index]

    def accept(self, value: str) -> Optional[Token]:
        if self.current().value == value:
            token = self.current()
            self.index += 1
            return token
        return None

    def expect(self, value: str) -> Token:
        token = self.accept(value)
        if token is None:
            current = self.current()
            raise SyntaxError(
                f"Expected {value!r} at position {current.position + 1}, "
                f"but found {current.value!r}."
            )
        return token

    def parse(self) -> ASTNode:
        if self.current().kind == "EOF":
            raise SyntaxError("Input is empty. Enter an expression first.")
        root = self.parse_assignment()
        if self.current().kind != "EOF":
            token = self.current()
            raise SyntaxError(
                f"Unexpected token {token.value!r} at position {token.position + 1}."
            )
        return root

    def parse_assignment(self) -> ASTNode:
        left = self.parse_expression()
        if self.accept("="):
            if left.kind != "Identifier":
                raise SyntaxError("The left side of an assignment must be a variable name.")
            right = self.parse_assignment()
            return ASTNode("Assignment", "=", [left, right])
        return left

    def parse_expression(self) -> ASTNode:
        """Parse addition and subtraction, the lower-precedence arithmetic level."""
        node = self.parse_term()
        while self.current().value in ("+", "-"):
            operator = self.current().value
            self.index += 1
            right = self.parse_term()
            node = ASTNode("BinaryExpression", operator, [node, right])
        return node

    def parse_term(self) -> ASTNode:
        """Parse multiplication and division, which bind more tightly than + and -."""
        node = self.parse_factor()
        while self.current().value in ("*", "/"):
            operator = self.current().value
            self.index += 1
            right = self.parse_factor()
            node = ASTNode("BinaryExpression", operator, [node, right])
        return node

    def parse_factor(self) -> ASTNode:
        """Parse unary operators, values, identifiers, and parenthesized expressions."""
        token = self.current()

        if token.value in ("+", "-"):
            operator = token.value
            self.index += 1
            child = self.parse_factor()
            return ASTNode("UnaryExpression", operator, [child])

        if token.kind == "NUMBER":
            self.index += 1
            return ASTNode("Number", token.value)

        if token.kind == "IDENTIFIER":
            self.index += 1
            return ASTNode("Identifier", token.value)

        if self.accept("("):
            node = self.parse_assignment()
            if self.accept(")") is None:
                raise SyntaxError("Missing closing parenthesis ')'.")
            return node

        if token.kind == "EOF":
            raise SyntaxError("Unexpected end of input. Check for a missing operand or parenthesis.")

        raise SyntaxError(
            f"Expected a number, variable, unary operator, or '(', "
            f"but found {token.value!r} at position {token.position + 1}."
        )


class ASTVisualizerApp:
    BG = "#0b1020"
    PANEL = "#131d32"
    PANEL_LIGHT = "#192743"
    TEXT = "#edf2ff"
    MUTED = "#a4b2d0"
    ACCENT = "#86a1ff"
    CYAN = "#62e0d2"
    BORDER = "#2c3a59"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AST Studio | Generator & Visualizer")
        self.root.geometry("1180x790")
        self.root.minsize(900, 650)
        self.root.configure(bg=self.BG)

        self.current_ast: Optional[ASTNode] = None
        self.current_tokens: List[Token] = []
        self.active_view = tk.StringVar(value="Tree")

        self._configure_styles()
        self._build_ui()
        self.generate_ast()

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "TNotebook", background=self.PANEL, borderwidth=0
        )
        style.configure(
            "TNotebook.Tab", background=self.PANEL_LIGHT, foreground=self.TEXT,
            padding=(12, 7), font=("Segoe UI", 9, "bold")
        )
        style.map("TNotebook.Tab", background=[("selected", "#344b79")])
        style.configure(
            "Treeview", background="#0e1729", fieldbackground="#0e1729",
            foreground=self.TEXT, rowheight=27, borderwidth=0,
            font=("Consolas", 10)
        )
        style.configure(
            "Treeview.Heading", background="#243655", foreground=self.TEXT,
            font=("Segoe UI", 9, "bold")
        )

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=24, pady=(20, 14))
        logo = tk.Label(
            header, text="AST", bg="#86a1ff", fg="#081126",
            font=("Segoe UI", 16, "bold"), padx=12, pady=9
        )
        logo.pack(side="left", padx=(0, 12))
        title_box = tk.Frame(header, bg=self.BG)
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_box, text="AST Studio", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            title_box, text="Abstract Syntax Tree Generator & Visualizer",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w")
        tk.Label(
            header, text="PYTHON  •  TKINTER  •  RECURSIVE DESCENT",
            bg="#182847", fg="#cbd8ff", padx=12, pady=8,
            font=("Segoe UI", 8, "bold")
        ).pack(side="right", padx=(10, 0))

        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        body.grid_columnconfigure(0, weight=4, uniform="columns")
        body.grid_columnconfigure(1, weight=6, uniform="columns")
        body.grid_rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=self.PANEL, highlightbackground=self.BORDER, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        right = tk.Frame(body, bg=self.PANEL, highlightbackground=self.BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 0))

        self._section_header(left, "01  /  SOURCE CODE", "INPUT")
        tk.Label(
            left, text="Enter an arithmetic expression or assignment.",
            bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.source = tk.Text(
            left, height=7, wrap="word", undo=True, bg="#0a1120",
            fg="#e5edff", insertbackground="white", relief="flat",
            padx=12, pady=12, font=("Consolas", 12),
            highlightbackground=self.BORDER, highlightthickness=1
        )
        self.source.pack(fill="x", padx=16)
        self.source.insert("1.0", "result = (a + 12) * 3 - -b / 2")

        button_row = tk.Frame(left, bg=self.PANEL)
        button_row.pack(fill="x", padx=16, pady=12)
        self._button(button_row, "Generate AST  ↗", self.generate_ast, primary=True).pack(
            side="left", fill="x", expand=True, padx=(0, 6)
        )
        self._button(button_row, "Clear", self.clear_input).pack(side="left")

        tk.Label(left, text="QUICK EXAMPLES", bg=self.PANEL, fg=self.MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(5, 7))
        examples = [
            ("Precedence", "x = 4 + 5 * 2"),
            ("Parentheses", "total = (price + tax) * count"),
            ("Unary signs", "answer = -a + +b"),
            ("Simple expression", "(x + 7) / (y - 2)"),
        ]
        example_frame = tk.Frame(left, bg=self.PANEL)
        example_frame.pack(fill="x", padx=12)
        for i, (label, value) in enumerate(examples):
            btn = self._button(example_frame, label, lambda v=value: self.load_example(v))
            btn.grid(row=i // 2, column=i % 2, sticky="ew", padx=4, pady=4)
        example_frame.grid_columnconfigure(0, weight=1)
        example_frame.grid_columnconfigure(1, weight=1)

        self.status = tk.Label(
            left, text="Ready. Generate an AST to begin.", bg="#18233b",
            fg=self.MUTED, justify="left", anchor="w", wraplength=350,
            padx=11, pady=10, font=("Segoe UI", 9)
        )
        self.status.pack(fill="x", padx=16, pady=(14, 10))

        self._section_header(right, "02  /  VISUAL OUTPUT", "TREE • TOKENS • JSON")
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        tree_tab = tk.Frame(self.notebook, bg="#0e1729")
        token_tab = tk.Frame(self.notebook, bg="#0e1729")
        json_tab = tk.Frame(self.notebook, bg="#0e1729")
        self.notebook.add(tree_tab, text="AST Tree")
        self.notebook.add(token_tab, text="Tokens")
        self.notebook.add(json_tab, text="AST JSON")

        self.canvas = tk.Canvas(tree_tab, bg="#0e1729", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.draw_tree())

        token_frame = tk.Frame(token_tab, bg="#0e1729")
        token_frame.pack(fill="both", expand=True)
        self.token_table = ttk.Treeview(
            token_frame, columns=("type", "value", "position"),
            show="headings", height=12
        )
        for col, title, width in [
            ("type", "TOKEN TYPE", 120), ("value", "VALUE", 150), ("position", "POSITION", 90)
        ]:
            self.token_table.heading(col, text=title)
            self.token_table.column(col, width=width, anchor="w")
        token_scroll = ttk.Scrollbar(token_frame, orient="vertical", command=self.token_table.yview)
        self.token_table.configure(yscrollcommand=token_scroll.set)
        self.token_table.pack(side="left", fill="both", expand=True)
        token_scroll.pack(side="right", fill="y")

        json_frame = tk.Frame(json_tab, bg="#0e1729")
        json_frame.pack(fill="both", expand=True)
        self.json_text = tk.Text(
            json_frame, bg="#0e1729", fg="#dce7ff", relief="flat",
            font=("Consolas", 10), wrap="none", padx=12, pady=12
        )
        self.json_text.pack(side="left", fill="both", expand=True)
        json_scroll = ttk.Scrollbar(json_frame, orient="vertical", command=self.json_text.yview)
        self.json_text.configure(yscrollcommand=json_scroll.set)
        json_scroll.pack(side="right", fill="y")

        self.footer = tk.Label(
            right, text="Root = outermost operation  •  Leaves = values and variables",
            bg=self.PANEL, fg=self.MUTED, anchor="w", padx=12, pady=9,
            font=("Segoe UI", 9)
        )
        self.footer.pack(fill="x", side="bottom")

    def _section_header(self, parent, title, badge):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", padx=15, pady=(14, 0))
        tk.Label(row, text=title, bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, text=badge, bg="#1b2b49", fg="#c6d5ff",
                 font=("Segoe UI", 7, "bold"), padx=7, pady=4).pack(side="right")

    def _button(self, parent, text, command, primary=False):
        bg = "#86a1ff" if primary else "#223453"
        fg = "#081126" if primary else self.TEXT
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground="#9db2ff", activeforeground="#081126",
            relief="flat", borderwidth=0, cursor="hand2",
            font=("Segoe UI", 9, "bold"), padx=10, pady=9
        )

    def load_example(self, expression):
        self.source.delete("1.0", "end")
        self.source.insert("1.0", expression)
        self.generate_ast()

    def clear_input(self):
        self.source.delete("1.0", "end")
        self.current_ast = None
        self.current_tokens = []
        self.status.config(text="Input cleared. Enter an expression to continue.",
                           bg="#18233b", fg=self.MUTED)
        self._refresh_outputs()
        self.canvas.delete("all")
        self.canvas.create_text(
            25, 35, anchor="nw", fill=self.MUTED,
            text="Your syntax tree will appear here.\nEnter an expression and click Generate AST.",
            font=("Segoe UI", 11), justify="left"
        )

    def generate_ast(self):
        source = self.source.get("1.0", "end-1c")
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(source)
            parser = Parser(tokens)
            ast = parser.parse()
            self.current_tokens = tokens
            self.current_ast = ast
            self.status.config(
                text=f"Success: AST generated. {len(tokens)-1} tokens, "
                     f"{self.count_nodes(ast)} nodes, depth {self.tree_depth(ast)}.",
                bg="#122d27", fg="#a9f2c6"
            )
            self._refresh_outputs()
            self.draw_tree()
        except (SyntaxError, RecursionError) as exc:
            self.current_ast = None
            self.current_tokens = []
            self.status.config(
                text=f"Parse error: {exc}", bg="#351927", fg="#ffc2ca"
            )
            self._refresh_outputs()
            self.canvas.delete("all")
            self.canvas.create_text(
                22, 25, anchor="nw", fill="#ff9aaa",
                text="AST not generated.\n\nFix the input error shown on the left and try again.",
                font=("Segoe UI", 11), justify="left"
            )

    def _refresh_outputs(self):
        for item in self.token_table.get_children():
            self.token_table.delete(item)
        for token in self.current_tokens:
            if token.kind != "EOF":
                self.token_table.insert(
                    "", "end", values=(token.kind, token.value, token.position + 1)
                )
        self.json_text.delete("1.0", "end")
        if self.current_ast:
            self.json_text.insert("1.0", json.dumps(self.current_ast.to_dict(), indent=2))
        else:
            self.json_text.insert("1.0", "No AST available.")

    def count_nodes(self, node):
        return 1 + sum(self.count_nodes(child) for child in node.children)

    def tree_depth(self, node):
        if not node.children:
            return 1
        return 1 + max(self.tree_depth(child) for child in node.children)

    def _display_label(self, node):
        if node.kind == "Number":
            return node.value
        if node.kind == "Identifier":
            return node.value
        if node.kind == "UnaryExpression":
            return "unary " + node.value
        if node.kind == "Assignment":
            return "="
        return node.value

    def draw_tree(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        if not self.current_ast:
            return

        width = max(self.canvas.winfo_width(), 500)
        level_gap = 86
        node_height = 36
        leaf_gap = 84
        leaves = []

        def collect_leaves(node):
            if not node.children:
                leaves.append(node)
            else:
                for child in node.children:
                    collect_leaves(child)

        collect_leaves(self.current_ast)
        leaf_count = max(1, len(leaves))
        required_width = max(width, leaf_count * leaf_gap + 60)
        self.canvas.configure(scrollregion=(0, 0, required_width, self.tree_depth(self.current_ast) * level_gap + 80))
        x_positions = {}
        next_leaf = [35]

        def assign(node, depth):
            child_positions = [assign(child, depth + 1) for child in node.children]
            if not child_positions:
                x = next_leaf[0]
                next_leaf[0] += leaf_gap
            else:
                x = (child_positions[0][0] + child_positions[-1][0]) / 2
            y = 38 + depth * level_gap
            x_positions[id(node)] = (x, y)
            return x, y

        assign(self.current_ast, 0)
        # Center the layout when there is extra canvas width.
        used_width = max(70, next_leaf[0] - leaf_gap + 35)
        shift = max(0, (required_width - used_width) / 2)
        for key, (x, y) in list(x_positions.items()):
            x_positions[key] = (x + shift, y)

        def draw_edges(node):
            x1, y1 = x_positions[id(node)]
            for child in node.children:
                x2, y2 = x_positions[id(child)]
                self.canvas.create_line(
                    x1, y1 + node_height / 2, x2, y2 - node_height / 2,
                    fill="#63779f", width=2, smooth=True
                )
                draw_edges(child)

        def draw_nodes(node):
            x, y = x_positions[id(node)]
            label = self._display_label(node)
            node_width = max(64, min(150, len(label) * 8 + 24))
            left, top = x - node_width / 2, y - node_height / 2
            if node.kind == "Identifier":
                fill, outline = "#123d42", "#62cfc3"
            elif node.kind == "Number":
                fill, outline = "#382b51", "#b49bff"
            elif node.kind in ("BinaryExpression", "UnaryExpression", "Assignment"):
                fill, outline = "#233b68", "#86a1ff"
            else:
                fill, outline = "#1b2b49", "#5c78b7"
            self.canvas.create_rectangle(
                left, top, left + node_width, top + node_height,
                fill=fill, outline=outline, width=2
            )
            self.canvas.create_text(
                x, y, text=label, fill=self.TEXT,
                font=("Segoe UI", 9, "bold")
            )
            for child in node.children:
                draw_nodes(child)

        draw_edges(self.current_ast)
        draw_nodes(self.current_ast)


def main():
    root = tk.Tk()
    ASTVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
