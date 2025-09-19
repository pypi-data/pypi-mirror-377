"""
Test suite for EasyScript - Basic functionality tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easyscript import EasyScriptEvaluator


def test_easyscript():
    evaluator = EasyScriptEvaluator()

    print("=== EasyScript Basic Tests ===\n")

    # Test basic arithmetic
    print("Testing: 3+3")
    result = evaluator.evaluate("3+3")
    print(f"Result: {result}")
    assert result == 6

    # Test string concatenation with number
    print("\nTesting: \"hallo\" + 3")
    result = evaluator.evaluate('"hallo" + 3')
    print(f"Result: {result}")
    assert result == "hallo3"

    # Test string concatenation with variable
    print("\nTesting: \"hallo \" + day")
    result = evaluator.evaluate('"hallo " + day')
    print(f"Result: {result}")

    # Test built-in variables
    print(f"\nTesting built-in variables:")
    print(f"day = {evaluator.evaluate('day')}")
    print(f"month = {evaluator.evaluate('month')}")
    print(f"year = {evaluator.evaluate('year')}")

    # Test complex conditional
    print("\nTesting: if 3 > 1 and len(\"hallo\") > 3: return True")
    result = evaluator.evaluate('if 3 > 1 and len("hallo") > 3: return True')
    print(f"Result: {result}")
    assert result is True

    # Test more expressions
    print("\nAdditional tests:")

    # Simple comparison
    print(f"5 > 3: {evaluator.evaluate('5 > 3')}")

    # String length
    print(f'len("hello"): {evaluator.evaluate('len("hello")')}')

    # Complex arithmetic
    print(f"2 * 3 + 4: {evaluator.evaluate('2 * 3 + 4')}")

    # Boolean operations
    print(f"True and False: {evaluator.evaluate('True and False')}")
    print(f"True or False: {evaluator.evaluate('True or False')}")

    # Variable in arithmetic
    print(f"day * 2: {evaluator.evaluate('day * 2')}")

    # Conditional with variables
    print(f"if month > 6: return \"Second half\": {evaluator.evaluate('if month > 6: return \"Second half\"')}")

    # Test log function
    print(f"\nTesting log function:")
    print(f"log(\"Hello World\"): {evaluator.evaluate('log(\"Hello World\")')}")
    print(f"log(42): {evaluator.evaluate('log(42)')}")
    print(f"log(day): {evaluator.evaluate('log(day)')}")

    # Test regex operator
    print(f"\nTesting regex operator (~):")
    print(f'"hello" ~ "h.*o": {evaluator.evaluate('"hello" ~ "h.*o"')}')
    print(f'"test123" ~ "[0-9]+": {evaluator.evaluate('"test123" ~ "[0-9]+"')}')
    print(f'"abc" ~ "^[a-c]*$": {evaluator.evaluate('"abc" ~ "^[a-c]*$"')}')
    print(f'"xyz" ~ "^[a-c]*$": {evaluator.evaluate('"xyz" ~ "^[a-c]*$"')}')

    print("\n=== All EasyScript Basic Tests Completed! ===")


if __name__ == "__main__":
    test_easyscript()