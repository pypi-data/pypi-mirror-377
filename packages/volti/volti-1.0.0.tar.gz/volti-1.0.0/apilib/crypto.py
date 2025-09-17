"""Encryption Module for API Keys"""

import os
import time
import base64
import ctypes
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from struct import pack, unpack

def secure_wipe(data: bytes) -> None:
    """Securely wipe sensitive data from memory.
    
    Args:
        data (bytes): Data to wipe
    """
    # Get the memory address and size
    data_size = len(data)
    # Create a ctypes array from the buffer
    buf = (ctypes.c_char * data_size).from_buffer(data)
    # Overwrite with random data multiple times
    for _ in range(3):
        ctypes.memset(buf, secrets.randbelow(256), data_size)

class KeyEncryption:
    """Handle encryption and decryption of API keys."""
    
    def __init__(self, password: str = None, min_length: int = 10):
        """Initialize encryption with a password.
        
        Args:
            password (str, optional): User password for encryption. If None, uses system-based key for backward compatibility.
        """
        if password is None:
            # Generate a secure default password using system entropy
            import uuid
            import hashlib
            
            # Combine multiple sources of entropy
            entropy_sources = [
                os.urandom(32),                    # System entropy
                str(uuid.uuid4()).encode(),        # Random UUID
                str(time.time_ns()).encode(),      # High-precision timestamp
                str(os.getpid()).encode()          # Process ID
            ]
            
            # Create a unique hash from all entropy sources
            hasher = hashlib.sha256()
            for source in entropy_sources:
                hasher.update(source)
            
            # Convert hash to a password-like string with required complexity
            hash_bytes = hasher.digest()
            password = base64.urlsafe_b64encode(hash_bytes).decode()[:24]
            # Ensure complexity requirements are met
            password = f"Ap{password}#1"  # Guarantees upper, lower, special, and number
        
        # Validate password strength
        if not self._is_password_strong(password, min_length):
            raise ValueError(
                f"Password must be at least {min_length} characters long and contain "
                "uppercase, lowercase, numbers, and special characters"
            )
        
        self.password = bytearray(password.encode())
        self._fernet = None
        
    def __del__(self):
        """Securely wipe sensitive data when object is destroyed."""
        if hasattr(self, 'password'):
            secure_wipe(self.password)
    
    def _is_password_strong(self, password: str, min_length: int) -> bool:
        """Check if password meets minimum security requirements.
        
        Args:
            password (str): Password to check
            min_length (int): Minimum required length
            
        Returns:
            bool: True if password meets requirements
        """
        if len(password) < min_length:
            return False
            
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return has_upper and has_lower and has_digit and has_special
        self._fernet = None
    
    def _derive_key(self, salt: bytes = None) -> tuple[bytes, bytes]:
        """Derive encryption key using Argon2id.
        
        Args:
            salt (bytes, optional): Salt for key derivation. If None, generates random salt.
            
        Returns:
            tuple[bytes, bytes]: Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = Argon2id(
            length=32,
            salt=salt,
            iterations=3,
            memory_cost=65536,
            lanes=4
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key, salt

    def _get_fernet(self, salt: bytes = None) -> tuple[Fernet, bytes]:
        """Get Fernet instance with optional salt.
        
        Args:
            salt (bytes, optional): Salt for key derivation. If None, generates random salt.
            
        Returns:
            tuple[Fernet, bytes]: Tuple of (Fernet instance, salt used)
        """
        key, salt = self._derive_key(salt)
        return Fernet(key), salt
    
    def encrypt(self, data: str, rotation_seconds: int = 7 * 24 * 3600) -> str:
        """Encrypt a string.
        
        Args:
            data (str): The string to encrypt
            rotation_seconds (int, optional): Number of seconds until key rotation is needed.
                Defaults to 7 days.
            
        Returns:
            str: Base64 encoded encrypted data with salt and expiration
        """
        fernet, salt = self._get_fernet()
        expiration = int(time.time()) + rotation_seconds
        expiration_bytes = pack('<Q', expiration)
        
        encrypted_data = fernet.encrypt(data.encode())
        # Combine salt, expiration and encrypted data
        combined = salt + expiration_bytes + encrypted_data
        return base64.urlsafe_b64encode(combined).decode()
    
    def decrypt(self, encrypted_data: str) -> tuple[str, bool]:
        """Decrypt a string.
        
        Args:
            encrypted_data (str): Base64 encoded encrypted data with salt and expiration
            
        Returns:
            tuple[str, bool]: Tuple of (decrypted string, needs_rotation)
        """
        combined = base64.urlsafe_b64decode(encrypted_data.encode())
        # Extract salt, expiration and encrypted data
        salt = combined[:16]
        expiration_bytes = combined[16:24]
        encrypted_bytes = combined[24:]
        
        expiration = unpack('<Q', expiration_bytes)[0]
        needs_rotation = time.time() > expiration
        
        fernet, _ = self._get_fernet(salt)
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode(), needs_rotation