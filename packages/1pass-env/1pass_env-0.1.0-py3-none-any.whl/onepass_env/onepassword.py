"""1Password SDK integration."""

import asyncio
import os
from typing import Any, Dict, List, Optional

from onepassword.client import Client

from onepass_env.exceptions import OnePassEnvError, AuthenticationError, VaultError


class OnePasswordClient:
    """Client for interacting with 1Password using the official SDK."""
    
    def __init__(self, vault: Optional[str] = None, verbose: bool = False):
        """Initialize the 1Password client.
        
        Args:
            vault: 1Password vault name or ID
            verbose: Enable verbose logging
        """
        self.vault = vault
        self.verbose = verbose
        self._client: Optional[Client] = None
        self._vault_id: Optional[str] = None
    
    async def _get_client(self) -> Client:
        """Get or create the 1Password client."""
        if self._client is None:
            try:
                token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
                if not token:
                    raise AuthenticationError("OP_SERVICE_ACCOUNT_TOKEN environment variable is not set")
                
                # Authenticate with 1Password using the async SDK
                self._client = await Client.authenticate(
                    auth=token,
                    integration_name="1pass-env CLI",
                    integration_version="v0.1.0"
                )
            except Exception as e:
                raise AuthenticationError(
                    f"Failed to initialize 1Password client. Make sure OP_SERVICE_ACCOUNT_TOKEN "
                    f"environment variable is set: {e}"
                )
        return self._client
    
    async def _get_vault_id(self) -> str:
        """Get the vault ID from the vault name."""
        if not self.vault:
            raise VaultError("Vault name is required")
        
        if self._vault_id is None:
            try:
                client = await self._get_client()
                vaults = await client.vaults.list()
                
                # Try to find vault by name or ID
                for vault in vaults:
                    if vault.title == self.vault or vault.id == self.vault:
                        self._vault_id = vault.id
                        break
                
                if self._vault_id is None:
                    raise VaultError(f"Vault '{self.vault}' not found")
                    
            except Exception as e:
                if isinstance(e, VaultError):
                    raise
                raise VaultError(f"Failed to access vault '{self.vault}': {e}")
        
        return self._vault_id
    
    def is_available(self) -> bool:
        """Check if 1Password SDK is available and properly configured."""
        try:
            return os.getenv("OP_SERVICE_ACCOUNT_TOKEN") is not None
        except Exception:
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with 1Password."""
        try:
            # Run the async check in a sync context
            return asyncio.run(self._check_authentication())
        except Exception:
            return False
    
    async def _check_authentication(self) -> bool:
        """Async helper to check authentication."""
        try:
            client = await self._get_client()
            # Try to list vaults to test authentication
            vaults = await client.vaults.list()
            if self.verbose:
                print(f"Found {len(vaults)} vaults")
            return True
        except Exception as e:
            if self.verbose:
                print(f"Authentication failed: {e}")
            return False
    
    def get_item_by_title(self, title: str):
        """Get an item by its title."""
        try:
            return asyncio.run(self._get_item_by_title_async(title))
        except Exception as e:
            raise OnePassEnvError(f"Failed to get item '{title}': {e}")
    
    async def _get_item_by_title_async(self, title: str):
        """Async helper to get item by title."""
        if not self.vault:
            raise VaultError("Vault name is required")
        
        client = await self._get_client()
        vault_id = await self._get_vault_id()
        
        # List all items in the vault
        items = await client.items.list(vault_id=vault_id)
        
        # Find item by title
        for item_overview in items:
            if item_overview.title == title:
                # Get the full item details
                full_item = await client.items.get(vault_id=vault_id, item_id=item_overview.id)
                return full_item
        
        return None
    
    def list_items(self) -> List[Dict[str, Any]]:
        """List all items in the vault."""
        try:
            return asyncio.run(self._list_items_async())
        except Exception as e:
            raise OnePassEnvError(f"Failed to list items: {e}")
    
    async def _list_items_async(self) -> List[Dict[str, Any]]:
        """Async helper to list items."""
        client = await self._get_client()
        vault_id = await self._get_vault_id()
        
        items = await client.items.list(vault_id=vault_id)
        
        return [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "created_at": getattr(item, 'created_at', None),
                "updated_at": getattr(item, 'updated_at', None),
            }
            for item in items
        ]


# Sync wrapper functions to make the async API easier to use
def run_async(coro):
    """Helper to run async functions in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def get_client() -> Client:
    """Initialize and authenticate 1Password client with proper error handling.
    
    This function provides compatibility with the main.py style client initialization.
    
    Returns:
        Authenticated 1Password client
        
    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Get the service account token from environment
        token = os.getenv('OP_SERVICE_ACCOUNT_TOKEN')
        if not token:
            raise AuthenticationError("OP_SERVICE_ACCOUNT_TOKEN environment variable is required")
        
        # Initialize 1Password client with SDK
        client = await Client.authenticate(
            auth=token,
            integration_name="1pass-env CLI",
            integration_version="v1.0.0"
        )
        
        return client
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Failed to connect to 1Password - {str(e)}")
