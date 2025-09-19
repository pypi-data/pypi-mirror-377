# 🔐 Secure Token

[![PyPI version](https://badge.fury.io/py/secure-token.svg)](https://badge.fury.io/py/secure-token)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/secure-token)](https://pepy.tech/project/secure-token)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/amirhosein2004/secure-token)

A simple and secure token management library for Python applications. Generate, validate, and manage encrypted tokens with ease.

Perfect for **authentication**, **API security**, **session management**, and **microservices**.

## ✨ Key Features

- **🛡️ Secure**: Fernet encryption with PBKDF2 key derivation
- **⚡ Fast**: Stateless design, no database required
- **🎯 Simple**: Easy-to-use API
- **🔧 Flexible**: Custom permissions and expiration times
- **📦 Lightweight**: Minimal dependencies

## 📋 Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Features](#-core-features)
- [Configuration](#-configuration)
- [Error Handling](#-error-handling)
- [Documentation](#-documentation)

## 🚀 Installation

```bash
pip install secure-token
```

## 💡 Quick Start

Get up and running in seconds:

```python
from secure_token import SecureTokenManager

# Initialize the token manager
manager = SecureTokenManager()

# Generate a secure token
token = manager.generate_token(
    user_id="john_doe",
    permissions=["read", "write"],
    expires_in_hours=24
)

# Validate the token
result = manager.validate_token(token)
if result['valid']:
    user_id = result['user_id']
    permissions = result['permissions']
    expires_at = result['expires_at']

# Check specific permission
try:
    manager.check_permission(token, "write")
except PermissionDeniedError:
    pass
```

**Result:**
```
Token generated successfully
User authenticated: john_doe
Permissions: ['read', 'write']
Expires: 2025-01-08 10:30:00
Write access: granted
```

## 🎯 Core Features

### 🔑 **Token Generation**
Create secure, encrypted tokens with custom data and permissions:

```python
# Basic token (expires in 24 hours by default)
basic_token = manager.generate_token("user123")

# Token with permissions
user_token = manager.generate_token(
    user_id="regular_user",
    permissions=["read", "write"]
)

# Advanced token with custom data
admin_token = manager.generate_token(
    user_id="admin_user",
    permissions=["admin", "read", "write", "delete"],
    expires_in_hours=48,
    additional_data={
        "role": "administrator",
        "department": "IT",
        "login_ip": "192.168.1.100",
        "session_id": "sess_abc123"
    }
)

# Short-lived token for sensitive operations
sensitive_token = manager.generate_token(
    user_id="user123",
    permissions=["delete", "admin"],
    expires_in_hours=1  # Expires in 1 hour
)
```

### ✅ **Token Validation**
Validate tokens and extract user information:

```python
from secure_token import TokenExpiredError, InvalidTokenError

try:
    result = manager.validate_token(token)

    # Extract token information
    user_id = result['user_id']
    permissions = result['permissions']
    expires_at = result['expires_at']
    issued_at = result['issued_at']
    additional_data = result['additional_data']
    time_remaining = result['time_remaining']

except TokenExpiredError:
    # Handle expired token - redirect to login
    pass
except InvalidTokenError:
    # Handle invalid token - authentication failed
    pass
except Exception as e:
    # Handle other token errors
    pass
```

### 🔄 **Token Refresh**
Extend token lifetime without losing data:

```python
# Refresh with default expiration (24 hours)
new_token = manager.refresh_token(old_token)

# Refresh with custom expiration
extended_token = manager.refresh_token(old_token, new_expires_in_hours=72)

# Example: Automatic token refresh in middleware
def refresh_if_needed(token):
    try:
        info = manager.get_token_info(token)
        # Refresh if less than 2 hours remaining
        remaining = info['time_remaining']
        if "1:" in remaining or "0:" in remaining:  # Less than 2 hours
            return manager.refresh_token(token, new_expires_in_hours=24)
        return token
    except TokenExpiredError:
        return None  # Token expired, need new login
```

### 🛡️ **Permission Checking**
Verify user permissions easily:

```python
from secure_token import PermissionDeniedError

# Check single permission
try:
    manager.check_permission(token, "admin")
    # Grant admin access
except PermissionDeniedError:
    # Handle access denied
    pass

# Check multiple permissions
def check_multiple_permissions(token, required_permissions):
    granted = []
    denied = []

    for permission in required_permissions:
        try:
            manager.check_permission(token, permission)
            granted.append(permission)
        except PermissionDeniedError:
            denied.append(permission)

    return {"granted": granted, "denied": denied}

# Usage
result = check_multiple_permissions(token, ["read", "write", "admin"])
granted_permissions = result['granted']
denied_permissions = result['denied']
# Process permission results
```

### 📊 **Token Information**
Get comprehensive token details:

```python
info = manager.get_token_info(token)

# Access token information
token_id = info['token_id']
user_id = info['user_id']
time_remaining = info['time_remaining']
permissions = info['permissions']
issued_at = info['issued_at']
expires_at = info['expires_at']
additional_data = info['additional_data']
is_revoked = info['is_revoked']

# Example: Token dashboard
def get_token_dashboard(token):
    """Get token information for dashboard display"""
    info = manager.get_token_info(token)
    return {
        'user_id': info['user_id'],
        'status': 'active' if info['valid'] else 'invalid',
        'permissions': info['permissions'],
        'time_remaining': info['time_remaining']
    }
```

## 🔧 Configuration

Customize settings for your application:

```python
from secure_token import SecureTokenManager, Settings
import os

# Method 1: Environment variables (Recommended for production)
os.environ['SECRET_KEY'] = 'your-super-secret-key-here'
os.environ['DEFAULT_EXPIRATION_HOURS'] = '12'

# Method 2: Custom settings instance
settings = Settings(
    SECRET_KEY="your-super-secret-key-here",
    DEFAULT_EXPIRATION_HOURS=12,
    SALT=b"your-custom-salt-32-bytes-long!!"
)

manager = SecureTokenManager(settings_instance=settings)

# Method 3: Using .env file (create .env file in your project)
# SECRET_KEY=your-super-secret-key-here
# DEFAULT_EXPIRATION_HOURS=12
# Then load with python-dotenv:
from dotenv import load_dotenv
load_dotenv()
manager = SecureTokenManager()  # Will use environment variables

# Example: Different configurations for different environments
def create_manager_for_environment(env="development"):
    if env == "production":
        settings = Settings(
            SECRET_KEY=os.getenv("PROD_SECRET_KEY"),
            DEFAULT_EXPIRATION_HOURS=8,  # Shorter expiration for production
            SALT=os.getenv("PROD_SALT").encode()
        )
    elif env == "testing":
        settings = Settings(
            SECRET_KEY="test-key-not-for-production",
            DEFAULT_EXPIRATION_HOURS=1,  # Very short for tests
            SALT=b"test-salt-32-bytes-long-test!!"
        )
    else:  # development
        settings = Settings(
            SECRET_KEY="dev-key-change-in-production",
            DEFAULT_EXPIRATION_HOURS=24,  # Longer for development
            SALT=b"dev-salt-32-bytes-long-develop"
        )

    return SecureTokenManager(settings_instance=settings)
```


## 📋 Error Handling

Secure Token provides specific exceptions for different scenarios:

```python
from secure_token import (
    TokenError,           # Base exception
    TokenExpiredError,    # Token has expired
    InvalidTokenError,    # Invalid token format
    PermissionDeniedError # Insufficient permissions
)

try:
    result = manager.validate_token(token)
except TokenExpiredError:
    # Handle expired token
    pass
except InvalidTokenError:
    # Handle invalid token
    pass
except PermissionDeniedError:
    # Handle permission issues
    pass
```

## 🎨 Complete Example

```python
from secure_token import SecureTokenManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

class AuthService:
    def __init__(self):
        self.token_manager = SecureTokenManager()

    def login(self, username: str, user_permissions: list) -> str:
        """Generate token after successful login"""
        return self.token_manager.generate_token(
            user_id=username,
            permissions=user_permissions,
            expires_in_hours=24,
            additional_data={"login_time": "2025-01-07T10:30:00"}
        )

    def verify_access(self, token: str, required_permission: str) -> bool:
        """Verify user has required permission"""
        try:
            return self.token_manager.check_permission(token, required_permission)
        except Exception:
            return False

    def get_user_info(self, token: str) -> dict:
        """Get user information from token"""
        try:
            return self.token_manager.validate_token(token)
        except Exception:
            return {"valid": False}

# Usage
auth = AuthService()
token = auth.login("john_doe", ["read", "write"])
if auth.verify_access(token, "write"):
    print("User can write!")
```

## 📚 Documentation

### 📖 **Complete Documentation**

> **📋 [API Reference](docs/api-reference.md)** - Complete API documentation with all methods and parameters

> **🎓 [Tutorial Guide](docs/tutorial-guide.md)** - Step-by-step beginner's guide with examples

> **🔧 [Advanced Examples](docs/advanced-examples.md)** - Real-world examples with Flask, Django, and Python apps

> **⚙️ [Development Setup](docs/development-setup.md)** - Set up development environment

> **🧪 [Testing Guide](docs/testing-guide.md)** - Run tests and benchmarks

### 🌐 **Online Documentation**
> **[📖 Full Documentation Site](https://secure-token.readthedocs.io/en/)**

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/secure-token/](https://pypi.org/project/secure-token/)
- **Source Code**: [https://github.com/amirhosein2004/secure-token](https://github.com/amirhosein2004/secure-token)
- **Documentation**: [https://secure-token.readthedocs.io/en](https://secure-token.readthedocs.io/en/)
- **Bug Reports**: [https://github.com/amirhosein2004/secure-token/issues](https://github.com/amirhosein2004/secure-token/issues)

---

**Made with ❤️ by [AmirHossein Babaee](https://github.com/amirhosein2004)**

*Secure Token - Because your application's security matters.*
