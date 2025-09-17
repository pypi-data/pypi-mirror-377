"""
Volti - Minimal CLI & Library for Secure API Key Storage and Retrieval

Features:
- Add, get, remove, list, clear API keys
- Secure password-based encryption
- .env file import/export support
- Minimalistic CLI commands
- Onboarding and help included

Author: Lokesh & Aditya
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Lokesh & Aditya"
__email__ = "lokeshpantangi@gmail.com, aditya268244@gmail.com"

from .core import APIKeyManager

__all__ = ['APIKeyManager']