"""
EasyScript - A simple scripting language that blends Python and JavaScript syntax

EasyScript is designed to be an easy-to-use scripting language for:
- Simple expression evaluation
- Business rule processing
- LDAP/user object manipulation
- Conditional logic

Features:
- JavaScript-style string concatenation (string + number)
- Python-style boolean operators (and, or, not)
- Object property access with dot notation (user.cn, user.mail)
- Built-in variables: day, month, year
- Built-in functions: len(), log()
- Regex matching with ~ operator (string ~ pattern)
- Optional return keyword in conditionals
- Support for both True/False and true/false
"""

import re
import datetime
from enum import Enum
from typing import Any, Dict, List, Union, Optional
from dataclasses import dataclass



class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    KEYWORD = "KEYWORD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COLON = "COLON"
    COMMA = "COMMA"
    DOT = "DOT"
    EOF = "EOF"


@dataclass
class Token:
    type: TokenType
    value: Any
    position: int


class EasyScriptEvaluator:
    """Main EasyScript evaluation engine"""

    def __init__(self):
        self.tokens: List[Token] = []
        self.current_token_index = 0
        self.variables = self._initialize_builtin_variables()

    def _initialize_builtin_variables(self) -> Dict[str, Any]:
        now = datetime.datetime.now()

        return {
            'day': now.day,
            'month': now.month,
            'year': now.year
        }

    def _parse_statements(self, code: str) -> List[str]:
        """Parse statements from code, properly handling string literals that may contain newlines"""
        statements = []
        current_statement = ""
        in_string = False
        escape_next = False
        i = 0
        
        while i < len(code):
            char = code[i]
            
            if escape_next:
                current_statement += char
                escape_next = False
            elif char == '\\' and in_string:
                current_statement += char
                escape_next = True
            elif char == '"':
                current_statement += char
                in_string = not in_string
            elif char == '\n':
                if in_string:
                    # Newline inside string literal - part of the string
                    current_statement += char
                else:
                    # Newline outside string - end of statement
                    stmt = current_statement.strip()
                    if stmt and not stmt.startswith('#'):
                        statements.append(stmt)
                    current_statement = ""
            else:
                current_statement += char
            
            i += 1
        
        # Add the final statement if there is one
        stmt = current_statement.strip()
        if stmt and not stmt.startswith('#'):
            statements.append(stmt)
        
        return statements

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        i = 0

        while i < len(code):
            if code[i].isspace():
                i += 1
                continue

            # Numbers
            if code[i].isdigit():
                start = i
                while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                    i += 1
                value = code[start:i]
                tokens.append(Token(TokenType.NUMBER, float(value) if '.' in value else int(value), start))
                continue

            # Strings
            if code[i] == '"':
                start = i
                i += 1
                string_value = ""
                while i < len(code) and code[i] != '"':
                    if code[i] == '\\' and i + 1 < len(code):
                        # Handle escape sequences
                        escape_char = code[i + 1]
                        if escape_char == 'n':
                            string_value += '\n'
                        elif escape_char == 't':
                            string_value += '\t'
                        elif escape_char == 'r':
                            string_value += '\r'
                        elif escape_char == '\\':
                            string_value += '\\'
                        elif escape_char == '"':
                            string_value += '"'
                        elif escape_char == "'":
                            string_value += "'"
                        else:
                            # For unknown escape sequences, keep both characters
                            string_value += code[i] + escape_char
                        i += 2  # Skip both backslash and escape character
                    else:
                        string_value += code[i]
                        i += 1
                if i < len(code):
                    i += 1  # Skip closing quote
                tokens.append(Token(TokenType.STRING, string_value, start))
                continue

            # Identifiers and keywords
            if code[i].isalpha() or code[i] == '_':
                start = i
                while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                    i += 1
                value = code[start:i]

                if value in ['if', 'return', 'and', 'or', 'not', 'True', 'False', 'true', 'false']:
                    tokens.append(Token(TokenType.KEYWORD, value, start))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, value, start))
                continue

            # Comments - skip everything after # until end of line
            if code[i] == '#':
                # Skip to end of line or end of code
                while i < len(code) and code[i] != '\n':
                    i += 1
                # Don't increment i again at the end of the loop, 
                # as we either reached end of code or are at newline
                continue

            # Two-character operators
            if i < len(code) - 1:
                two_char = code[i:i+2]
                if two_char in ['>=', '<=', '==', '!=']:
                    tokens.append(Token(TokenType.OPERATOR, two_char, i))
                    i += 2
                    continue

            # Single-character tokens
            if code[i] == '(':
                tokens.append(Token(TokenType.LPAREN, '(', i))
            elif code[i] == ')':
                tokens.append(Token(TokenType.RPAREN, ')', i))
            elif code[i] == '[':
                tokens.append(Token(TokenType.LBRACKET, '[', i))
            elif code[i] == ']':
                tokens.append(Token(TokenType.RBRACKET, ']', i))
            elif code[i] == ':':
                tokens.append(Token(TokenType.COLON, ':', i))
            elif code[i] == ',':
                tokens.append(Token(TokenType.COMMA, ',', i))
            elif code[i] == '.':
                tokens.append(Token(TokenType.DOT, '.', i))
            elif code[i] in '+-*/><!~=':
                tokens.append(Token(TokenType.OPERATOR, code[i], i))
            elif code[i] in '&|':
                raise SyntaxError(f"Unsupported operator '{code[i]}' at position {i}. Use 'and' and 'or' instead of '&&' and '||'.")
            else:
                raise SyntaxError(f"Unexpected character '{code[i]}' at position {i}")

            i += 1

        tokens.append(Token(TokenType.EOF, None, len(code)))
        return tokens

    def current_token(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return self.tokens[-1]  # EOF token

    def consume_token(self):
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1

    def parse_expression(self) -> Any:
        return self.parse_assignment()

    def parse_assignment(self) -> Any:
        """Parse assignment expressions like a = 5 or object.property = value"""
        # Check if this looks like an assignment by looking ahead
        if self._is_assignment():
            return self._parse_assignment_expression()
        else:
            return self.parse_or_expression()

    def _is_assignment(self) -> bool:
        """Look ahead to see if this is an assignment expression"""
        saved_index = self.current_token_index
        
        try:
            # Check if it starts with an identifier
            if self.current_token().type != TokenType.IDENTIFIER:
                return False
            
            self.consume_token()  # consume identifier
            
            # Skip through optional property chain
            while self.current_token().type == TokenType.DOT:
                self.consume_token()  # consume '.'
                if self.current_token().type != TokenType.IDENTIFIER:
                    return False
                self.consume_token()  # consume property name
            
            # Check if next token is '='
            is_assignment = (self.current_token().type == TokenType.OPERATOR and 
                           self.current_token().value == '=')
            
            return is_assignment
            
        finally:
            # Restore position
            self.current_token_index = saved_index

    def _parse_assignment_expression(self) -> Any:
        """Parse a complete assignment expression"""
        # Parse the left side (identifier or object.property)
        if self.current_token().type != TokenType.IDENTIFIER:
            raise SyntaxError("Assignment target must start with an identifier")
        
        identifier_name = self.current_token().value
        self.consume_token()
        
        property_chain = []
        
        # Handle property access chain (e.g., user.cn, user.department)
        while self.current_token().type == TokenType.DOT:
            self.consume_token()  # consume '.'
            if self.current_token().type != TokenType.IDENTIFIER:
                raise SyntaxError("Expected property name after '.'")
            
            property_name = self.current_token().value
            property_chain.append(property_name)
            self.consume_token()
        
        # Consume the '=' operator
        if (self.current_token().type == TokenType.OPERATOR and 
            self.current_token().value == '='):
            self.consume_token()
        else:
            raise SyntaxError("Expected '=' in assignment")
        
        # Parse the right side (the value to assign)
        value = self.parse_or_expression()
        
        # Perform the assignment
        if not property_chain:
            # Direct variable assignment (e.g., a = 5)
            self.variables[identifier_name] = value
            return value
        else:
            # Object property assignment (e.g., user.department = "IT")
            if identifier_name not in self.variables:
                raise NameError(f"Variable '{identifier_name}' is not defined")
            
            obj = self.variables[identifier_name]
            return self._perform_assignment(obj, property_chain, value)

    def _perform_assignment(self, obj: Any, property_chain: List[str], value: Any) -> Any:
        """Perform the actual assignment operation"""
        # Navigate to the parent object (all but the last property)
        current_obj = obj
        for prop in property_chain[:-1]:
            if not hasattr(current_obj, prop):
                raise AttributeError(f"Object has no attribute '{prop}'")
            current_obj = getattr(current_obj, prop)
        
        # Set the final property
        final_property = property_chain[-1]
        setattr(current_obj, final_property, value)
        
        return value

    def parse_or_expression(self) -> Any:
        left = self.parse_and_expression()

        while (self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'or'):
            self.consume_token()
            right = self.parse_and_expression()
            left = left or right

        return left

    def parse_and_expression(self) -> Any:
        left = self.parse_comparison()

        while (self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'and'):
            self.consume_token()
            right = self.parse_comparison()
            left = left and right

        return left

    def parse_comparison(self) -> Any:
        left = self.parse_additive()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['>', '<', '>=', '<=', '==', '!=', '~']:
            op = self.current_token().value
            self.consume_token()
            right = self.parse_additive()

            if op == '>':
                left = left > right
            elif op == '<':
                left = left < right
            elif op == '>=':
                left = left >= right
            elif op == '<=':
                left = left <= right
            elif op == '==':
                left = left == right
            elif op == '!=':
                left = left != right
            elif op == '~':
                # Regex matching: left ~ right (string matches pattern)
                if not isinstance(left, str):
                    left = str(left)
                if not isinstance(right, str):
                    raise TypeError(f"Regex pattern must be a string, got {type(right).__name__}")
                try:
                    left = bool(re.search(right, left))
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{right}': {e}")

        return left

    def parse_additive(self) -> Any:
        left = self.parse_multiplicative()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['+', '-']:
            op = self.current_token().value
            self.consume_token()
            right = self.parse_multiplicative()

            if op == '+':
                # Handle JavaScript-like string concatenation
                if isinstance(left, str) or isinstance(right, str):
                    left = str(left) + str(right)
                else:
                    left = left + right
            elif op == '-':
                left = left - right

        return left

    def parse_multiplicative(self) -> Any:
        left = self.parse_unary()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['*', '/']:
            op = self.current_token().value
            self.consume_token()
            right = self.parse_unary()

            if op == '*':
                left = left * right
            elif op == '/':
                left = left / right

        return left

    def parse_unary(self) -> Any:
        """Handle unary operators like negative numbers and logical not"""
        token = self.current_token()
        
        if token.type == TokenType.OPERATOR and token.value == '-':
            self.consume_token()
            # Recursively parse the right side and negate it
            return -self.parse_unary()
        elif token.type == TokenType.KEYWORD and token.value == 'not':
            self.consume_token()
            # Recursively parse the right side and apply logical not
            return not self.parse_unary()
        else:
            return self.parse_primary()

    def parse_primary(self) -> Any:
        token = self.current_token()
        result = None

        if token.type == TokenType.NUMBER:
            self.consume_token()
            result = token.value

        elif token.type == TokenType.STRING:
            self.consume_token()
            result = token.value

        elif token.type == TokenType.KEYWORD:
            if token.value in ['True', 'true']:
                self.consume_token()
                result = True
            elif token.value in ['False', 'false']:
                self.consume_token()
                result = False

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.consume_token()

            # Check for function call
            if self.current_token().type == TokenType.LPAREN:
                result = self.parse_function_call(name)
            else:
                # Check for property access (dot notation)
                if name in self.variables:
                    obj = self.variables[name]
                else:
                    raise NameError(f"Variable '{name}' is not defined")

                # Handle property access chain (e.g., user.cn, user.mail)
                while self.current_token().type == TokenType.DOT:
                    self.consume_token()  # consume '.'
                    if self.current_token().type != TokenType.IDENTIFIER:
                        raise SyntaxError("Expected property name after '.'")

                    property_name = self.current_token().value
                    self.consume_token()

                    if hasattr(obj, property_name):
                        obj = getattr(obj, property_name)
                    else:
                        raise AttributeError(f"Object has no attribute '{property_name}'")

                result = obj

        elif token.type == TokenType.LPAREN:
            self.consume_token()
            result = self.parse_expression()
            if self.current_token().type == TokenType.RPAREN:
                self.consume_token()
            # result is already set

        if result is None:
            raise SyntaxError(f"Unexpected token: {token.value}")

        # Handle indexing and slicing for any result (numbers, strings, lists, etc.)
        while self.current_token().type == TokenType.LBRACKET:
            result = self.parse_indexing_or_slicing(result)

        return result

    def parse_indexing_or_slicing(self, obj: Any) -> Any:
        """Parse indexing (a[0]) or slicing (a[1:3], a[:5], a[2:]) operations"""
        self.consume_token()  # consume '['
        
        # Check if the object is subscriptable
        if not hasattr(obj, '__getitem__'):
            raise TypeError(f"'{type(obj).__name__}' object is not subscriptable")
        
        # Check if the first token is a colon (e.g., [:5])
        if self.current_token().type == TokenType.COLON:
            # This is a slice with no start index: [:end]
            self.consume_token()  # consume ':'
            
            if self.current_token().type == TokenType.RBRACKET:
                # This is just [:] - slice everything
                self.consume_token()  # consume ']'
                return obj[:]
            else:
                # Parse the end index - use parse_or_expression to avoid issues with :-
                end_expr = self.parse_or_expression()
                if self.current_token().type == TokenType.RBRACKET:
                    self.consume_token()  # consume ']'
                    return obj[:end_expr]
                else:
                    raise SyntaxError("Expected ']' after slice end index")
        
        # Parse the first expression (could be index or start of slice)
        first_expr = self.parse_or_expression()
        
        # Check if this is a slice (contains colon)
        if self.current_token().type == TokenType.COLON:
            self.consume_token()  # consume ':'
            
            if self.current_token().type == TokenType.RBRACKET:
                # This is a slice with no end index: [start:]
                self.consume_token()  # consume ']'
                return obj[first_expr:]
            else:
                # Parse the end index: [start:end] - use parse_or_expression to avoid issues with :-
                end_expr = self.parse_or_expression()
                if self.current_token().type == TokenType.RBRACKET:
                    self.consume_token()  # consume ']'
                    return obj[first_expr:end_expr]
                else:
                    raise SyntaxError("Expected ']' after slice end index")
        else:
            # This is simple indexing: [index]
            if self.current_token().type == TokenType.RBRACKET:
                self.consume_token()  # consume ']'
                return obj[first_expr]
            else:
                raise SyntaxError("Expected ']' after index")

    def parse_function_call(self, function_name: str) -> Any:
        self.consume_token()  # consume '('

        args = []
        while self.current_token().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            if self.current_token().type == TokenType.COMMA:
                self.consume_token()

        self.consume_token()  # consume ')'

        # Built-in functions
        if function_name == 'len':
            if len(args) != 1:
                raise TypeError(f"len() takes exactly one argument ({len(args)} given)")
            return len(args[0])
        elif function_name == 'log':
            if len(args) != 1:
                raise TypeError(f"log() takes exactly one argument ({len(args)} given)")
            value = args[0]
            print(value)
            return value
        else:
            raise NameError(f"Function '{function_name}' is not defined")

    def parse_statement(self) -> Any:
        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'if':
            return self.parse_if_statement()
        elif self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'return':
            self.consume_token()
            return self.parse_expression()
        else:
            return self.parse_expression()

    def parse_if_statement(self) -> Any:
        self.consume_token()  # consume 'if'

        condition = self.parse_expression()

        if self.current_token().type == TokenType.COLON:
            self.consume_token()

        # Handle optional return keyword
        if self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'return':
            self.consume_token()

        # If there's more content after the condition (and optional return), parse it as the return value
        if (self.current_token().type != TokenType.EOF):
            return_value = self.parse_expression()

            if condition:
                return return_value
            else:
                return None

        # If no return value specified, just return the condition result
        return condition

    def evaluate(self, code: str, variables: Optional[Dict[str, Any]] = None) -> Any:
        """
        Evaluate EasyScript code (single expression, statement, or multi-line script)

        Args:
            code: The EasyScript code to evaluate (single line or multi-line)
            variables: Optional dictionary of additional variables

        Returns:
            The result of the evaluation (for single statements) or the result of the last statement (for multi-line scripts)
        """
        if variables:
            self.variables.update(variables)

        # Parse statements properly, respecting string literals that may contain newlines
        statements = self._parse_statements(code)
        
        # Handle edge case of no statements
        if not statements:
            return None
        
        last_result = None
        
        # Execute each statement (works for both single and multiple statements)
        for statement in statements:
            try:
                self.tokens = self.tokenize(statement)
                self.current_token_index = 0
                last_result = self.parse_statement()
            except (NameError, AttributeError, TypeError, ValueError, SyntaxError, ZeroDivisionError) as e:
                # Re-raise specific exception types that tests expect
                raise e
            except Exception as e:
                # For other exceptions, provide enhanced error messages
                raise Exception(f"Error in statement '{statement}': {e}")
        
        return last_result