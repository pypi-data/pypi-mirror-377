"""Storage Module for API Keys"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from .crypto import KeyEncryption
from .auth import PasswordManager
import platform
from pathlib import Path

def restrict_file_to_user(filepath):
    if os.name == 'nt':  # Windows
        try:
            import win32security
            import ntsecuritycon as con
            user, domain, type = win32security.LookupAccountName("", os.getlogin())
            sd = win32security.GetFileSecurity(str(filepath), win32security.DACL_SECURITY_INFORMATION)
            dacl = win32security.ACL()
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, user)
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(str(filepath), win32security.DACL_SECURITY_INFORMATION, sd)
        except ImportError:
            print("[WARNING] pywin32 is not installed. File permissions may not be secure on Windows.")
        except Exception as e:
            print(f"[WARNING] Could not set secure permissions on {filepath}: {e}")
    else:
        try:
            os.chmod(filepath, 0o600)
        except Exception as e:
            print(f"[WARNING] Could not set secure permissions on {filepath}: {e}")

class KeyStorage:
    """Handle storage and retrieval of encrypted API keys."""
    
    def __init__(self, password: str = None):
        """Initialize storage with default location.
        
        Args:
            password (str, optional): User password for encryption. If None, uses system-based encryption.
        """
        self.storage_dir = Path.home() / '.apilib'
        self.storage_file = self.storage_dir / 'keys.json'
        self.password_manager = PasswordManager()
        
        # Use provided password or fallback to system-based encryption
        self.encryption = KeyEncryption(password)
        
        # Ensure storage directory exists with proper permissions
        try:
            self.storage_dir.mkdir(exist_ok=True)
            # Ensure directory is writable
            import stat
            if self.storage_dir.exists():
                current_mode = self.storage_dir.stat().st_mode
                self.storage_dir.chmod(current_mode | stat.S_IWRITE | stat.S_IREAD)
        except PermissionError:
            raise PermissionError(f"Cannot create or access directory {self.storage_dir}. Please check permissions or run as administrator.")
        except Exception as e:
            raise Exception(f"Error setting up storage directory: {e}")
    
    def _load_data(self) -> Dict:
        """Load data from storage file.
        
        Returns:
            Dict: The stored data or empty dict if file doesn't exist
        """
        if not self.storage_file.exists():
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: Dict) -> None:
        """Save data to storage file.
        
        Args:
            data (Dict): The data to save
        """
        import tempfile
        import shutil
        
        try:
            # Create a temporary file first
            temp_file = self.storage_file.with_suffix('.tmp')
            
            # Write to temporary file
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # If file exists and is read-only, try to make it writable
            if self.storage_file.exists():
                try:
                    import stat
                    # Remove read-only attribute if present
                    current_mode = self.storage_file.stat().st_mode
                    self.storage_file.chmod(current_mode | stat.S_IWRITE)
                except (OSError, PermissionError):
                    pass  # Continue anyway
            
            # Atomic move from temp to actual file
            shutil.move(str(temp_file), str(self.storage_file))
            
            # Set secure permissions
            restrict_file_to_user(self.storage_file)
            
        except PermissionError as e:
            # Clean up temp file if it exists
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            raise PermissionError(f"Cannot write to {self.storage_file}. Please check file permissions or run as administrator.") from e
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            raise e
    
    def store_key(self, provider, api_key, password=None, expiration_days=7):
        data = self._load_data()
        normalized_provider = provider.lower()
        actual_provider = normalized_provider
        if actual_provider not in data:
            data[actual_provider] = []
        
        # Encrypt the API key
        encrypted_key = self.encryption.encrypt(api_key)
        
        # Check if key already exists (compare decrypted values)
        for existing_encrypted_key in data[actual_provider]:
            try:
                # Try current encryption first
                existing_result = self.encryption.decrypt(existing_encrypted_key)
                existing_key = existing_result[0] if isinstance(existing_result, tuple) else existing_result
                if existing_key == api_key:
                    return False  # Key already exists
            except:
                # If current encryption fails, try system-based encryption for backward compatibility
                try:
                    system_encryption = KeyEncryption(None)  # This will use system-based key
                    existing_result = system_encryption.decrypt(existing_encrypted_key)
                    existing_key = existing_result[0] if isinstance(existing_result, tuple) else existing_result
                    if existing_key == api_key:
                        return False  # Key already exists
                except:
                    continue  # Skip corrupted entries
        
        # Add the new encrypted key
        data[actual_provider].append(encrypted_key)
        
        # Save the updated data
        self._save_data(data)
        return True

    def get_keys(self, provider, password=None):
        data = self._load_data()
        normalized_provider = provider.lower()
        actual_provider = normalized_provider
        if actual_provider not in data:
            print(f"No keys found for '{provider}'. Did you mean: {', '.join(data.keys())}?")
            return []
        decrypted_keys = []
        for encrypted_key in data[actual_provider]:
            try:
                # Try current encryption first
                decrypted_result = self.encryption.decrypt(encrypted_key)
                decrypted_key = decrypted_result[0] if isinstance(decrypted_result, tuple) else decrypted_result
                decrypted_keys.append(decrypted_key)
            except:
                # If current encryption fails, try system-based encryption for backward compatibility
                try:
                    system_encryption = KeyEncryption(None)  # This will use system-based key
                    decrypted_result = system_encryption.decrypt(encrypted_key)
                    decrypted_key = decrypted_result[0] if isinstance(decrypted_result, tuple) else decrypted_result
                    decrypted_keys.append(decrypted_key)
                except:
                    continue  # Skip corrupted entries
        return decrypted_keys
    
    def list_providers(self):
        data = self._load_data()
        return list(data.keys())
    
    def delete_key(self, provider, index):
        """Delete a specific key by 1-based index for a provider."""
        data = self._load_data()
        normalized_provider = provider.lower()
        actual_provider = normalized_provider
        if actual_provider in data:
            try:
                # index is 1-based from CLI
                idx = int(index)
                if idx < 1 or idx > len(data[actual_provider]):
                    return False
                data[actual_provider].pop(idx - 1)
            except (ValueError, IndexError):
                return False

            # Remove provider if no keys left
            if not data.get(actual_provider):
                try:
                    del data[actual_provider]
                except KeyError:
                    pass

            self._save_data(data)
            # Audit log: record deletion event (no secrets)
            try:
                pm = PasswordManager()
                pm._log_event("DELETE_KEY", f"Deleted key #{idx} for provider '{actual_provider}'")
            except Exception:
                pass
            return True
        return False
        
    def get_all_keys(self) -> Dict[str, List[str]]:
        """Retrieve all API keys for all providers.
        
        Returns:
            Dict[str, List[str]]: Dictionary with provider names as keys and lists of decrypted API keys as values
        """
        try:
            data = self._load_data()
            all_keys = {}
            
            for provider, encrypted_keys in data.items():
                decrypted_keys = []
                for encrypted_key in encrypted_keys:
                    try:
                        # Try current encryption first
                        decrypted_result = self.encryption.decrypt(encrypted_key)
                        # decrypt returns (decrypted_string, needs_rotation)
                        decrypted_key = decrypted_result[0] if isinstance(decrypted_result, tuple) else decrypted_result
                        decrypted_keys.append(decrypted_key)
                    except:
                        # If current encryption fails, try system-based encryption for backward compatibility
                        try:
                            system_encryption = KeyEncryption(None)  # This will use system-based key
                            decrypted_result = system_encryption.decrypt(encrypted_key)
                            # decrypt returns (decrypted_string, needs_rotation)
                            decrypted_key = decrypted_result[0] if isinstance(decrypted_result, tuple) else decrypted_result
                            decrypted_keys.append(decrypted_key)
                        except:
                            continue  # Skip corrupted entries
                
                if decrypted_keys:  # Only include providers with valid keys
                    all_keys[provider] = decrypted_keys
            
            return all_keys
            
        except Exception as e:
            print(f"Error retrieving all keys: {e}")
            return {}
    
    def delete_provider_keys(self, provider):
        data = self._load_data()
        normalized_provider = provider.lower()
        actual_provider = normalized_provider
        if actual_provider in data:
            del data[actual_provider]
            self._save_data(data)
            # Audit log: deleted all keys for provider
            try:
                pm = PasswordManager()
                pm._log_event("DELETE_ALL_PROVIDER", f"Deleted all keys for provider '{actual_provider}'")
            except Exception:
                pass
            return True
        return False

    def delete_all_for_provider(self, provider) -> bool:
        """Delete all keys for a specific provider (alias for delete_provider_keys)."""
        return self.delete_provider_keys(provider)
        
    def delete_all_keys(self) -> bool:
        """Delete all stored API keys for all providers.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clear all data by saving an empty dictionary
            self._save_data({})
            # Audit log: deleted all keys
            try:
                pm = PasswordManager()
                pm._log_event("DELETE_ALL_KEYS", "Deleted ALL stored API keys")
            except Exception:
                pass
            return True
            
        except Exception as e:
            print(f"Error deleting all keys: {e}")
            return False