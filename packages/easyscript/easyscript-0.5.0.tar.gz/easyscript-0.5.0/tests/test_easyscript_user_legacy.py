"""
Test suite for EasyScript - User object and LDAP functionality tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easyscript import EasyScriptEvaluator
from test_helpers import LDAPUser


def test_easyscript_user_functionality():
    # Create a test user object - this shows how to inject objects
    test_user = LDAPUser(
        cn='John Doe',
        uid='jdoe',
        mail='john.doe@company.com',
        givenName='John',
        sn='Doe',
        department='Engineering',
        title='Senior Developer'
    )

    # Create evaluator and inject the user object
    evaluator = EasyScriptEvaluator()

    # Inject the user object into the evaluator's variables
    user_variables = {'user': test_user}

    print("=== EasyScript User Object Tests ===\n")

    # Test basic user property access
    print("Testing: user.cn")
    result = evaluator.evaluate("user.cn", user_variables)
    print(f"Result: {result}")

    print(f"\nTesting: user.mail")
    result = evaluator.evaluate("user.mail", user_variables)
    print(f"Result: {result}")

    # Test the main example: if len(user.cn) > 3: true
    print(f"\nTesting: if len(user.cn) > 3: true")
    result = evaluator.evaluate("if len(user.cn) > 3: true", user_variables)
    print(f"Result: {result}")

    # Test with lowercase true/false
    print(f"\nTesting lowercase booleans:")
    print(f"true: {evaluator.evaluate('true')}")
    print(f"false: {evaluator.evaluate('false')}")
    print(f"true and false: {evaluator.evaluate('true and false')}")
    print(f"true or false: {evaluator.evaluate('true or false')}")

    # Test conditional without return keyword
    print(f"\nTesting: if len(user.uid) > 2: true")
    result = evaluator.evaluate("if len(user.uid) > 2: true", user_variables)
    print(f"Result: {result}")

    # Test conditional with return keyword
    print(f"\nTesting: if len(user.department) > 5: return true")
    result = evaluator.evaluate("if len(user.department) > 5: return true", user_variables)
    print(f"Result: {result}")

    # Test more complex expressions
    print(f"\nTesting: if user.department == \"Engineering\" and len(user.cn) > 3: true")
    result = evaluator.evaluate('if user.department == "Engineering" and len(user.cn) > 3: true', user_variables)
    print(f"Result: {result}")

    # Test user properties
    print(f"\nUser object properties:")
    print(f"CN: {evaluator.evaluate('user.cn', user_variables)}")
    print(f"UID: {evaluator.evaluate('user.uid', user_variables)}")
    print(f"Mail: {evaluator.evaluate('user.mail', user_variables)}")
    print(f"Given Name: {evaluator.evaluate('user.givenName', user_variables)}")
    print(f"Surname: {evaluator.evaluate('user.sn', user_variables)}")
    print(f"Department: {evaluator.evaluate('user.department', user_variables)}")
    print(f"Title: {evaluator.evaluate('user.title', user_variables)}")

    # Test string operations with user data
    print(f"\nTesting string operations:")
    print(f'"Hello " + user.givenName: {evaluator.evaluate('"Hello " + user.givenName', user_variables)}')
    print(f'user.givenName + " " + user.sn: {evaluator.evaluate('user.givenName + " " + user.sn', user_variables)}')

    # Test length checks
    print(f"\nTesting length checks:")
    print(f'len(user.mail) > 10: {evaluator.evaluate("len(user.mail) > 10", user_variables)}')
    print(f'len(user.uid) < 10: {evaluator.evaluate("len(user.uid) < 10", user_variables)}')

    # Test log function with user data
    print(f"\nTesting log function with user data:")
    print(f'log(user.cn): {evaluator.evaluate("log(user.cn)", user_variables)}')
    print(f'log("User: " + user.givenName): {evaluator.evaluate('log("User: " + user.givenName)', user_variables)}')

    # Test regex operator with user data
    print(f"\nTesting regex operator with user data:")
    print(f'user.mail ~ ".*@.*": {evaluator.evaluate('user.mail ~ ".*@.*"', user_variables)}')
    print(f'user.cn ~ "John.*": {evaluator.evaluate('user.cn ~ "John.*"', user_variables)}')
    print(f'user.department ~ "^[A-Z]": {evaluator.evaluate('user.department ~ "^[A-Z]"', user_variables)}')
    print(f'user.uid ~ "^[a-z]+$": {evaluator.evaluate('user.uid ~ "^[a-z]+$"', user_variables)}')

    print("\n=== All EasyScript User Tests Completed! ===")


def test_custom_object_injection():
    """Demonstrate how to inject any custom object into EasyScript"""

    print("\n=== Custom Object Injection Demo ===\n")

    # Create a custom config object
    class Config:
        def __init__(self):
            self.debug = True
            self.api_url = "https://api.example.com"
            self.max_retries = 3
            self.timeout = 30

    # Create a custom product object
    class Product:
        def __init__(self, name, price, category):
            self.name = name
            self.price = price
            self.category = category
            self.active = True

    # Create instances
    config = Config()
    product = Product("Widget Pro", 29.99, "Electronics")

    # Create evaluator and inject multiple objects
    evaluator = EasyScriptEvaluator()

    # Test with config object
    config_vars = {'config': config}
    print("Testing config object injection:")
    print(f'config.debug: {evaluator.evaluate("config.debug", config_vars)}')
    print(f'config.api_url ~ ".*api.*": {evaluator.evaluate('config.api_url ~ ".*api.*"', config_vars)}')

    # Test with product object
    product_vars = {'product': product}
    print(f"\nTesting product object injection:")
    print(f'product.name: {evaluator.evaluate("product.name", product_vars)}')
    print(f'product.price > 20: {evaluator.evaluate("product.price > 20", product_vars)}')
    print(f'if product.active and product.price < 50: "Affordable": {evaluator.evaluate('if product.active and product.price < 50: "Affordable"', product_vars)}')

    # Test with multiple objects
    multi_vars = {'config': config, 'product': product, 'version': 1.0}
    print(f"\nTesting multiple object injection:")
    print(f'log("Product: " + product.name + ", Debug: " + config.debug): {evaluator.evaluate('log("Product: " + product.name + ", Debug: " + config.debug)', multi_vars)}')

    print("\n=== Custom Object Injection Demo Completed! ===")


def test_assignment_functionality():
    """Test the new assignment functionality"""
    
    print("\n=== Assignment Functionality Tests ===\n")
    
    # Create a test user object
    test_user = LDAPUser(
        cn='John Doe',
        uid='jdoe',
        mail='john.doe@company.com',
        givenName='John',
        sn='Doe',
        department='IT',
        title='Developer'
    )

    # Create evaluator and inject the user object
    evaluator = EasyScriptEvaluator()
    user_variables = {'user': test_user}

    print("=== Before Assignment ===")
    print(f'user.department: {evaluator.evaluate("user.department", user_variables)}')

    # Test the main assignment case: user.department = "25_" + user.department
    print(f"\nTesting: user.department = \"25_\" + user.department")
    result = evaluator.evaluate('user.department = "25_" + user.department', user_variables)
    print(f"Assignment result: {result}")
    
    print(f"\n=== After Assignment ===")
    print(f'user.department: {evaluator.evaluate("user.department", user_variables)}')

    # Test other assignment operations
    print(f"\nTesting: user.title = \"Senior \" + user.title")
    result = evaluator.evaluate('user.title = "Senior " + user.title', user_variables)
    print(f"Assignment result: {result}")
    print(f'user.title: {evaluator.evaluate("user.title", user_variables)}')

    # Test assignment with different data types
    print(f"\nTesting: user.cn = \"Updated Name\"")
    result = evaluator.evaluate('user.cn = "Updated Name"', user_variables)
    print(f"Assignment result: {result}")
    print(f'user.cn: {evaluator.evaluate("user.cn", user_variables)}')

    # Test assignment in conditional context
    print(f"\nTesting assignment in conditional:")
    print(f'if len(user.uid) > 2: user.uid = user.uid + "_new"')
    result = evaluator.evaluate('if len(user.uid) > 2: user.uid = user.uid + "_new"', user_variables)
    print(f"Conditional assignment result: {result}")
    print(f'user.uid: {evaluator.evaluate("user.uid", user_variables)}')

    print("\n=== Assignment Functionality Tests Completed! ===")


if __name__ == "__main__":
    test_easyscript_user_functionality()
    test_custom_object_injection()
    test_assignment_functionality()