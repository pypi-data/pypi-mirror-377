# EasyScript

A simple scripting language interpreter that blends Python and JavaScript syntax, designed for easy expression evaluation, business rule processing, and LDAP/user object manipulation.

## Features

- **Hybrid Syntax**: Combines the best of Python and JavaScript syntax
- **JavaScript-style String Concatenation**: Automatic string conversion (e.g., `"hello" + 5` → `"hello5"`)
- **Python-style Boolean Operators**: Supports `and`, `or`, and `not` operators
- **Object Property Access**: Dot notation for accessing object properties (`user.cn`, `user.mail`)
- **Built-in Variables**: Pre-defined variables (`day`, `month`, `year`) with support for object injection
- **Built-in Functions**: Essential functions like `len()`, `log()`
- **Regex Matching**: Pattern matching with `~` operator (`string ~ pattern`)
- **Conditional Logic**: Support for `if` statements with optional `return` keyword
- **Mixed Boolean Values**: Supports both `True/False` and `true/false`
- **Comments**: Python-style comments using `#` character (everything after `#` is ignored)

## Quick Start

```python
from easyscript import EasyScriptEvaluator

# Create an evaluator instance
evaluator = EasyScriptEvaluator()

# Basic arithmetic
result = evaluator.evaluate("3 + 5")  # Returns: 8

# String concatenation
result = evaluator.evaluate('"Hello " + "World"')  # Returns: "Hello World"

# JavaScript-style string + number
result = evaluator.evaluate('"Count: " + 42')  # Returns: "Count: 42"

# Built-in variables
result = evaluator.evaluate("year")  # Returns: current year

# Object injection
class User:
    def __init__(self):
        self.cn = "John Doe"
        self.mail = "john@example.com"

user = User()
result = evaluator.evaluate("user.cn", {"user": user})  # Returns: "John Doe"

# Log function (prints and returns value)
result = evaluator.evaluate('log("Debug info")')  # Prints: Debug info, Returns: "Debug info"

# Regex matching
result = evaluator.evaluate('user.mail ~ ".*@.*"', {"user": user})  # Returns: True

# Conditional logic
result = evaluator.evaluate('if len(user.cn) > 3: return true', {"user": user})  # Returns: True

# Comments in expressions
result = evaluator.evaluate('5 + 3 # This is a comment')  # Returns: 8
result = evaluator.evaluate('len("hello") # Get string length')  # Returns: 5
```

## Syntax Examples

### Basic Operations
```javascript
// Arithmetic
3 + 5 * 2        // 13
10 / 2 - 1       // 4.0

// String operations
"Hello " + "World"           // "Hello World"
"Value: " + 42               // "Value: 42"
len("Hello")                 // 5
log("Debug: " + 42)          // Prints: Debug: 42, Returns: "Debug: 42"

// Comparisons
5 > 3                        // True
"abc" == "abc"               // True
len("test") >= 4             // True

// Regex matching
"hello" ~ "h.*o"             // True
"test123" ~ "[0-9]+"         // True
"email@domain.com" ~ ".*@.*" // True
```

### Boolean Logic
```javascript
// Python-style boolean operators
true and false               // False
true or false                // True
not true                     // False
not false                    // True

// Operator precedence (not has higher precedence)
not true and false           // False (equivalent to: (not true) and false)
not (true and false)         // True

// Mixed case support
True and False               // False
true and False               // False
not True                     // False
```

### Comments
```javascript
// Python-style comments using #
5 + 3 # This is a comment
"hello" + "world" # Comments can appear at end of line

# Full line comments are supported
5 + 3  # Result: 8

# Multiple comments work fine
# This is comment line 1
# This is comment line 2
5 * 2  # Result: 10

// Comments in multi-line expressions
5 # first number
+ 3 # second number
* 2 # multiply result
```

