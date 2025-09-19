"""
Test helper classes for EasyScript tests

This module contains example classes that can be used for testing object injection.
"""


class LDAPUser:
    """LDAP-like user object with common eDirectory attributes - Example for testing"""

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