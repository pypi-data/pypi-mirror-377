"""
PolyPrime Compiler - Fixed and working version
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"

    # Keywords
    FUNCTION = "function"
    LET = "let"
    CONST = "const"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    FOR = "for"
    WHILE = "while"

    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    ASSIGN = "="

    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SEMICOLON = ";"
    COMMA = ","

    # Special
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

class Lexer:
    """Tokenizer for PolyPrime source code"""

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Convert source to tokens"""
        while self.pos < len(self.source):
            self._skip_whitespace()

            if self.pos >= len(self.source):
                break

            char = self.source[self.pos]

            # Numbers
            if char.isdigit():
                self._read_number()
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self._read_identifier()
            # Strings
            elif char in '"\'':
                self._read_string()
            # Operators and delimiters
            else:
                self._read_operator()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _skip_whitespace(self):
        """Skip whitespace and comments"""
        while self.pos < len(self.source):
            char = self.source[self.pos]

            if char in ' \t\r\n':
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
            # Skip comments
            elif self.pos + 1 < len(self.source) and self.source[self.pos:self.pos+2] == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
            else:
                break

    def _read_number(self):
        """Read a number token"""
        start = self.pos
        start_col = self.column

        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            self.column += 1
            self.pos += 1

        value = self.source[start:self.pos]
        num_value = float(value) if '.' in value else int(value)
        self.tokens.append(Token(TokenType.NUMBER, num_value, self.line, start_col))

    def _read_identifier(self):
        """Read identifier or keyword"""
        start = self.pos
        start_col = self.column

        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.column += 1
            self.pos += 1

        value = self.source[start:self.pos]

        # Check if it's a keyword
        keywords = {
            'function': TokenType.FUNCTION,
            'let': TokenType.LET,
            'const': TokenType.CONST,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'return': TokenType.RETURN,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
        }

        token_type = keywords.get(value, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, value, self.line, start_col))

    def _read_string(self):
        """Read string literal"""
        start_col = self.column
        quote = self.source[self.pos]
        self.pos += 1
        self.column += 1

        value = ""
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            if self.source[self.pos] == '\\' and self.pos + 1 < len(self.source):
                self.pos += 1
                self.column += 1
                next_char = self.source[self.pos]
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                else:
                    value += next_char
            else:
                value += self.source[self.pos]
            self.pos += 1
            self.column += 1

        # Skip closing quote
        if self.pos < len(self.source):
            self.pos += 1
            self.column += 1

        self.tokens.append(Token(TokenType.STRING, value, self.line, start_col))

    def _read_operator(self):
        """Read operator or delimiter"""
        start_col = self.column
        char = self.source[self.pos]

        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.ASSIGN,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
        }

        if char in single_char_tokens:
            self.tokens.append(Token(single_char_tokens[char], char, self.line, start_col))

        # Always advance to prevent infinite loop
        self.pos += 1
        self.column += 1

