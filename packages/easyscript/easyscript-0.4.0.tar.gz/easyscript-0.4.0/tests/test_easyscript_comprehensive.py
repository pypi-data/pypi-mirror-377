"""
Comprehensive unit test suite for EasyScript

This module contains thorough unit tests for all EasyScript functionality including:
- Tokenizer
- Parser
- Expression evaluation
- Assignment operations
- Built-in functions
- Error handling
- Edge cases
"""

import unittest
import sys
import os
import re
from typing import Any, Dict

# Add the parent directory to the path to import easyscript
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easyscript import EasyScriptEvaluator
from easyscript.easyscript import TokenType, Token
from test_helpers import LDAPUser


class TestEasyScriptBasics(unittest.TestCase):
    """Test basic EasyScript functionality"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.evaluator = EasyScriptEvaluator()

    def test_arithmetic_operations(self):
        """Test basic arithmetic operations"""
        test_cases = [
            ("3+3", 6),
            ("10-4", 6),
            ("2*3", 6),
            ("12/2", 6.0),
            ("2 + 3 * 4", 14),  # Order of operations
            ("(2 + 3) * 4", 20),  # Parentheses
            ("10 / 2 + 3", 8.0),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_string_operations(self):
        """Test string operations and concatenation"""
        test_cases = [
            ('"hello" + "world"', "helloworld"),
            ('"hello" + 123', "hello123"),
            ('123 + "world"', "123world"),
            ('"hello " + "world"', "hello world"),
            ('"Value: " + 42', "Value: 42"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_comparison_operations(self):
        """Test comparison operations"""
        test_cases = [
            ("5 > 3", True),
            ("3 > 5", False),
            ("5 >= 5", True),
            ("4 >= 5", False),
            ("3 < 5", True),
            ("5 < 3", False),
            ("5 <= 5", True),
            ("6 <= 5", False),
            ("5 == 5", True),
            ("5 == 3", False),
            ("5 != 3", True),
            ("5 != 5", False),
            ('"hello" == "hello"', True),
            ('"hello" == "world"', False),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_boolean_operations(self):
        """Test boolean operations"""
        test_cases = [
            ("true", True),
            ("false", False),
            ("True", True),
            ("False", False),
            ("true and true", True),
            ("true and false", False),
            ("false and true", False),
            ("false and false", False),
            ("true or true", True),
            ("true or false", True),
            ("false or true", True),
            ("false or false", False),
            ("true && true", True),  # JS style
            ("true && false", False),
            ("true || false", True),
            ("false || false", False),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_builtin_variables(self):
        """Test built-in variables"""
        import datetime
        now = datetime.datetime.now()
        
        self.assertEqual(self.evaluator.evaluate("day"), now.day)
        self.assertEqual(self.evaluator.evaluate("month"), now.month)
        self.assertEqual(self.evaluator.evaluate("year"), now.year)
        
        # Test using variables in expressions
        self.assertEqual(self.evaluator.evaluate("day + 0"), now.day)
        self.assertEqual(self.evaluator.evaluate("month * 1"), now.month)

    def test_builtin_functions(self):
        """Test built-in functions"""
        # Test len function
        test_cases = [
            ('len("hello")', 5),
            ('len("test")', 4),
            ('len("")', 0),
            ('len("unicode: 🎉")', 10),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_log_function(self):
        """Test log function (capture output)"""
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = self.evaluator.evaluate('log("test message")')
        
        output = f.getvalue().strip()
        self.assertEqual(output, "test message")
        self.assertEqual(result, "test message")  # log returns the value

    def test_regex_operator(self):
        """Test regex matching operator"""
        test_cases = [
            ('"hello" ~ "h.*o"', True),
            ('"hello" ~ "x.*"', False),
            ('"test123" ~ "[0-9]+"', True),
            ('"test" ~ "[0-9]+"', False),
            ('"abc" ~ "^[a-c]*$"', True),
            ('"xyz" ~ "^[a-c]*$"', False),
            ('"email@domain.com" ~ ".*@.*"', True),
            ('"invalid-email" ~ ".*@.*"', False),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_conditional_statements(self):
        """Test if statements"""
        test_cases = [
            ('if true: "yes"', "yes"),
            ('if false: "yes"', None),
            ('if 5 > 3: "greater"', "greater"),
            ('if 3 > 5: "greater"', None),
            ('if true: return "returned"', "returned"),
            ('if len("hello") > 3: "long"', "long"),
            ('if len("hi") > 3: "long"', None),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_complex_expressions(self):
        """Test complex nested expressions"""
        test_cases = [
            ('if 3 > 1 and len("hello") > 3: return True', True),
            ('if (5 + 3) > 6 and "test" ~ "t.*": "match"', "match"),
            ('"Result: " + (2 * 3 + 4)', "Result: 10"),
            ('len("hello") + len("world")', 10),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)


class TestEasyScriptTokenizer(unittest.TestCase):
    """Test the tokenizer functionality"""

    def setUp(self):
        self.evaluator = EasyScriptEvaluator()

    def test_number_tokenization(self):
        """Test tokenization of numbers"""
        tokens = self.evaluator.tokenize("123 45.67 0")
        
        # Filter out EOF token
        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        
        self.assertEqual(len(number_tokens), 3)
        self.assertEqual(number_tokens[0].value, 123)
        self.assertEqual(number_tokens[1].value, 45.67)
        self.assertEqual(number_tokens[2].value, 0)

    def test_string_tokenization(self):
        """Test tokenization of strings"""
        tokens = self.evaluator.tokenize('"hello" "world with spaces" ""')
        
        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        
        self.assertEqual(len(string_tokens), 3)
        self.assertEqual(string_tokens[0].value, "hello")
        self.assertEqual(string_tokens[1].value, "world with spaces")
        self.assertEqual(string_tokens[2].value, "")

    def test_identifier_tokenization(self):
        """Test tokenization of identifiers"""
        tokens = self.evaluator.tokenize("variable user_name test123 _private")
        
        identifier_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        
        self.assertEqual(len(identifier_tokens), 4)
        self.assertEqual(identifier_tokens[0].value, "variable")
        self.assertEqual(identifier_tokens[1].value, "user_name")
        self.assertEqual(identifier_tokens[2].value, "test123")
        self.assertEqual(identifier_tokens[3].value, "_private")

    def test_keyword_tokenization(self):
        """Test tokenization of keywords"""
        tokens = self.evaluator.tokenize("if return and or not True False true false")
        
        keyword_tokens = [t for t in tokens if t.type == TokenType.KEYWORD]
        
        expected_keywords = ["if", "return", "and", "or", "not", "True", "False", "true", "false"]
        actual_keywords = [t.value for t in keyword_tokens]
        
        self.assertEqual(actual_keywords, expected_keywords)

    def test_operator_tokenization(self):
        """Test tokenization of operators"""
        tokens = self.evaluator.tokenize("+ - * / > < >= <= == != ~ = && ||")
        
        operator_tokens = [t for t in tokens if t.type == TokenType.OPERATOR]
        
        # Note: && and || are converted to 'and' and 'or'
        expected_operators = ["+", "-", "*", "/", ">", "<", ">=", "<=", "==", "!=", "~", "=", "and", "or"]
        actual_operators = [t.value for t in operator_tokens]
        
        self.assertEqual(actual_operators, expected_operators)

    def test_punctuation_tokenization(self):
        """Test tokenization of punctuation"""
        tokens = self.evaluator.tokenize("( ) : , .")
        
        punct_tokens = [t for t in tokens if t.type in [TokenType.LPAREN, TokenType.RPAREN, 
                                                        TokenType.COLON, TokenType.COMMA, TokenType.DOT]]
        
        expected_types = [TokenType.LPAREN, TokenType.RPAREN, TokenType.COLON, TokenType.COMMA, TokenType.DOT]
        actual_types = [t.type for t in punct_tokens]
        
        self.assertEqual(actual_types, expected_types)


class TestEasyScriptObjectHandling(unittest.TestCase):
    """Test object property access and manipulation"""

    def setUp(self):
        self.evaluator = EasyScriptEvaluator()
        self.test_user = LDAPUser(
            cn='John Doe',
            uid='jdoe',
            mail='john.doe@company.com',
            givenName='John',
            sn='Doe',
            department='Engineering',
            title='Senior Developer'
        )
        self.user_variables = {'user': self.test_user}

    def test_property_access(self):
        """Test reading object properties"""
        test_cases = [
            ("user.cn", "John Doe"),
            ("user.uid", "jdoe"),
            ("user.mail", "john.doe@company.com"),
            ("user.givenName", "John"),
            ("user.sn", "Doe"),
            ("user.department", "Engineering"),
            ("user.title", "Senior Developer"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, self.user_variables)
                self.assertEqual(result, expected)

    def test_property_in_expressions(self):
        """Test using object properties in expressions"""
        test_cases = [
            ('len(user.cn)', 8),
            ('"Hello " + user.givenName', "Hello John"),
            ('user.givenName + " " + user.sn', "John Doe"),
            ('len(user.mail) > 10', True),
            ('user.department == "Engineering"', True),
            ('user.mail ~ ".*@.*"', True),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, self.user_variables)
                self.assertEqual(result, expected)

    def test_property_assignment(self):
        """Test assigning values to object properties"""
        # Test basic assignment
        result = self.evaluator.evaluate('user.department = "IT"', self.user_variables)
        self.assertEqual(result, "IT")
        self.assertEqual(self.test_user.department, "IT")
        
        # Test assignment with expression
        result = self.evaluator.evaluate('user.title = "Senior " + user.title', self.user_variables)
        self.assertEqual(result, "Senior Senior Developer")
        self.assertEqual(self.test_user.title, "Senior Senior Developer")
        
        # Test assignment with concatenation
        result = self.evaluator.evaluate('user.uid = user.uid + "_new"', self.user_variables)
        self.assertEqual(result, "jdoe_new")
        self.assertEqual(self.test_user.uid, "jdoe_new")

    def test_conditional_assignment(self):
        """Test assignments within conditional statements"""
        # Reset user for clean test
        self.test_user.department = "Engineering"
        
        result = self.evaluator.evaluate('if len(user.department) > 5: user.department = "ENGINEERING"', self.user_variables)
        self.assertEqual(result, "ENGINEERING")
        self.assertEqual(self.test_user.department, "ENGINEERING")

    def test_multiple_object_injection(self):
        """Test working with multiple injected objects"""
        class Config:
            def __init__(self):
                self.debug = True
                self.version = "1.0"
        
        config = Config()
        variables = {'user': self.test_user, 'config': config}
        
        # Test accessing different objects
        self.assertEqual(self.evaluator.evaluate("user.cn", variables), "John Doe")
        self.assertEqual(self.evaluator.evaluate("config.debug", variables), True)
        self.assertEqual(self.evaluator.evaluate("config.version", variables), "1.0")
        
        # Test assignment to different objects
        self.evaluator.evaluate('config.version = "2.0"', variables)
        self.assertEqual(config.version, "2.0")


class TestEasyScriptErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        self.evaluator = EasyScriptEvaluator()

    def test_undefined_variable_error(self):
        """Test error when accessing undefined variables"""
        with self.assertRaises(NameError):
            self.evaluator.evaluate("undefined_variable")

    def test_undefined_property_error(self):
        """Test error when accessing undefined properties"""
        test_obj = type('TestObj', (), {'name': 'test'})()
        variables = {'obj': test_obj}
        
        with self.assertRaises(AttributeError):
            self.evaluator.evaluate("obj.undefined_property", variables)

    def test_invalid_function_error(self):
        """Test error when calling undefined functions"""
        with self.assertRaises(NameError):
            self.evaluator.evaluate("undefined_function()")

    def test_function_argument_error(self):
        """Test error when calling functions with wrong number of arguments"""
        with self.assertRaises(TypeError):
            self.evaluator.evaluate("len()")  # len requires 1 argument
        
        with self.assertRaises(TypeError):
            self.evaluator.evaluate('len("hello", "world")')  # len takes only 1 argument

    def test_invalid_regex_error(self):
        """Test error with invalid regex patterns"""
        with self.assertRaises(ValueError):
            self.evaluator.evaluate('"test" ~ "["')  # Invalid regex

    def test_syntax_error(self):
        """Test syntax errors"""
        # Create a dummy object to test assignment syntax errors
        test_obj = type('TestObj', (), {'prop': 'value'})()
        variables = {'user': test_obj}
        
        with self.assertRaises(SyntaxError):
            self.evaluator.evaluate("user. = value", variables)  # Invalid assignment syntax
        
        # Test that direct variable assignment is not supported (only property assignment)
        with self.assertRaises(NameError):
            self.evaluator.evaluate("undefined_variable = value")  # Undefined variable

    def test_assignment_to_nonexistent_object(self):
        """Test assignment to properties of non-existent objects"""
        with self.assertRaises(NameError):
            self.evaluator.evaluate("nonexistent.property = value")

    def test_division_by_zero(self):
        """Test division by zero"""
        with self.assertRaises(ZeroDivisionError):
            self.evaluator.evaluate("10 / 0")

    def test_type_error_in_operations(self):
        """Test type errors in operations"""
        # Test that regex operator properly handles type conversion
        with self.assertRaises(TypeError):
            self.evaluator.evaluate('"test" ~ 123')  # Should raise TypeError for non-string regex pattern


class TestEasyScriptEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        self.evaluator = EasyScriptEvaluator()

    def test_empty_string(self):
        """Test operations with empty strings"""
        self.assertEqual(self.evaluator.evaluate('""'), "")
        self.assertEqual(self.evaluator.evaluate('len("")'), 0)
        self.assertEqual(self.evaluator.evaluate('"" + "hello"'), "hello")

    def test_zero_values(self):
        """Test operations with zero"""
        self.assertEqual(self.evaluator.evaluate("0"), 0)
        self.assertEqual(self.evaluator.evaluate("0 + 5"), 5)
        self.assertEqual(self.evaluator.evaluate("0 * 100"), 0)

    def test_whitespace_handling(self):
        """Test expressions with various whitespace"""
        test_cases = [
            ("  3  +  3  ", 6),
            ("\t5\t>\t3\t", True),
            ("\n\"hello\"\n", "hello"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=repr(expression)):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_nested_parentheses(self):
        """Test deeply nested expressions"""
        test_cases = [
            ("((3 + 2) * (4 - 1))", 15),
            ("(((5)))", 5),
            ('(("hello" + "world"))', "helloworld"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_boolean_edge_cases(self):
        """Test boolean edge cases"""
        # Test truthy/falsy behavior
        self.assertEqual(self.evaluator.evaluate("true and true and true"), True)
        self.assertEqual(self.evaluator.evaluate("false or false or false"), False)
        self.assertEqual(self.evaluator.evaluate("true and false or true"), True)

    def test_string_with_special_characters(self):
        """Test strings with special characters"""
        test_cases = [
            ('"hello\tworld"', "hello\tworld"),
            ('"line1\nline2"', "line1\nline2"),
            ('"quote: \'"', 'quote: \''),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)

    def test_large_numbers(self):
        """Test with large numbers"""
        self.assertEqual(self.evaluator.evaluate("1000000 + 1"), 1000001)
        self.assertEqual(self.evaluator.evaluate("999999999 * 1"), 999999999)

    def test_float_precision(self):
        """Test floating point operations"""
        result = self.evaluator.evaluate("0.1 + 0.2")
        self.assertAlmostEqual(result, 0.3, places=10)


class TestEasyScriptIntegration(unittest.TestCase):
    """Integration tests combining multiple features"""

    def setUp(self):
        self.evaluator = EasyScriptEvaluator()

    def test_ldap_user_transformation_scenario(self):
        """Test a realistic LDAP user transformation scenario"""
        user = LDAPUser(
            cn='John Smith',
            uid='jsmith',
            mail='j.smith@oldcompany.com',
            department='IT',
            title='Developer'
        )
        
        variables = {'user': user}
        
        # Simulate a series of transformations
        transformations = [
            'user.department = "25_" + user.department',
            'user.title = "Senior " + user.title',
            'user.mail = user.uid + "@newcompany.com"',
            'if len(user.cn) > 5: user.cn = user.cn + " (Updated)"'
        ]
        
        expected_results = [
            "25_IT",
            "Senior Developer", 
            "jsmith@newcompany.com",
            "John Smith (Updated)"
        ]
        
        for transformation, expected in zip(transformations, expected_results):
            with self.subTest(transformation=transformation):
                result = self.evaluator.evaluate(transformation, variables)
                self.assertEqual(result, expected)
        
        # Verify final state
        self.assertEqual(user.department, "25_IT")
        self.assertEqual(user.title, "Senior Developer")
        self.assertEqual(user.mail, "jsmith@newcompany.com")
        self.assertEqual(user.cn, "John Smith (Updated)")

    def test_complex_conditional_logic(self):
        """Test complex conditional logic with multiple branches"""
        user = LDAPUser(department='Engineering', title='Manager')
        variables = {'user': user}
        
        complex_expression = '''
        if user.department == "Engineering" and user.title ~ ".*Manager.*":
            user.department = "ENGINEERING_MGMT"
        '''
        
        # Remove extra whitespace and newlines for evaluation
        expression = ' '.join(complex_expression.split())
        result = self.evaluator.evaluate(expression, variables)
        
        self.assertEqual(result, "ENGINEERING_MGMT")
        self.assertEqual(user.department, "ENGINEERING_MGMT")

    def test_mathematical_expressions_with_variables(self):
        """Test complex mathematical expressions using built-in variables"""
        import datetime
        now = datetime.datetime.now()
        
        # Test date-based calculations
        test_cases = [
            ("year - 2000", now.year - 2000),
            ("month * day", now.month * now.day),
            ("if year > 2020: year - 2020", now.year - 2020 if now.year > 2020 else None),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression)
                self.assertEqual(result, expected)


class TestSliceOperations(unittest.TestCase):
    """Test slice operator functionality"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.evaluator = EasyScriptEvaluator()

    def test_string_slicing(self):
        """Test string slicing operations"""
        test_string = "hello world"
        variables = {"text": test_string}
        
        test_cases = [
            # Basic indexing
            ("text[0]", "h"),
            ("text[1]", "e"),
            ("text[-1]", "d"),
            ("text[6]", "w"),
            
            # Slice with start and end
            ("text[0:5]", "hello"),
            ("text[6:11]", "world"),
            ("text[1:4]", "ell"),
            ("text[0:2]", "he"),
            ("text[1:-1]", "ello worl"),  # From index 1 to second-to-last
            
            # Slice with no start ([:end])
            ("text[:5]", "hello"),
            ("text[:2]", "he"),
            ("text[:0]", ""),
            
            # Slice with no end ([start:])
            ("text[6:]", "world"),
            ("text[1:]", "ello world"),
            ("text[0:]", "hello world"),
            
            # Full slice
            ("text[:]", "hello world"),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, variables)
                self.assertEqual(result, expected)

    def test_list_slicing(self):
        """Test list slicing operations"""
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        variables = {"numbers": test_list}
        
        test_cases = [
            # Basic indexing
            ("numbers[0]", 1),
            ("numbers[4]", 5),
            ("numbers[-1]", 10),
            ("numbers[9]", 10),
            
            # Slice with start and end
            ("numbers[0:3]", [1, 2, 3]),
            ("numbers[2:5]", [3, 4, 5]),
            ("numbers[1:4]", [2, 3, 4]),
            ("numbers[1:-1]", [2, 3, 4, 5, 6, 7, 8, 9]),  # From index 1 to second-to-last
            
            # Slice with no start ([:end])
            ("numbers[:3]", [1, 2, 3]),
            ("numbers[:5]", [1, 2, 3, 4, 5]),
            ("numbers[:0]", []),
            
            # Slice with no end ([start:])
            ("numbers[7:]", [8, 9, 10]),
            ("numbers[3:]", [4, 5, 6, 7, 8, 9, 10]),
            ("numbers[0:]", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
            
            # Full slice
            ("numbers[:]", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, variables)
                self.assertEqual(result, expected)

    def test_complex_slice_expressions(self):
        """Test slicing with complex expressions for indices"""
        variables = {
            "text": "programming",
            "numbers": [10, 20, 30, 40, 50],
            "start": 2,
            "end": 7,
            "index": 3
        }
        
        test_cases = [
            # Using variables as indices
            ("text[start]", "o"),
            ("text[start:end]", "ogram"),
            ("text[:end]", "program"),
            ("text[start:]", "ogramming"),
            ("numbers[index]", 40),
            ("numbers[start:end]", [30, 40, 50]),
            
            # Using expressions as indices
            ("text[1+1]", "o"),  # text[2]
            ("text[start*2:end+1]", "ramm"),  # text[4:8]
            ("numbers[index-1]", 30),  # numbers[2]
            ("numbers[1:end-4]", [20, 30]),  # numbers[1:3]
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, variables)
                self.assertEqual(result, expected)

    def test_chained_operations(self):
        """Test slicing combined with other operations"""
        variables = {
            "words": ["hello", "world", "python", "programming"],
            "text": "EasyScript"
        }
        
        test_cases = [
            # Length of slice
            ('len(text[2:6])', 4),  # len("ySc")
            ('len(words[:2])', 2),  # len(["hello", "world"])
            
            # Slice of slice (chained slicing)
            ('text[1:8][2:5]', "ySc"),  # "asyScri"[2:5]
            
            # Property access on sliced results
            # Note: This would work if we had objects with properties in the list
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = self.evaluator.evaluate(expression, variables)
                self.assertEqual(result, expected)

    def test_slice_error_handling(self):
        """Test error handling for slice operations"""
        variables = {"text": "hello", "numbers": [1, 2, 3]}
        
        # Test cases that should raise errors
        error_cases = [
            ("text[", SyntaxError),  # Incomplete syntax
            ("text[1", SyntaxError),  # Missing closing bracket
            ("5[0]", TypeError),  # Cannot index numbers
        ]
        
        for expression, expected_error in error_cases:
            with self.subTest(expression=expression):
                with self.assertRaises(expected_error):
                    self.evaluator.evaluate(expression, variables)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)