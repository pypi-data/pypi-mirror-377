"""
EasyScript - A simple scripting language that blends Python and JavaScript syntax

EasyScript is designed to be an easy-to-use scripting language for:
- Simple expression evaluation
- Business rule processing
- LDAP/user object manipulation
- Conditional logic

Features:
- JavaScript-style string concatenation (string + number)
- Python-style boolean operators (and, or) with JS alternatives (&&, ||)
- Object property access with dot notation (user.cn, user.mail)
- Built-in variables: day, month, year, user
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


class LDAPUser:
    """LDAP-like user object with common eDirectory attributes"""
    def __init__(self, **attributes):
        # Common LDAP/eDirectory attributes
        self.cn = attributes.get('cn', 'John Doe')  # Common Name
        self.uid = attributes.get('uid', 'jdoe')  # User ID
        self.mail = attributes.get('mail', 'john.doe@example.com')  # Email
        self.givenName = attributes.get('givenName', 'John')  # First Name
        self.sn = attributes.get('sn', 'Doe')  # Surname/Last Name
        self.ou = attributes.get('ou', 'Users')  # Organizational Unit
        self.telephoneNumber = attributes.get('telephoneNumber', '+1-555-0123')
        self.title = attributes.get('title', 'Software Engineer')
        self.department = attributes.get('department', 'IT')
        self.employeeNumber = attributes.get('employeeNumber', '12345')
        self.manager = attributes.get('manager', 'cn=Manager,ou=Users,o=company')
        self.homeDirectory = attributes.get('homeDirectory', '/home/jdoe')
        self.loginShell = attributes.get('loginShell', '/bin/bash')

        # Allow setting any additional attributes
        for key, value in attributes.items():
            if not hasattr(self, key):
                setattr(self, key, value)


class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    KEYWORD = "KEYWORD"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
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
        # Create a test user object
        test_user = LDAPUser(
            cn='John Doe',
            uid='jdoe',
            mail='john.doe@company.com',
            givenName='John',
            sn='Doe',
            department='Engineering',
            title='Senior Developer'
        )

        return {
            'day': now.day,
            'month': now.month,
            'year': now.year,
            'user': test_user
        }

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

            # Two-character operators
            if i < len(code) - 1:
                two_char = code[i:i+2]
                if two_char in ['>=', '<=', '==', '!=', '&&', '||']:
                    # Convert JS-style operators to Python-style
                    if two_char == '&&':
                        tokens.append(Token(TokenType.OPERATOR, 'and', i))
                    elif two_char == '||':
                        tokens.append(Token(TokenType.OPERATOR, 'or', i))
                    else:
                        tokens.append(Token(TokenType.OPERATOR, two_char, i))
                    i += 2
                    continue

            # Single-character tokens
            if code[i] == '(':
                tokens.append(Token(TokenType.LPAREN, '(', i))
            elif code[i] == ')':
                tokens.append(Token(TokenType.RPAREN, ')', i))
            elif code[i] == ':':
                tokens.append(Token(TokenType.COLON, ':', i))
            elif code[i] == ',':
                tokens.append(Token(TokenType.COMMA, ',', i))
            elif code[i] == '.':
                tokens.append(Token(TokenType.DOT, '.', i))
            elif code[i] in '+-*/><!~':
                tokens.append(Token(TokenType.OPERATOR, code[i], i))

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
        return self.parse_or_expression()

    def parse_or_expression(self) -> Any:
        left = self.parse_and_expression()

        while ((self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['or', '||']) or
               (self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'or')):
            self.consume_token()
            right = self.parse_and_expression()
            left = left or right

        return left

    def parse_and_expression(self) -> Any:
        left = self.parse_comparison()

        while ((self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['and', '&&']) or
               (self.current_token().type == TokenType.KEYWORD and self.current_token().value == 'and')):
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
        left = self.parse_primary()

        while self.current_token().type == TokenType.OPERATOR and self.current_token().value in ['*', '/']:
            op = self.current_token().value
            self.consume_token()
            right = self.parse_primary()

            if op == '*':
                left = left * right
            elif op == '/':
                left = left / right

        return left

    def parse_primary(self) -> Any:
        token = self.current_token()

        if token.type == TokenType.NUMBER:
            self.consume_token()
            return token.value

        elif token.type == TokenType.STRING:
            self.consume_token()
            return token.value

        elif token.type == TokenType.KEYWORD:
            if token.value in ['True', 'true']:
                self.consume_token()
                return True
            elif token.value in ['False', 'false']:
                self.consume_token()
                return False

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.consume_token()

            # Check for function call
            if self.current_token().type == TokenType.LPAREN:
                return self.parse_function_call(name)

            # Check for property access (dot notation)
            obj = None
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

            return obj

        elif token.type == TokenType.LPAREN:
            self.consume_token()
            result = self.parse_expression()
            if self.current_token().type == TokenType.RPAREN:
                self.consume_token()
            return result

        raise SyntaxError(f"Unexpected token: {token.value}")

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
        Evaluate an EasyScript expression or statement

        Args:
            code: The EasyScript code to evaluate
            variables: Optional dictionary of additional variables

        Returns:
            The result of the evaluation
        """
        if variables:
            self.variables.update(variables)

        self.tokens = self.tokenize(code)
        self.current_token_index = 0

        return self.parse_statement()