### Object Injection and Access
```javascript
// Create and inject custom objects
from easyscript import EasyScriptEvaluator

class User:
    def __init__(self):
        self.cn = "John Doe"
        self.mail = "john.doe@company.com"
        self.department = "Engineering"

user = User()
evaluator = EasyScriptEvaluator()

// Access injected object properties
evaluator.evaluate("user.cn", {"user": user})                      // "John Doe"
evaluator.evaluate("user.mail", {"user": user})                    // "john.doe@company.com"

// Use in expressions
evaluator.evaluate('"Hello " + user.cn', {"user": user})           // "Hello John Doe"
evaluator.evaluate('len(user.mail) > 10', {"user": user})          // True
evaluator.evaluate('user.mail ~ ".*@.*"', {"user": user})          // True (email validation)
```

### Conditional Statements
```javascript
// Basic conditional
if 5 > 3: true               // True

// With return keyword (optional)
if len(user.cn) > 3: return "Long name"    // "Long name"

// Complex conditions
if user.department == "Engineering" and len(user.cn) > 3: true
```

## Built-in Variables

EasyScript provides several built-in variables:

- `day`: Current day of the month
- `month`: Current month (1-12)
- `year`: Current year

Additional objects can be injected using the `variables` parameter.

## Use Cases

EasyScript is particularly useful for:

- **Business Rule Processing**: Evaluate complex business logic with simple syntax
- **LDAP/Directory Services**: Process user attributes and directory data
- **Configuration Management**: Dynamic configuration based on conditions
- **Data Validation**: Validate data with readable expressions
- **Template Processing**: Generate dynamic content based on user data

## Installation

Simply install the package or download the `easyscript.py` file:

```bash
pip install easyscript
```

```python
from easyscript import EasyScriptEvaluator
```

## Requirements

- Python 3.6+
- No external dependencies

## Running Tests

Run the included test suite to verify functionality:

```bash
# Basic functionality tests
python tests/test_easyscript.py

# Object injection examples (includes LDAPUser example class)
python tests/test_easyscript_user.py

# Or run all tests
python -m pytest tests/
```

**Note:** The `LDAPUser` class used in tests is just an example of object injection and is located in `tests/test_helpers.py`. It's not part of the main library.

## Object Injection

EasyScript's power comes from injecting your own objects and data:

```python
from easyscript import EasyScriptEvaluator

evaluator = EasyScriptEvaluator()

# Inject any Python object
class Config:
    def __init__(self):
        self.debug = True
        self.api_url = "https://api.example.com"

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.active = True

# Create instances
config = Config()
user = User("Alice", "alice@company.com")

# Inject multiple objects
variables = {
    'config': config,
    'user': user,
    'version': '1.0'
}

# Use in expressions
result = evaluator.evaluate('user.name + " - " + config.api_url', variables)
# Returns: "Alice - https://api.example.com"

result = evaluator.evaluate('if user.active and config.debug: "Debug mode"', variables)
# Returns: "Debug mode"

result = evaluator.evaluate('user.email ~ ".*@company\.com"', variables)
# Returns: True
```

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

This project is released under the MIT License. See the LICENSE file for details.

## Examples

### Real-world Usage Scenarios

**User Access Control**:
```javascript
if user.department == "IT" and len(user.cn) > 0: return true
```

**Dynamic Greetings**:
```javascript
if month >= 6 and month <= 8: return "Summer greetings, " + user.givenName
```

**Data Validation**:
```python
# Inject user object
user = User("john", "john@company.com")
variables = {"user": user}

result = evaluator.evaluate('if len(user.mail) > 5 and user.mail ~ ".*@.*": return true', variables)
```

**Pattern Matching**:
```python
result = evaluator.evaluate('if user.username ~ "^[a-z]+$": return "Valid username"', variables)
result = evaluator.evaluate('if user.mail ~ ".*@company\.com$": return "Company email"', variables)
```

**Configuration Logic**:
```javascript
if user.title == "Manager" or user.department == "Executive": return "admin"
```