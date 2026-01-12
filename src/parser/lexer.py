"""
SQL lexer/tokenizer for LedgerLite.

Tokenizes SQL strings into a sequence of tokens.
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class TokenType(Enum):
    """Types of tokens."""
    # Keywords
    CREATE = "CREATE"
    TABLE = "TABLE"
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    JOIN = "JOIN"
    INNER = "INNER"
    ON = "ON"
    
    # Data types
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    
    # Constraints
    PRIMARY = "PRIMARY"
    KEY = "KEY"
    UNIQUE = "UNIQUE"
    
    # Operators
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    AND = "AND"
    OR = "OR"
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN_LITERAL = "BOOLEAN_LITERAL"
    NULL = "NULL"
    
    # Punctuation
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    DOT = "DOT"
    ASTERISK = "ASTERISK"
    
    # End of input
    EOF = "EOF"


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: str
    line: int = 1
    column: int = 1


class Lexer:
    """SQL lexer/tokenizer."""
    
    # SQL keywords
    KEYWORDS = {
        "CREATE": TokenType.CREATE,
        "TABLE": TokenType.TABLE,
        "INSERT": TokenType.INSERT,
        "INTO": TokenType.INTO,
        "VALUES": TokenType.VALUES,
        "SELECT": TokenType.SELECT,
        "FROM": TokenType.FROM,
        "WHERE": TokenType.WHERE,
        "UPDATE": TokenType.UPDATE,
        "SET": TokenType.SET,
        "DELETE": TokenType.DELETE,
        "JOIN": TokenType.JOIN,
        "INNER": TokenType.INNER,
        "ON": TokenType.ON,
        "INT": TokenType.INT,
        "TEXT": TokenType.TEXT,
        "FLOAT": TokenType.FLOAT,
        "BOOLEAN": TokenType.BOOLEAN,
        "TIMESTAMP": TokenType.TIMESTAMP,
        "PRIMARY": TokenType.PRIMARY,
        "KEY": TokenType.KEY,
        "UNIQUE": TokenType.UNIQUE,
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NULL": TokenType.NULL,
    }
    
    def __init__(self, text: str):
        """Initialize lexer with SQL text."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def advance(self) -> None:
        """Move to next character."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip SQL comments (-- style)."""
        if self.current_char == '-' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '-':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
    
    def read_identifier(self) -> str:
        """Read an identifier or keyword."""
        start_pos = self.pos
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            self.advance()
        return self.text[start_pos:self.pos]
    
    def read_string(self) -> str:
        """Read a string literal."""
        quote_char = self.current_char
        self.advance()  # Skip opening quote
        
        start_pos = self.pos
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\\':  # Handle escape sequences
                self.advance()
            self.advance()
        
        value = self.text[start_pos:self.pos]
        self.advance()  # Skip closing quote
        
        # Simple unescaping
        value = value.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")
        return value
    
    def read_number(self) -> tuple[str, bool]:
        """
        Read a number (integer or float).
        
        Returns:
            Tuple of (number_string, is_float)
        """
        start_pos = self.pos
        is_float = False
        
        while self.current_char is not None and self.current_char.isdigit():
            self.advance()
        
        if self.current_char == '.':
            is_float = True
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                self.advance()
        
        return self.text[start_pos:self.pos], is_float
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at characters without advancing."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None
    
    def tokenize(self) -> List[Token]:
        """Tokenize the input SQL text."""
        tokens = []
        
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if self.current_char == '-' and self.peek() == '-':
                self.skip_comment()
                continue
            
            # Single character tokens
            if self.current_char == ';':
                tokens.append(Token(TokenType.SEMICOLON, ';', self.line, self.column))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TokenType.LEFT_PAREN, '(', self.line, self.column))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TokenType.RIGHT_PAREN, ')', self.line, self.column))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(TokenType.DOT, '.', self.line, self.column))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TokenType.ASTERISK, '*', self.line, self.column))
                self.advance()
            
            # Operators
            elif self.current_char == '=':
                tokens.append(Token(TokenType.EQUALS, '=', self.line, self.column))
                self.advance()
            elif self.current_char == '!' and self.peek() == '=':
                tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line, self.column))
                self.advance()
                self.advance()
            elif self.current_char == '<':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LESS, '<', self.line, self.column))
                    self.advance()
            elif self.current_char == '>':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GREATER, '>', self.line, self.column))
                    self.advance()
            
            # String literals
            elif self.current_char in ("'", '"'):
                start_col = self.column
                value = self.read_string()
                tokens.append(Token(TokenType.STRING, value, self.line, start_col))
            
            # Numbers
            elif self.current_char.isdigit():
                start_col = self.column
                num_str, is_float = self.read_number()
                tokens.append(Token(TokenType.NUMBER, num_str, self.line, start_col))
            
            # Identifiers and keywords
            elif self.current_char.isalpha() or self.current_char == '_':
                start_col = self.column
                identifier = self.read_identifier()
                
                # Check if it's a keyword
                keyword_type = self.KEYWORDS.get(identifier.upper())
                if keyword_type:
                    tokens.append(Token(keyword_type, identifier.upper(), self.line, start_col))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line, start_col))
            
            else:
                raise SyntaxError(
                    f"Unexpected character '{self.current_char}' at line {self.line}, column {self.column}"
                )
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

