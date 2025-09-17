# 🔐 Volti - Secure API Key Manager

[![PyPI version](https://badge.fury.io/py/volti.svg)](https://badge.fury.io/py/volti)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Volti** is a minimal, secure, and user-friendly CLI tool and Python library for managing API keys. Store, retrieve, and organize your API keys with military-grade encryption and intuitive commands.

## ✨ Features

### 🔒 **Security First**
- **AES-256 encryption** with Argon2 password hashing
- **Password-based authentication** for all sensitive operations
- **Secure memory handling** with automatic key wiping
- **Cross-platform secure storage** (Windows Credential Manager, macOS Keychain, Linux Secret Service)

### 🚀 **Developer Friendly**
- **Minimal CLI commands** - just `add`, `get`, `remove`, `list`, `clear`
- **Bulk import from .env files** - migrate existing projects instantly
- **Smart key masking** - preview keys safely without full exposure
- **Auto-completion ready** - works seamlessly with shell completion
- **Zero configuration** - works out of the box

### 🛠 **Versatile Usage**
- **CLI tool** for terminal workflows
- **Python library** for programmatic access
- **Cross-platform** support (Windows, macOS, Linux)
- **Multiple keys per provider** - store backup keys, different environments
- **.gitignore integration** - automatically exclude sensitive files

## 📦 Installation

```bash
pip install volti
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Set up your master password (one-time setup)
volti setup
```

### 2. Add API Keys
```bash
# Add a single API key
volti add openai sk-1234567890abcdef

# Bulk import from .env file
volti add --env
```

### 3. Retrieve API Keys
```bash
# Get API keys for a provider
volti get openai

# Copy to clipboard automatically
volti get openai --copy
```

### 4. Manage Your Keys
```bash
# List all providers
volti list

# Remove specific key
volti remove openai 1

# Clear all keys (with confirmation)
volti clear
```

## 📖 Detailed Usage

### Adding API Keys

**Single Key:**
```bash
volti add github ghp_xxxxxxxxxxxxxxxxxxxx
volti add stripe sk_test_xxxxxxxxxxxxxxxxxxxx
volti add aws AKIAIOSFODNN7EXAMPLE
```

**Bulk Import from .env:**
```bash
# Create a .env file
echo "OPENAI_API_KEY=sk-1234567890abcdef" >> .env
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx" >> .env

# Import all keys
volti add --env
```

### Retrieving Keys

```bash
# Basic retrieval
volti get openai
# Output: 
# 🔑 API Keys for openai:
# 1. sk-1234****cdef (Primary)

# Get specific key by index
volti get openai 1

# Copy to clipboard (if pyperclip available)
volti get openai --copy
```

### Managing Keys

```bash
# List all stored providers
volti list
# Output:
# 📋 Stored API Key Providers:
# • openai (2 keys)
# • github (1 key)
# • stripe (1 key)

# Remove specific key
volti remove openai 1

# Clear all keys (with confirmation)
volti clear
```

### Utility Commands

```bash
# Check authentication status
volti auth

# Add .env to .gitignore
volti gitignore

# Show help
volti help
```

## 🐍 Python Library Usage

```python
from apilib import APIKeyManager

# Initialize with password
manager = APIKeyManager(password="your_secure_password")

# Store a key
success, message = manager.store_key("sk-1234567890abcdef", "openai")
print(f"✅ {message}" if success else f"❌ {message}")

# Retrieve keys
success, keys, message = manager.fetch_keys("openai")
if success:
    for i, key in enumerate(keys, 1):
        print(f"{i}. {key}")

# Delete a key
success, message = manager.delete_key("openai", 1)
print(f"✅ {message}" if success else f"❌ {message}")
```

## 🔧 Advanced Features

### Environment File Format
```env
# .env file format
OPENAI_API_KEY=sk-1234567890abcdef
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxx
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Comments are ignored
# Empty lines are ignored
```

### Security Features

- **Argon2 Password Hashing**: Industry-standard password hashing
- **AES-256 Encryption**: Military-grade encryption for stored keys
- **Secure Memory Handling**: Automatic cleanup of sensitive data
- **Platform Integration**: Uses OS-native secure storage when available

### Cross-Platform Support

| Platform | Secure Storage Backend |
|----------|----------------------|
| Windows  | Windows Credential Manager |
| macOS    | Keychain Services |
| Linux    | Secret Service API |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/lokeshpantangi/volti/blob/main/CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/lokeshpantangi/volti.git
cd volti
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by [Lokesh](https://github.com/lokeshpantangi) & [Aditya](https://github.com/aditya268244)
- Powered by [cryptography](https://cryptography.io/) for encryption
- CLI built with [Click](https://click.palletsprojects.com/)

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/volti/
- **GitHub Repository**: https://github.com/lokeshpantangi/volti
- **Issue Tracker**: https://github.com/lokeshpantangi/volti/issues
- **Documentation**: https://github.com/lokeshpantangi/volti#readme

---

**⚡ Made for developers who value security and simplicity.**