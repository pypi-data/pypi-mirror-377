# EasyScript

A simple scripting language interpreter that blends Python and JavaScript syntax, designed for easy expression evaluation, business rule processing, and LDAP/user object manipulation.

## Features

- **Hybrid Syntax**: Combines the best of Python and JavaScript syntax
- **JavaScript-style String Concatenation**: Automatic string conversion (e.g., `"hello" + 5` → `"hello5"`)
- **Flexible Boolean Operators**: Supports both Python (`and`, `or`) and JavaScript (`&&`, `||`) style operators
- **Object Property Access**: Dot notation for accessing object properties (`user.cn`, `user.mail`)
- **Built-in Variables**: Pre-defined variables for common use cases (`day`, `month`, `year`, `user`)
- **Built-in Functions**: Essential functions like `len()`, `log()`
- **Regex Matching**: Pattern matching with `~` operator (`string ~ pattern`)
- **Conditional Logic**: Support for `if` statements with optional `return` keyword
- **Mixed Boolean Values**: Supports both `True/False` and `true/false`

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

# User object access
result = evaluator.evaluate("user.cn")  # Returns: "John Doe"

# Log function (prints and returns value)
result = evaluator.evaluate('log("Debug info")')  # Prints: Debug info, Returns: "Debug info"

# Regex matching
result = evaluator.evaluate('user.mail ~ ".*@.*"')  # Returns: True

# Conditional logic
result = evaluator.evaluate('if len(user.cn) > 3: return true')  # Returns: True
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
// Python-style
true and false               // False
true or false                // True

// JavaScript-style
true && false                // False
true || false                // True

// Mixed case support
True and False               // False
true and False               // False
```

### User Object Access
```javascript
// Access user properties
user.cn                      // "John Doe"
user.mail                    // "john.doe@company.com"
user.department              // "Engineering"

// Use in expressions
"Hello " + user.givenName    // "Hello John"
len(user.uid) > 3            // True
user.mail ~ ".*@.*"          // True (email validation)
user.cn ~ "John.*"           // True (starts with "John")
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

EasyScript provides several built-in variables for common use cases:

- `day`: Current day of the month
- `month`: Current month (1-12)
- `year`: Current year
- `user`: LDAP-like user object with common attributes

## User Object Attributes

The built-in `user` object includes common LDAP/eDirectory attributes:

- `cn`: Common Name (e.g., "John Doe")
- `uid`: User ID (e.g., "jdoe")
- `mail`: Email address
- `givenName`: First name
- `sn`: Surname/last name
- `department`: Department name
- `title`: Job title
- `ou`: Organizational Unit
- `telephoneNumber`: Phone number
- `employeeNumber`: Employee ID
- `manager`: Manager DN
- `homeDirectory`: Home directory path
- `loginShell`: Login shell

## Use Cases

EasyScript is particularly useful for:

- **Business Rule Processing**: Evaluate complex business logic with simple syntax
- **LDAP/Directory Services**: Process user attributes and directory data
- **Configuration Management**: Dynamic configuration based on conditions
- **Data Validation**: Validate data with readable expressions
- **Template Processing**: Generate dynamic content based on user data

## Installation

Simply download the `easyscript.py` file and import it into your Python project:

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

# User object and LDAP functionality tests
python tests/test_easyscript_user.py

# Or run all tests
python -m pytest tests/
```

## Custom Variables

You can provide custom variables when evaluating expressions:

```python
evaluator = EasyScriptEvaluator()

# Add custom variables
custom_vars = {
    'name': 'Alice',
    'age': 30,
    'config': {'debug': True}
}

result = evaluator.evaluate('"User: " + name', variables=custom_vars)
# Returns: "User: Alice"
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
```javascript
if len(user.mail) > 5 and user.mail ~ ".*@.*": return true
```

**Pattern Matching**:
```javascript
if user.uid ~ "^[a-z]+$": return "Valid username"
if user.mail ~ ".*@company\.com$": return "Company email"
```

**Configuration Logic**:
```javascript
if user.title == "Manager" or user.department == "Executive": return "admin"
```