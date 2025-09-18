"""
Test suite for EasyScript - User object and LDAP functionality tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easyscript import EasyScriptEvaluator


def test_easyscript_user_functionality():
    evaluator = EasyScriptEvaluator()

    print("=== EasyScript User Object Tests ===\n")

    # Test basic user property access
    print("Testing: user.cn")
    result = evaluator.evaluate("user.cn")
    print(f"Result: {result}")

    print(f"\nTesting: user.mail")
    result = evaluator.evaluate("user.mail")
    print(f"Result: {result}")

    # Test the main example: if len(user.cn) > 3: true
    print(f"\nTesting: if len(user.cn) > 3: true")
    result = evaluator.evaluate("if len(user.cn) > 3: true")
    print(f"Result: {result}")

    # Test with lowercase true/false
    print(f"\nTesting lowercase booleans:")
    print(f"true: {evaluator.evaluate('true')}")
    print(f"false: {evaluator.evaluate('false')}")
    print(f"true and false: {evaluator.evaluate('true and false')}")
    print(f"true or false: {evaluator.evaluate('true or false')}")

    # Test conditional without return keyword
    print(f"\nTesting: if len(user.uid) > 2: true")
    result = evaluator.evaluate("if len(user.uid) > 2: true")
    print(f"Result: {result}")

    # Test conditional with return keyword
    print(f"\nTesting: if len(user.department) > 5: return true")
    result = evaluator.evaluate("if len(user.department) > 5: return true")
    print(f"Result: {result}")

    # Test more complex expressions
    print(f"\nTesting: if user.department == \"Engineering\" and len(user.cn) > 3: true")
    result = evaluator.evaluate('if user.department == "Engineering" and len(user.cn) > 3: true')
    print(f"Result: {result}")

    # Test user properties
    print(f"\nUser object properties:")
    print(f"CN: {evaluator.evaluate('user.cn')}")
    print(f"UID: {evaluator.evaluate('user.uid')}")
    print(f"Mail: {evaluator.evaluate('user.mail')}")
    print(f"Given Name: {evaluator.evaluate('user.givenName')}")
    print(f"Surname: {evaluator.evaluate('user.sn')}")
    print(f"Department: {evaluator.evaluate('user.department')}")
    print(f"Title: {evaluator.evaluate('user.title')}")

    # Test string operations with user data
    print(f"\nTesting string operations:")
    print(f'"Hello " + user.givenName: {evaluator.evaluate('"Hello " + user.givenName')}')
    print(f'user.givenName + " " + user.sn: {evaluator.evaluate('user.givenName + " " + user.sn')}')

    # Test length checks
    print(f"\nTesting length checks:")
    print(f'len(user.mail) > 10: {evaluator.evaluate("len(user.mail) > 10")}')
    print(f'len(user.uid) < 10: {evaluator.evaluate("len(user.uid) < 10")}')

    # Test log function with user data
    print(f"\nTesting log function with user data:")
    print(f'log(user.cn): {evaluator.evaluate("log(user.cn)")}')
    print(f'log("User: " + user.givenName): {evaluator.evaluate('log("User: " + user.givenName)')}')

    # Test regex operator with user data
    print(f"\nTesting regex operator with user data:")
    print(f'user.mail ~ ".*@.*": {evaluator.evaluate('user.mail ~ ".*@.*"')}')
    print(f'user.cn ~ "John.*": {evaluator.evaluate('user.cn ~ "John.*"')}')
    print(f'user.department ~ "^[A-Z]": {evaluator.evaluate('user.department ~ "^[A-Z]"')}')
    print(f'user.uid ~ "^[a-z]+$": {evaluator.evaluate('user.uid ~ "^[a-z]+$"')}')

    print("\n=== All EasyScript User Tests Completed! ===")


if __name__ == "__main__":
    test_easyscript_user_functionality()