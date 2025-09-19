"""Tests for the core module - import functionality only."""

import pytest
from pathlib import Path
from unittest.mock import Mock

from onepass_env.core import EnvImporter
from onepass_env.exceptions import OnePassEnvError


class TestEnvImporter:
    """Test cases for EnvImporter."""
    
    def test_import_to_file_success(self, env_importer, temp_env_file, mock_op_client):
        """Test successful import to file."""
        # Mock the 1Password item
        mock_field1 = Mock()
        mock_field1.label = "API_KEY"
        mock_field1.value = "secret-api-key"
        
        mock_field2 = Mock()
        mock_field2.label = "DB_PASSWORD"
        mock_field2.value = "secret-db-password"
        
        mock_item = Mock()
        mock_item.title = "test-item"
        mock_item.id = "item-123"
        mock_item.fields = [mock_field1, mock_field2]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        # Import to file
        imported = env_importer.import_to_file("test-item", temp_env_file)
        
        assert len(imported) == 2
        assert imported["API_KEY"] == "secret-api-key"
        assert imported["DB_PASSWORD"] == "secret-db-password"
        
        # Check file was created with correct content
        assert temp_env_file.exists()
        content = temp_env_file.read_text()
        assert 'API_KEY="secret-api-key"' in content
        assert 'DB_PASSWORD="secret-db-password"' in content
        assert '# Environment variables imported from 1Password' in content
        assert '# Vault: test-vault' in content
        assert '# Item: test-item' in content
    
    def test_import_with_field_filter(self, env_importer, temp_env_file, mock_op_client):
        """Test import with field filter."""
        # Mock the 1Password item
        mock_field1 = Mock()
        mock_field1.label = "API_KEY"
        mock_field1.value = "secret-api-key"
        
        mock_field2 = Mock()
        mock_field2.label = "DB_PASSWORD"
        mock_field2.value = "secret-db-password"
        
        mock_item = Mock()
        mock_item.fields = [mock_field1, mock_field2]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        # Import only API_KEY
        imported = env_importer.import_to_file(
            "test-item", 
            temp_env_file, 
            field_filter=["API_KEY"]
        )
        
        assert len(imported) == 1
        assert imported["API_KEY"] == "secret-api-key"
        assert "DB_PASSWORD" not in imported
        
        # Check file content
        content = temp_env_file.read_text()
        assert 'API_KEY="secret-api-key"' in content
        assert 'DB_PASSWORD' not in content
    
    def test_import_merge_with_existing(self, env_importer, temp_env_file, mock_op_client):
        """Test import merging with existing file."""
        # Create existing file
        temp_env_file.write_text('EXISTING_KEY="existing-value"\n')
        
        # Mock the 1Password item
        mock_field = Mock()
        mock_field.label = "NEW_KEY"
        mock_field.value = "new-value"
        
        mock_item = Mock()
        mock_item.fields = [mock_field]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        # Import with merge
        imported = env_importer.import_to_file("test-item", temp_env_file, merge_existing=True)
        
        assert len(imported) == 1
        assert imported["NEW_KEY"] == "new-value"
        
        # Check both existing and new variables are present
        content = temp_env_file.read_text()
        assert 'EXISTING_KEY="existing-value"' in content
        assert 'NEW_KEY="new-value"' in content
    
    def test_import_no_merge_overwrites(self, env_importer, temp_env_file, mock_op_client):
        """Test import without merge overwrites existing file."""
        # Create existing file
        temp_env_file.write_text('EXISTING_KEY="existing-value"\n')
        
        # Mock the 1Password item
        mock_field = Mock()
        mock_field.label = "NEW_KEY"
        mock_field.value = "new-value"
        
        mock_item = Mock()
        mock_item.fields = [mock_field]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        # Import without merge
        imported = env_importer.import_to_file("test-item", temp_env_file, merge_existing=False)
        
        assert len(imported) == 1
        assert imported["NEW_KEY"] == "new-value"
        
        # Check only new variables are present
        content = temp_env_file.read_text()
        assert 'EXISTING_KEY' not in content
        assert 'NEW_KEY="new-value"' in content
    
    def test_import_item_not_found(self, env_importer, mock_op_client):
        """Test import when item is not found."""
        mock_op_client.get_item_by_title.return_value = None
        
        with pytest.raises(OnePassEnvError, match="not found"):
            env_importer.import_to_file("nonexistent-item", "test.env")
    
    def test_import_authentication_failed(self, env_importer, mock_op_client):
        """Test import when authentication fails."""
        mock_op_client.is_authenticated.return_value = False
        
        with pytest.raises(OnePassEnvError, match="Not authenticated"):
            env_importer.import_to_file("test-item", "test.env")
    
    def test_import_no_fields(self, env_importer, temp_env_file, mock_op_client):
        """Test import when item has no valid fields."""
        # Mock item with no valid fields
        mock_field1 = Mock()
        mock_field1.label = None  # Invalid field
        mock_field1.value = "value"
        
        mock_field2 = Mock()
        mock_field2.label = "KEY"
        mock_field2.value = None  # Invalid field
        
        mock_item = Mock()
        mock_item.fields = [mock_field1, mock_field2]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        imported = env_importer.import_to_file("test-item", temp_env_file)
        
        assert len(imported) == 0
        # File should still be created with header
        assert temp_env_file.exists()
        content = temp_env_file.read_text()
        assert '# Environment variables imported from 1Password' in content
    
    def test_get_item_fields(self, env_importer, mock_op_client):
        """Test getting field names from an item."""
        # Mock the 1Password item
        mock_field1 = Mock()
        mock_field1.label = "API_KEY"
        mock_field1.value = "secret-api-key"
        
        mock_field2 = Mock()
        mock_field2.label = "DB_PASSWORD"
        mock_field2.value = "secret-db-password"
        
        mock_field3 = Mock()  # Invalid field
        mock_field3.label = None
        mock_field3.value = "value"
        
        mock_item = Mock()
        mock_item.fields = [mock_field1, mock_field2, mock_field3]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        fields = env_importer.get_item_fields("test-item")
        
        assert len(fields) == 2
        assert "API_KEY" in fields
        assert "DB_PASSWORD" in fields
    
    def test_get_item_fields_not_found(self, env_importer, mock_op_client):
        """Test getting fields when item is not found."""
        mock_op_client.get_item_by_title.return_value = None
        
        with pytest.raises(OnePassEnvError, match="not found"):
            env_importer.get_item_fields("nonexistent-item")
    
    def test_get_item_fields_authentication_failed(self, env_importer, mock_op_client):
        """Test getting fields when authentication fails."""
        mock_op_client.is_authenticated.return_value = False
        
        with pytest.raises(OnePassEnvError, match="Not authenticated"):
            env_importer.get_item_fields("test-item")
    
    def test_escape_quotes_in_values(self, env_importer, temp_env_file, mock_op_client):
        """Test that quotes in values are properly escaped."""
        # Mock item with value containing quotes
        mock_field = Mock()
        mock_field.label = "COMPLEX_VALUE"
        mock_field.value = 'value with "quotes" and more'
        
        mock_item = Mock()
        mock_item.fields = [mock_field]
        
        mock_op_client.get_item_by_title.return_value = mock_item
        
        imported = env_importer.import_to_file("test-item", temp_env_file)
        
        assert imported["COMPLEX_VALUE"] == 'value with "quotes" and more'
        
        # Check that quotes are escaped in the file
        content = temp_env_file.read_text()
        assert 'COMPLEX_VALUE="value with \\"quotes\\" and more"' in content
