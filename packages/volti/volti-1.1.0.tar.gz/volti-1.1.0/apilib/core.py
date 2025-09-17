"""Core API Key Manager"""

from typing import Dict, List, Tuple
from .storage import KeyStorage
from .auth import PasswordManager

class APIKeyManager:
    """Main class for managing API keys."""
    
    def __init__(self, password: str = None):
        """Initialize the API Key Manager.
        
        Args:
            password (str, optional): User password for encryption. If None, uses system-based encryption.
        """
        self.password_manager = PasswordManager()
        self.storage = KeyStorage(password)
    
    def store_key(self, api_key: str, provider: str) -> Tuple[bool, str]:
        """Store an API key for a specified provider.
        
        Args:
            api_key (str): The API key to store
            provider (str): The provider name
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Store the key
        success = self.storage.store_key(provider, api_key)
        
        if success:
            return True, f"API key successfully stored for {provider}"
        else:
            return False, "API key already exists or failed to store"
    
    def fetch_keys(self, provider: str) -> Tuple[bool, List[str], str]:
        """Fetch all API keys for a provider with password authentication.
        
        Args:
            provider (str): The provider name (case-insensitive)
            
        Returns:
            Tuple[bool, List[str], str]: (Success status, Keys list, Message)
        """
        # Authenticate user first
        password = self.password_manager.get_password_for_encryption()
        if password is None:
            return False, [], "Authentication failed. Cannot fetch keys."
        
        # Create new storage instance with authenticated password
        authenticated_storage = KeyStorage(password)
        
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Get keys
        keys = authenticated_storage.get_keys(provider)
        
        if not keys:
            available_providers = authenticated_storage.list_providers()
            if available_providers:
                providers_list = ", ".join([p for p in available_providers])
                message = f"No keys found for '{provider}'. Available providers: {providers_list}"
            else:
                message = "No API keys stored yet. Use 'add' to add some keys first."
            return False, [], message
        
        return True, keys, f"Found {len(keys)} key(s) for {provider}"
    
    def delete_key(self, provider: str, key_index: int) -> Tuple[bool, str]:
        """Delete a specific API key by index with password authentication.
        
        Args:
            provider (str): The provider name
            key_index (int): The index of the key to delete (1-based)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Authenticate user first
        password = self.password_manager.get_password_for_encryption()
        if password is None:
            return False, "Authentication failed. Cannot delete keys."
        
        # Create new storage instance with authenticated password
        authenticated_storage = KeyStorage(password)
        
        # Normalize provider name
        provider = provider.lower().strip()
        
        # Validate key index
        if key_index < 1:
            return False, "Key index must be 1 or greater"
        
        # Check if provider exists and has keys
        keys = authenticated_storage.get_keys(provider)
        if not keys:
            return False, f"No keys found for '{provider}'"
        
        if key_index > len(keys):
            return False, f"Key index {key_index} not found. {provider} has only {len(keys)} key(s)"
        
        # Delete the key
        success = authenticated_storage.delete_key(provider, key_index)
        
        if success:
            return True, f"Key #{key_index} successfully deleted for {provider}"
        else:
            return False, "Failed to delete key"
    
    def fetch_all_keys(self) -> Tuple[bool, Dict[str, List[str]], str]:
        """Fetch all API keys for all providers.
        
        Returns:
            Tuple[bool, Dict[str, List[str]], str]: (Success status, All keys dict, Message)
        """
        all_keys = self.storage.get_all_keys()
        
        if not all_keys:
            return False, {}, "No API keys stored yet. Use 'add' to add some keys first."
        
        total_keys = sum(len(keys) for keys in all_keys.values())
        return True, all_keys, f"Found {total_keys} key(s) across {len(all_keys)} provider(s)"
    
    def list_all_providers(self) -> List[str]:
        """Get list of all providers with stored keys (requires authentication).
        
        Returns:
            List[str]: List of provider names
        """
        # For listing providers, we don't require authentication as it's just metadata
        # But we could add authentication here if needed for extra security
        providers = self.storage.list_providers()
        return [p for p in providers]
    
    def delete_all_keys(self) -> Tuple[bool, str]:
        """Delete all API keys for all providers with password authentication.
        
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Authenticate user first
        password = self.password_manager.get_password_for_encryption()
        if password is None:
            return False, "Authentication failed. Cannot delete keys."
        
        # Create new storage instance with authenticated password
        authenticated_storage = KeyStorage(password)
        
        # Check if there are any keys to delete
        all_keys = authenticated_storage.get_all_keys()
        if not all_keys:
            return False, "No API keys found to delete."
        
        # Count total keys before deletion
        total_keys = sum(len(keys) for keys in all_keys.values())
        total_providers = len(all_keys)
        
        # Delete all keys
        success = authenticated_storage.delete_all_keys()
        
        if success:
            return True, f"Successfully deleted {total_keys} key(s) from {total_providers} provider(s)"
        else:
            return False, "Failed to delete all keys"

    def delete_all_keys_for_provider(self, provider: str) -> Tuple[bool, str]:
        """Delete all keys for a specific provider with password authentication.

        Args:
            provider (str): Provider name

        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        # Authenticate user first
        password = self.password_manager.get_password_for_encryption()
        if password is None:
            return False, "Authentication failed. Cannot delete keys."

        authenticated_storage = KeyStorage(password)
        provider = provider.lower().strip()

        # Check if provider exists
        keys = authenticated_storage.get_keys(provider)
        if not keys:
            return False, f"No keys found for '{provider}'"

        success = authenticated_storage.delete_all_for_provider(provider)
        if success:
            return True, f"Successfully deleted all keys for {provider}"
        else:
            return False, "Failed to delete keys for provider"