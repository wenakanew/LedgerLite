"""
SQL parser for LedgerLite.

Parses SQL statements into Abstract Syntax Tree (AST) nodes.
"""

from typing import List, Any, Dict, Optional

from src.parser.lexer import Lexer, Token, TokenType
from src.parser.ast import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
    UpdateStatement,
    DeleteStatement,
    JoinClause
)
from src.types import Column, DataType


class ParserError(Exception):
    """Raised when parsing fails."""
    pass


class SQLParser:
    """SQL parser that converts tokens into AST nodes."""
    
    def __init__(self, tokens: List[Token]):
        """Initialize parser with tokens."""
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
    
    def advance(self) -> None:
        """Move to next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type: TokenType) -> Token:
        """
        Expect a specific token type and advance.
        
        Args:
            token_type: Expected token type
            
        Returns:
            The current token
            
        Raises:
            ParserError: If token type doesn't match
        """
        if self.current_token is None or self.current_token.type != token_type:
            expected = token_type.value
            got = self.current_token.type.value if self.current_token else "EOF"
            raise ParserError(f"Expected {expected}, got {got}")
        
        token = self.current_token
        self.advance()
        return token
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peek ahead at tokens without advancing."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def parse(self) -> Any:
        """
        Parse SQL statement.
        
        Returns:
            AST node representing the statement
        """
        if self.current_token is None:
            raise ParserError("Empty input")
        
        # Determine statement type
        if self.current_token.type == TokenType.CREATE:
            return self.parse_create_table()
        elif self.current_token.type == TokenType.INSERT:
            return self.parse_insert()
        elif self.current_token.type == TokenType.SELECT:
            return self.parse_select()
        elif self.current_token.type == TokenType.UPDATE:
            return self.parse_update()
        elif self.current_token.type == TokenType.DELETE:
            return self.parse_delete()
        else:
            raise ParserError(f"Unexpected statement type: {self.current_token.type.value}")
    
    def parse_create_table(self) -> CreateTableStatement:
        """Parse CREATE TABLE statement."""
        self.expect(TokenType.CREATE)
        self.expect(TokenType.TABLE)
        
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LEFT_PAREN)
        
        columns = []
        while True:
            col_name = self.expect(TokenType.IDENTIFIER).value
            
            # Map token to DataType - data types are keywords
            type_map = {
                TokenType.INT: DataType.INT,
                TokenType.TEXT: DataType.TEXT,
                TokenType.FLOAT: DataType.FLOAT,
                TokenType.BOOLEAN: DataType.BOOLEAN,
                TokenType.TIMESTAMP: DataType.TIMESTAMP,
            }
            
            # Accept data type keywords (INT, TEXT, etc.)
            if self.current_token.type in type_map:
                data_type = type_map[self.current_token.type]
                self.advance()
            elif self.current_token.type == TokenType.IDENTIFIER:
                # Try to map identifier to data type (case-insensitive)
                identifier_upper = self.current_token.value.upper()
                keyword_to_type = {
                    "INT": TokenType.INT,
                    "TEXT": TokenType.TEXT,
                    "FLOAT": TokenType.FLOAT,
                    "BOOLEAN": TokenType.BOOLEAN,
                    "TIMESTAMP": TokenType.TIMESTAMP,
                }
                if identifier_upper in keyword_to_type:
                    data_type = type_map[keyword_to_type[identifier_upper]]
                    self.advance()
                else:
                    raise ParserError(f"Invalid data type: {self.current_token.value}")
            else:
                raise ParserError(f"Expected data type, got {self.current_token.type.value}")
            is_primary_key = False
            is_unique = False
            
            # Check for constraints
            while (self.current_token is not None and 
                   self.current_token.type != TokenType.COMMA and
                   self.current_token.type != TokenType.RIGHT_PAREN):
                if self.current_token.type == TokenType.PRIMARY:
                    self.advance()
                    self.expect(TokenType.KEY)
                    is_primary_key = True
                elif self.current_token.type == TokenType.UNIQUE:
                    self.advance()
                    is_unique = True
                else:
                    raise ParserError(f"Unexpected token in column definition: {self.current_token.type.value}")
            
            columns.append(Column(
                name=col_name,
                data_type=data_type,
                is_primary_key=is_primary_key,
                is_unique=is_unique
            ))
            
            if self.current_token.type == TokenType.RIGHT_PAREN:
                break
            self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RIGHT_PAREN)
        
        # Optional semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return CreateTableStatement(table_name=table_name, columns=columns)
    
    def parse_insert(self) -> InsertStatement:
        """Parse INSERT INTO statement."""
        self.expect(TokenType.INSERT)
        self.expect(TokenType.INTO)
        
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.VALUES)
        self.expect(TokenType.LEFT_PAREN)
        
        values = []
        while True:
            value = self.parse_value()
            values.append(value)
            
            if self.current_token.type == TokenType.RIGHT_PAREN:
                break
            self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RIGHT_PAREN)
        
        # Optional semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return InsertStatement(table_name=table_name, values=values)
    
    def parse_value(self) -> Any:
        """Parse a value (string, number, boolean, null)."""
        if self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return value
        elif self.current_token.type == TokenType.NUMBER:
            num_str = self.current_token.value
            self.advance()
            # Try to parse as int first, then float
            try:
                if '.' in num_str:
                    return float(num_str)
                return int(num_str)
            except ValueError:
                return float(num_str)
        elif self.current_token.type == TokenType.BOOLEAN_LITERAL:
            value = self.current_token.value.lower() == 'true'
            self.advance()
            return value
        elif self.current_token.type == TokenType.NULL:
            self.advance()
            return None
        else:
            raise ParserError(f"Unexpected value token: {self.current_token.type.value}")
    
    def parse_select(self) -> SelectStatement:
        """Parse SELECT statement."""
        self.expect(TokenType.SELECT)
        
        # Parse column list
        columns = []
        if self.current_token.type == TokenType.ASTERISK:
            columns = ["*"]
            self.advance()
        else:
            while True:
                # Handle table.column format
                if (self.current_token.type == TokenType.IDENTIFIER and
                    self.peek() and self.peek().type == TokenType.DOT):
                    table_name = self.current_token.value
                    self.advance()  # identifier
                    self.advance()  # dot
                    col_name = self.expect(TokenType.IDENTIFIER).value
                    columns.append(f"{table_name}.{col_name}")
                else:
                    col_name = self.expect(TokenType.IDENTIFIER).value
                    columns.append(col_name)
                
                if self.current_token.type != TokenType.COMMA:
                    break
                self.advance()
        
        self.expect(TokenType.FROM)
        table_name = self.expect(TokenType.IDENTIFIER).value
        
        # Optional WHERE clause
        where_clause = None
        if self.current_token and self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where_clause()
        
        # Optional JOINs
        joins = []
        while (self.current_token and 
               (self.current_token.type == TokenType.INNER or 
                self.current_token.type == TokenType.JOIN)):
            join = self.parse_join()
            joins.append(join)
        
        # Optional semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return SelectStatement(
            columns=columns,
            table_name=table_name,
            where_clause=where_clause,
            joins=joins if joins else None
        )
    
    def parse_where_clause(self) -> Dict[str, Any]:
        """Parse WHERE clause with support for AND/OR operators."""
        self.expect(TokenType.WHERE)
        return self.parse_or_condition()
    
    def parse_or_condition(self) -> Dict[str, Any]:
        """Parse OR condition (lowest precedence)."""
        left = self.parse_and_condition()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            self.advance()
            right = self.parse_and_condition()
            left = {
                "type": "OR",
                "left": left,
                "right": right
            }
        
        return left
    
    def parse_and_condition(self) -> Dict[str, Any]:
        """Parse AND condition (higher precedence than OR)."""
        left = self.parse_simple_condition()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            self.advance()
            right = self.parse_simple_condition()
            left = {
                "type": "AND",
                "left": left,
                "right": right
            }
        
        return left
    
    def parse_simple_condition(self) -> Dict[str, Any]:
        """Parse a simple condition: column operator value."""
        col_name = self.expect(TokenType.IDENTIFIER).value
        
        if self.current_token.type == TokenType.EQUALS:
            operator = "="
            self.advance()
        elif self.current_token.type == TokenType.NOT_EQUALS:
            operator = "!="
            self.advance()
        elif self.current_token.type == TokenType.GREATER:
            operator = ">"
            self.advance()
        elif self.current_token.type == TokenType.LESS:
            operator = "<"
            self.advance()
        elif self.current_token.type == TokenType.GREATER_EQUAL:
            operator = ">="
            self.advance()
        elif self.current_token.type == TokenType.LESS_EQUAL:
            operator = "<="
            self.advance()
        else:
            raise ParserError(f"Unsupported operator in WHERE clause: {self.current_token.type.value}")
        
        value = self.parse_value()
        
        return {
            "type": "CONDITION",
            "column": col_name,
            "operator": operator,
            "value": value
        }
    
    def parse_join(self) -> JoinClause:
        """Parse JOIN clause."""
        join_type = "INNER"
        if self.current_token.type == TokenType.INNER:
            self.advance()
        
        self.expect(TokenType.JOIN)
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ON)
        
        # Parse join condition: left_col = right_col (supports table.column format)
        # Left side
        if (self.current_token.type == TokenType.IDENTIFIER and
            self.peek() and self.peek().type == TokenType.DOT):
            left_table = self.current_token.value
            self.advance()  # identifier
            self.advance()  # dot
            left_col = self.expect(TokenType.IDENTIFIER).value
            left_col = f"{left_table}.{left_col}"
        else:
            left_col = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.EQUALS)
        
        # Right side
        if (self.current_token.type == TokenType.IDENTIFIER and
            self.peek() and self.peek().type == TokenType.DOT):
            right_table = self.current_token.value
            self.advance()  # identifier
            self.advance()  # dot
            right_col = self.expect(TokenType.IDENTIFIER).value
            right_col = f"{right_table}.{right_col}"
        else:
            right_col = self.expect(TokenType.IDENTIFIER).value
        
        return JoinClause(
            table_name=table_name,
            join_type=join_type,
            condition={left_col: right_col}
        )
    
    def parse_update(self) -> UpdateStatement:
        """Parse UPDATE statement."""
        self.expect(TokenType.UPDATE)
        table_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SET)
        
        set_clauses = {}
        while True:
            col_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.EQUALS)
            value = self.parse_value()
            set_clauses[col_name] = value
            
            if self.current_token.type != TokenType.COMMA:
                break
            self.advance()
        
        # Optional WHERE clause
        where_clause = None
        if self.current_token and self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where_clause()
        
        # Optional semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return UpdateStatement(
            table_name=table_name,
            set_clauses=set_clauses,
            where_clause=where_clause
        )
    
    def parse_delete(self) -> DeleteStatement:
        """Parse DELETE FROM statement."""
        self.expect(TokenType.DELETE)
        self.expect(TokenType.FROM)
        table_name = self.expect(TokenType.IDENTIFIER).value
        
        # Optional WHERE clause
        where_clause = None
        if self.current_token and self.current_token.type == TokenType.WHERE:
            where_clause = self.parse_where_clause()
        
        # Optional semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return DeleteStatement(
            table_name=table_name,
            where_clause=where_clause
        )


def parse_sql(sql: str) -> Any:
    """
    Parse a SQL statement string into an AST node.
    
    Args:
        sql: SQL statement string
        
    Returns:
        AST node representing the statement
        
    Raises:
        ParserError: If parsing fails
    """
    lexer = Lexer(sql)
    tokens = lexer.tokenize()
    parser = SQLParser(tokens)
    return parser.parse()

