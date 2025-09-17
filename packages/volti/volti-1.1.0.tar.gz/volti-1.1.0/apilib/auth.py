"""Authentication Module for Password Management"""

import os
import json
import hashlib
import getpass
import time
import secrets
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import argon2
import argon2.exceptions as argon2_exceptions
import shutil


class PasswordManager:
    """Handle user password authentication and management."""
    
    
    def __init__(self):
        """Initialize password manager."""
        self.config_dir = Path.home() / '.apilib'
        self.config_file = self.config_dir / 'config.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    # ===========================================
    # CONFIGURATION MANAGEMENT
    # ===========================================
    
    def _load_config(self) -> dict:
        """Load configuration from file.
        
        Returns:
            dict: Configuration data
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_config(self, config: dict) -> None:
        """Save configuration to file.
        
        Args:
            config (dict): Configuration data to save
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    # ===========================================
    # SESSION MANAGEMENT
    # ===========================================
    
    def cache_password_for_session(self, password: str):
        """No-op placeholder. Session caching removed for security.

        This method remains for backward compatibility but does nothing.
        """
        return None
    
    def get_session_password(self) -> Optional[str]:
        """Session caching removed; always return None.

        Kept for API compatibility with older callers.
        """
        return None
    
    def clear_session(self):
        """Session caching removed; no session to clear.

        Kept for backwards compatibility; performs no action.
        """
        return None
    
    # ===========================================
    # LOGGING AND AUDITING
    # ===========================================
    
    def _log_event(self, event_type: str, message: str):
        """Log security events to audit file.

        Adds actor (user) and PID context, attempts simple rotation when file exceeds
        a size threshold, and enforces restrictive file permissions where possible.
        """
        log_dir = self.config_dir
        log_file = log_dir / 'audit.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # actor and process context
        try:
            actor = getpass.getuser()
        except Exception:
            try:
                actor = os.getlogin()
            except Exception:
                actor = 'unknown'
        pid = os.getpid()

        entry = f"[{timestamp}] [{event_type}] [actor={actor}] [pid={pid}] {message}\n"

        try:
            # Ensure log directory exists
            log_dir.mkdir(exist_ok=True)

            # Rotate if file is large (>5MB)
            try:
                if log_file.exists() and log_file.stat().st_size > (5 * 1024 * 1024):
                    rotated = log_dir / f"audit.log.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.move(str(log_file), str(rotated))
            except Exception:
                # Rotation is best-effort
                pass

            with open(log_file, 'a') as f:
                f.write(entry)

            # Try to set restrictive permissions on POSIX
            try:
                if os.name != 'nt':
                    os.chmod(log_file, 0o600)
            except Exception:
                pass

        except Exception:
            # Logging must never raise for the caller
            pass
    
    # ===========================================
    # RATE LIMITING
    # ===========================================
    
    def _get_rate_limit_config(self) -> dict:
        """Get rate limiting configuration."""
        config = self._load_config()
        if 'rate_limit' not in config:
            config['rate_limit'] = {'failures': 0, 'last_failure': 0}
        return config
    
    def _save_rate_limit_config(self, config: dict):
        """Save rate limiting configuration."""
        self._save_config(config)
    
    def is_locked_out(self) -> Tuple[bool, int]:
        """Check if user is locked out due to too many failed attempts.
        
        Returns:
            Tuple[bool, int]: (is_locked_out, seconds_remaining)
        """
        config = self._get_rate_limit_config()
        failures = config['rate_limit']['failures']
        last_failure = config['rate_limit']['last_failure']
        
        if failures >= 3:
            lockout_period = 15 * 60  # 15 minutes
            time_since_failure = time.time() - last_failure
            
            if time_since_failure < lockout_period:
                return True, int(lockout_period - time_since_failure)
            else:
                # Reset after lockout period
                config['rate_limit']['failures'] = 0
                self._save_rate_limit_config(config)
        
        return False, 0
    
    # ===========================================
    # PASSWORD UTILITIES
    # ===========================================
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using Argon2 with a random salt."""
        ph = argon2.PasswordHasher()
        return ph.hash(password)
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets complexity requirements."""
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return (len(password) >= 10 and 
                has_upper and has_lower and has_digit and has_special)
    
    # ===========================================
    # FIRST-TIME SETUP
    # ===========================================
    
    def is_first_time_user(self) -> bool:
        """Check if this is the first time the user is using the library.
        
        Returns:
            bool: True if first time user, False otherwise
        """
        config = self._load_config()
        return 'password_hash' not in config
    
    def setup_password(self) -> Tuple[bool, str]:
        """Setup password for first-time users.
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if not self.is_first_time_user():
            return False, "Password already exists. Use authenticate() instead."
        
        print("\n🔐 Welcome to API Library! This is your first time using the library.")
        print("For security, you need to create a master password.")
        print("This password will be required every time you fetch API keys.\n")
        
        while True:
            password = getpass.getpass("Create a master password: ")
            
            if not self._validate_password_strength(password):
                print("❌ Password must be at least 10 characters long and contain uppercase letters,")
                print("   lowercase letters, numbers, and special characters. Please try again.\n")
                continue
            
            confirm_password = getpass.getpass("Confirm your password: ")
            
            if password != confirm_password:
                print("❌ Passwords don't match. Please try again.\n")
                continue
            
            # Save hashed password
            config = self._load_config()
            config['password_hash'] = self._hash_password(password)
            config['setup_complete'] = True
            
            try:
                self._save_config(config)
                print("\n✅ Master password created successfully!")
                print("Remember this password - you'll need it to fetch your API keys.\n")
                return True, "Password setup completed successfully"
            except Exception as e:
                return False, f"Failed to save password: {e}"
    
    # ===========================================
    # AUTHENTICATION
    # ===========================================
    
    def authenticate(self, password: str = None) -> bool:
        """Authenticate the user by verifying the password with Argon2.
        
        Args:
            password: Password to authenticate. If None, prompts the user.
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if password is None:
            # Prompt for password if not provided
            try:
                password = getpass.getpass("Enter your master password: ")
            except Exception:
                return False
            
        # Check lockout status
        locked, seconds_left = self.is_locked_out()
        if locked:
            self._log_event("AUTH_LOCKOUT", f"Too many failed attempts. Locked out for {seconds_left} seconds.")
            print(f"❌ Too many failed attempts. Try again in {seconds_left // 60} min {seconds_left % 60} sec.")
            return False
        
        config = self._load_config()
        password_hash = config.get('password_hash')
        if not password_hash:
            return False
        
        ph = argon2.PasswordHasher()
        try:
            result = ph.verify(password_hash, password)
            # Reset failures on success
            config = self._get_rate_limit_config()
            config['rate_limit']['failures'] = 0
            self._save_rate_limit_config(config)
            self._log_event("AUTH_SUCCESS", "Password authentication succeeded.")
            # Do not cache password in memory; session caching removed
            return result
        except argon2_exceptions.VerifyMismatchError:
            # Increment failure count
            config = self._get_rate_limit_config()
            config['rate_limit']['failures'] += 1
            config['rate_limit']['last_failure'] = time.time()
            self._save_rate_limit_config(config)
            self._log_event("AUTH_FAIL", "Incorrect password entered.")
            print("❌ Incorrect password.")
            return False
        except Exception:
            self._log_event("AUTH_ERROR", "Authentication error occurred.")
            print("❌ Authentication error.")
            return False
    
    # ===========================================
    # RECOVERY METHODS
    # ===========================================
    
    def setup_security_question(self):
        """Setup a security question for password reset."""
        print("\n🔒 Set up a security question for password recovery.")
        question = input("Enter your security question (e.g., Your first pet's name?): ")
        answer = getpass.getpass("Enter the answer (hidden): ")
        
        config = self._load_config()
        config['security_question'] = question
        config['security_answer_hash'] = self._hash_password(answer)
        self._save_config(config)
        print("✅ Security question set up successfully.")
    
    def setup_backup_code(self):
        """Generate and store a backup code for password reset."""
        backup_code = secrets.token_urlsafe(12)
        config = self._load_config()
        config['backup_code_hash'] = self._hash_password(backup_code)
        self._save_config(config)
        print(f"🔑 Your backup code (save this securely!): {backup_code}")
    
    def reset_password(self) -> Tuple[bool, str]:
        """Reset password using security question or backup code.
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        config = self._load_config()
        ph = argon2.PasswordHasher()
        
        # Try security question first
        if 'security_question' in config:
            print(f"\nSecurity Question: {config['security_question']}")
            answer = getpass.getpass("Enter your answer: ")
            try:
                if ph.verify(config['security_answer_hash'], answer):
                    print("✅ Security answer verified.")
                else:
                    print("❌ Incorrect answer.")
                    return False, "Security answer incorrect."
            except Exception:
                print("❌ Verification failed.")
                return False, "Verification failed."
                
        # Try backup code if security question not available
        elif 'backup_code_hash' in config:
            backup_code = getpass.getpass("Enter your backup code: ")
            try:
                if ph.verify(config['backup_code_hash'], backup_code):
                    print("✅ Backup code verified.")
                else:
                    print("❌ Incorrect backup code.")
                    return False, "Backup code incorrect."
            except Exception:
                print("❌ Verification failed.")
                return False, "Verification failed."
        else:
            print("❌ No recovery method set up. Cannot reset password.")
            return False, "No recovery method set up."
        
        # Allow user to set new password
        while True:
            new_password = getpass.getpass("Enter new master password: ")
            
            if not self._validate_password_strength(new_password):
                print("❌ Password must be at least 10 characters long and contain uppercase, lowercase, numbers, and special characters. Please try again.\n")
                continue
            
            confirm_password = getpass.getpass("Confirm new password: ")
            if new_password != confirm_password:
                print("❌ Passwords don't match. Please try again.\n")
                continue
            
            config['password_hash'] = self._hash_password(new_password)
            self._save_config(config)
            print("✅ Password reset successfully!")
            return True, "Password reset successfully."
    
    # ===========================================
    # MAIN ENTRY POINTS
    # ===========================================
    
    def get_password_for_encryption(self) -> Optional[str]:
        """Get the user's password for encryption purposes.
        
        Returns:
            Optional[str]: The password if authenticated, None otherwise
        """
        if self.is_first_time_user():
            success, _ = self.setup_password()
            if not success:
                return None
        
        # Prompt for password
        password = getpass.getpass("Enter your master password: ")
        success = self.authenticate(password)
        
        if success:
            return password
        else:
            print("❌ Authentication failed.")
            return None