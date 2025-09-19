"""Tests for the 1Password client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from onepass_env.onepassword import OnePasswordClient
from onepass_env.exceptions import OnePassEnvError, AuthenticationError, VaultError


class TestOnePasswordClient:
    """Test cases for OnePasswordClient."""
    
    @patch('onepass_env.onepassword.new_client')
    def test_client_initialization(self, mock_new_client):
        """Test client initialization."""
        mock_client = Mock()
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="test-vault")
        client = op_client._get_client()
        
        assert client == mock_client
        mock_new_client.assert_called_once()
    
    @patch('onepass_env.onepassword.new_client')
    def test_client_initialization_failure(self, mock_new_client):
        """Test client initialization failure."""
        mock_new_client.side_effect = Exception("SDK initialization failed")
        
        op_client = OnePasswordClient(vault="test-vault")
        
        with pytest.raises(AuthenticationError, match="OP_SERVICE_ACCOUNT_TOKEN"):
            op_client._get_client()
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    def test_is_available_with_token(self):
        """Test is_available returns True when token is set."""
        op_client = OnePasswordClient()
        assert op_client.is_available() is True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_is_available_without_token(self):
        """Test is_available returns False when token is not set."""
        op_client = OnePasswordClient()
        assert op_client.is_available() is False
    
    @patch('onepass_env.onepassword.new_client')
    def test_is_authenticated_success(self, mock_new_client):
        """Test is_authenticated returns True when authenticated."""
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = []
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient()
        assert op_client.is_authenticated() is True
    
    @patch('onepass_env.onepassword.new_client')
    def test_is_authenticated_failure(self, mock_new_client):
        """Test is_authenticated returns False when not authenticated."""
        mock_client = Mock()
        mock_client.vaults.list_all.side_effect = Exception("Authentication failed")
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient()
        assert op_client.is_authenticated() is False
    
    @patch('onepass_env.onepassword.new_client')
    def test_get_vault_id_by_name(self, mock_new_client):
        """Test getting vault ID by name."""
        mock_vault = Mock()
        mock_vault.id = "vault-123"
        mock_vault.title = "Test Vault"
        
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = [mock_vault]
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="Test Vault")
        vault_id = op_client._get_vault_id()
        
        assert vault_id == "vault-123"
    
    @patch('onepass_env.onepassword.new_client')
    def test_get_vault_id_not_found(self, mock_new_client):
        """Test getting vault ID when vault not found."""
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = []
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="Nonexistent Vault")
        
        with pytest.raises(VaultError, match="not found"):
            op_client._get_vault_id()
    
    @patch('onepass_env.onepassword.new_client')
    def test_store_secret(self, mock_new_client):
        """Test storing a secret."""
        mock_item = Mock()
        mock_item.id = "item-123"
        
        mock_vault = Mock()
        mock_vault.id = "vault-123"
        mock_vault.title = "Test Vault"
        
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = [mock_vault]
        mock_client.items.create.return_value = mock_item
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="Test Vault")
        item_id = op_client.store_secret("API_KEY", "secret-value")
        
        assert item_id == "item-123"
        mock_client.items.create.assert_called_once()
    
    @patch('onepass_env.onepassword.new_client')
    def test_get_secret(self, mock_new_client):
        """Test getting a secret."""
        mock_field = Mock()
        mock_field.label = "API_KEY"
        mock_field.value = "secret-value"
        
        mock_item = Mock()
        mock_item.fields = [mock_field]
        
        mock_vault = Mock()
        mock_vault.id = "vault-123"
        mock_vault.title = "Test Vault"
        
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = [mock_vault]
        mock_client.items.get.return_value = mock_item
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="Test Vault")
        value = op_client.get_secret("op://Test Vault/item-123/API_KEY")
        
        assert value == "secret-value"
    
    @patch('onepass_env.onepassword.new_client')
    def test_get_secret_field_not_found(self, mock_new_client):
        """Test getting a secret when field is not found."""
        mock_field = Mock()
        mock_field.label = "OTHER_KEY"
        mock_field.value = "other-value"
        
        mock_item = Mock()
        mock_item.fields = [mock_field]
        
        mock_vault = Mock()
        mock_vault.id = "vault-123"
        mock_vault.title = "Test Vault"
        
        mock_client = Mock()
        mock_client.vaults.list_all.return_value = [mock_vault]
        mock_client.items.get.return_value = mock_item
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="Test Vault")
        
        with pytest.raises(OnePassEnvError, match="Field 'API_KEY' not found"):
            op_client.get_secret("op://Test Vault/item-123/API_KEY")
    
    def test_get_secret_invalid_reference(self):
        """Test getting a secret with invalid reference."""
        op_client = OnePasswordClient(vault="Test Vault")
        
        with pytest.raises(OnePassEnvError, match="Invalid 1Password reference"):
            op_client.get_secret("invalid-reference")