class Parser:
    """Simple parser for PolyPrime"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Dict[str, Any]:
        """Parse tokens into AST"""
        statements = []

        while self.pos < len(self.tokens) and self.tokens[self.pos].type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return {"type": "Program", "statements": statements}

    def _current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None, 0, 0)

    def _advance(self) -> Token:
        token = self._current()
        self.pos += 1
        return token

    def _parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a single statement"""
        token = self._current()

        if token.type == TokenType.FUNCTION:
            return self._parse_function()
        elif token.type == TokenType.LET:
            return self._parse_variable()
        elif token.type == TokenType.RETURN:
            return self._parse_return()
        else:
            # Skip unknown tokens
            self._advance()
            return None

    def _parse_function(self) -> Dict[str, Any]:
        """Parse function declaration"""
        self._advance()  # Skip 'function'

        name = self._advance().value  # Function name

        # Skip parentheses and parameters for now
        while self._current().type != TokenType.LBRACE:
            self._advance()

        self._advance()  # Skip '{'

        # Parse body
        body = []
        while self._current().type != TokenType.RBRACE and self._current().type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                body.append(stmt)

        self._advance()  # Skip '}'

        return {
            "type": "Function",
            "name": name,
            "params": [],
            "body": body
        }

    def _parse_variable(self) -> Dict[str, Any]:
        """Parse variable declaration"""
        self._advance()  # Skip 'let'

        name = self._advance().value

        # Skip to value
        if self._current().type == TokenType.ASSIGN:
            self._advance()
            value = self._advance().value
        else:
            value = None

        # Skip semicolon if present
        if self._current().type == TokenType.SEMICOLON:
            self._advance()

        return {
            "type": "Variable",
            "name": name,
            "value": value
        }

    def _parse_return(self) -> Dict[str, Any]:
        """Parse return statement"""
        self._advance()  # Skip 'return'

        value = None
        if self._current().type != TokenType.SEMICOLON:
            value = self._advance().value

        # Skip semicolon
        if self._current().type == TokenType.SEMICOLON:
            self._advance()

        return {
            "type": "Return",
            "value": value
        }

class CodeGenerator:
    """Generate target code from AST"""

    def __init__(self):
        pass

    def generate_python(self, ast: Dict[str, Any]) -> str:
        """Generate Python code"""
        output = []

        for stmt in ast.get("statements", []):
            if stmt["type"] == "Function":
                output.append(self._gen_python_function(stmt))
            elif stmt["type"] == "Variable":
                output.append(self._gen_python_variable(stmt))

        return "\n".join(output)

    def _gen_python_function(self, func: Dict[str, Any]) -> str:
        """Generate Python function"""
        lines = [f"def {func['name']}():"]

        if func['body']:
            for stmt in func['body']:
                if stmt['type'] == 'Variable':
                    lines.append(f"    {stmt['name']} = {stmt['value']}")
                elif stmt['type'] == 'Return':
                    lines.append(f"    return {stmt['value']}")
        else:
            lines.append("    pass")

        return "\n".join(lines)

    def _gen_python_variable(self, var: Dict[str, Any]) -> str:
        """Generate Python variable"""
        if var['value'] is not None:
            return f"{var['name']} = {var['value']}"
        return f"{var['name']} = None"

    def generate_javascript(self, ast: Dict[str, Any]) -> str:
        """Generate JavaScript code"""
        output = []

        for stmt in ast.get("statements", []):
            if stmt["type"] == "Function":
                output.append(self._gen_js_function(stmt))
            elif stmt["type"] == "Variable":
                output.append(self._gen_js_variable(stmt))

        return "\n".join(output)

    def _gen_js_function(self, func: Dict[str, Any]) -> str:
        """Generate JavaScript function"""
        lines = [f"function {func['name']}() {{"]

        for stmt in func['body']:
            if stmt['type'] == 'Variable':
                lines.append(f"    let {stmt['name']} = {stmt['value']};")
            elif stmt['type'] == 'Return':
                lines.append(f"    return {stmt['value']};")

        lines.append("}")
        return "\n".join(lines)

    def _gen_js_variable(self, var: Dict[str, Any]) -> str:
        """Generate JavaScript variable"""
        if var['value'] is not None:
            return f"let {var['name']} = {var['value']};"
        return f"let {var['name']};"

class Compiler:
    """Main PolyPrime compiler"""

    def compile(self, source: str, target: str = "python") -> str:
        """Compile PolyPrime source to target language"""
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        # Generate code
        generator = CodeGenerator()

        if target == "python":
            return generator.generate_python(ast)
        elif target == "javascript":
            return generator.generate_javascript(ast)
        else:
            raise ValueError(f"Unsupported target: {target}")

    def compile_to_all(self, source: str) -> Dict[str, str]:
        """Compile to all supported targets"""
        return {
            "python": self.compile(source, "python"),
            "javascript": self.compile(source, "javascript"),
        }