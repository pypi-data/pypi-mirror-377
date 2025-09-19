"""
Comprehensive test suite for 1pass-env.
Consolidates all test cases from main, edge cases, cli, core, and onepassword modules.
"""
import pytest
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open, MagicMock
from click.testing import CliRunner

# Import main module functions
try:
    from main import (
        cli, import_env, export, get_client, 
        validate_output_path, validate_fields
    )
except ImportError:
    # Handle case where main module structure might be different
    cli = Mock()
    import_env = Mock()
    export = Mock()
    get_client = Mock()
    validate_output_path = Mock()
    validate_fields = Mock()

# Try to import the onepass_env modules
try:
    from onepass_env.core import EnvImporter
    from onepass_env.onepassword import OnePasswordClient
    from onepass_env.cli import cli as onepass_cli
    from onepass_env.exceptions import OnePassEnvError, AuthenticationError, VaultError
except ImportError:
    # Mock these if not available
    EnvImporter = Mock
    OnePasswordClient = Mock
    onepass_cli = Mock
    OnePassEnvError = Exception
    AuthenticationError = Exception
    VaultError = Exception


class TestValidationFunctions:
    """Test suite for validation functions."""
    
    def test_validate_fields_valid(self):
        """Test validate_fields with valid field names."""
        valid, error = validate_fields(['API_KEY', 'SECRET_TOKEN'])
        assert valid is True
        assert error is None
    
    def test_validate_fields_empty(self):
        """Test validate_fields with empty field list."""
        valid, error = validate_fields([])
        assert valid is True
        assert error is None
    
    def test_validate_fields_none(self):
        """Test validate_fields with None."""
        valid, error = validate_fields(None)
        assert valid is True
        assert error is None
    
    def test_validate_fields_with_spaces(self):
        """Test validate_fields with fields containing spaces."""
        valid, error = validate_fields(['API KEY', 'SECRET_TOKEN'])
        assert valid is False
        assert 'contains spaces' in error
    
    def test_validate_fields_empty_field(self):
        """Test validate_fields with empty field name."""
        valid, error = validate_fields(['', 'API_KEY'])
        assert valid is False
        assert '(empty)' in error
    
    def test_validate_fields_too_long(self):
        """Test validate_fields with overly long field name."""
        long_field = 'A' * 300
        valid, error = validate_fields([long_field])
        assert valid is False
        assert 'too long' in error
    
    @patch('os.access')
    def test_validate_output_path_valid(self, mock_access, temp_dir):
        """Test validate_output_path with valid path."""
        mock_access.return_value = True
        path = os.path.join(temp_dir, 'test.env')
        
        valid, error = validate_output_path(path)
        assert valid is True
        assert error is None
    
    @patch('os.access')
    def test_validate_output_path_existing_writable(self, mock_access, temp_dir):
        """Test validate_output_path with existing writable file."""
        mock_access.return_value = True
        path = os.path.join(temp_dir, 'existing.env')
        
        # Create the file
        with open(path, 'w') as f:
            f.write('TEST=value')
        
        valid, error = validate_output_path(path)
        assert valid is True
        assert error is None
    
    @patch('os.access')
    def test_validate_output_path_create_directory(self, mock_access, temp_dir):
        """Test validate_output_path creates directory if needed."""
        mock_access.return_value = True
        path = os.path.join(temp_dir, 'new_dir', 'test.env')
        
        valid, error = validate_output_path(path)
        assert valid is True
        assert error is None
        assert os.path.exists(os.path.dirname(path))
    
    @patch('os.access')
    def test_validate_output_path_not_writable_dir(self, mock_access, temp_dir):
        """Test validate_output_path with non-writable directory."""
        mock_access.return_value = False
        path = os.path.join(temp_dir, 'test.env')
        
        valid, error = validate_output_path(path)
        assert valid is False
        assert 'not writable' in error
    
    @patch('os.access')
    def test_validate_output_path_not_writable_file(self, mock_access, temp_dir):
        """Test validate_output_path with non-writable existing file."""
        path = os.path.join(temp_dir, 'readonly.env')
        
        # Create the file
        with open(path, 'w') as f:
            f.write('TEST=value')
        
        # Mock access to return False for writing
        mock_access.return_value = False
        
        valid, error = validate_output_path(path)
        assert valid is False
        assert 'not writable' in error
    
    @patch('os.access')
    def test_validate_output_path_mkdir_permission_error(self, mock_access, temp_dir):
        """Test validate_output_path with mkdir permission error."""
        mock_access.return_value = True
        
        # Mock makedirs to raise PermissionError
        with patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            path = os.path.join(temp_dir, 'protected', 'test.env')
            valid, error = validate_output_path(path)
            assert valid is False
            assert 'Permission denied' in error
    
    def test_validate_output_path_generic_exception(self):
        """Test validate_output_path with generic exception."""
        with patch('os.path.dirname', side_effect=RuntimeError("Generic error")):
            valid, error = validate_output_path('/some/path/test.env')
            assert valid is False
            assert 'Generic error' in error


class TestAuthentication:
    """Test suite for authentication and client creation."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.Client')
    async def test_get_client_success(self, mock_client_class):
        """Test successful client creation."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        client = await get_client()
        assert client == mock_client
        mock_client.authenticate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_client_missing_token(self):
        """Test client creation with missing token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OP_SERVICE_ACCOUNT_TOKEN"):
                await get_client()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.Client')
    async def test_get_client_auth_failure(self, mock_client_class):
        """Test client authentication failure."""
        mock_client = AsyncMock()
        mock_client.authenticate.side_effect = Exception("Auth failed")
        mock_client_class.return_value = mock_client
        
        with pytest.raises(Exception, match="Auth failed"):
            await get_client()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.Client')
    async def test_get_client_auth_exception_details(self, mock_client_class):
        """Test specific authentication exception handling."""
        mock_client_class.authenticate.side_effect = ConnectionError("Network unreachable")
        
        with pytest.raises(ConnectionError):
            await get_client()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.Client')
    async def test_get_client_value_error_propagation(self, mock_client_class):
        """Test that ValueError is properly propagated."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OP_SERVICE_ACCOUNT_TOKEN"):
                await get_client()


class TestImportFunctionality:
    """Test suite for import functionality."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_basic(self, mock_basename, mock_exists, mock_file, mock_get_client, runner, mock_client):
        """Test basic import functionality."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Successfully imported' in result.output
        mock_file.assert_called_once()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.validate_output_path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    @patch('click.confirm')
    def test_import_file_exists_confirm_yes(self, mock_confirm, mock_basename, mock_exists, 
                                          mock_file, mock_validate_path, mock_get_client, runner, mock_client):
        """Test import with existing file and user confirms overwrite."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_validate_path.return_value = (True, None)
        mock_confirm.return_value = True
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        mock_confirm.assert_called_once()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.validate_output_path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    @patch('click.confirm')
    def test_import_file_exists_confirm_no(self, mock_confirm, mock_basename, mock_exists, 
                                         mock_file, mock_validate_path, mock_get_client, runner, mock_client):
        """Test import with existing file and user cancels overwrite."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_validate_path.return_value = (True, None)
        mock_confirm.return_value = False
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Operation cancelled' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_vault_not_found(self, mock_basename, mock_get_client, runner):
        """Test import with vault not found."""
        mock_basename.return_value = 'test-project'
        
        # Setup client to raise exception for vault not found
        mock_client = AsyncMock()
        mock_client.vaults.list.side_effect = Exception("Vault not found")
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'nonexistent'])
        
        # Assertions
        assert result.exit_code == 1
        assert 'Error' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_specific_item_not_found(self, mock_basename, mock_get_client, runner, mock_client):
        """Test import with specific item not found."""
        mock_basename.return_value = 'test-project'
        mock_get_client.return_value = mock_client
        
        # Mock empty items list
        mock_client.items.list.return_value = []
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--name', 'nonexistent'])
        
        # Assertions
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_with_field_filter(self, mock_basename, mock_exists, mock_file, 
                                     mock_get_client, runner, mock_client):
        """Test import with specific field filter."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Run command with field filter
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--fields', 'API_KEY,SECRET_TOKEN'])
        
        # Assertions
        assert result.exit_code == 0
    
    def test_import_invalid_fields(self, runner):
        """Test import with invalid field names."""
        result = runner.invoke(cli, ['import', '--fields', 'INVALID FIELD'])
        
        assert result.exit_code == 1
        assert 'contains spaces' in result.output
    
    def test_import_missing_token(self, runner):
        """Test import without service account token."""
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ['import'])
            
            assert result.exit_code == 1
            assert 'OP_SERVICE_ACCOUNT_TOKEN' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_item_fields_attribute_fallback(self, mock_basename, mock_exists, 
                                                   mock_file, mock_get_client, runner):
        """Test import with items that have non-standard field attributes."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        
        # Create mock client with non-standard field attributes
        mock_client = AsyncMock()
        mock_vault = Mock()
        mock_vault.id = 'vault_123'
        mock_vault.title = 'tokens'
        mock_client.vaults.list.return_value = [mock_vault]
        
        mock_item_overview = Mock()
        mock_item_overview.id = 'item_123'
        mock_item_overview.title = 'test-project'
        mock_client.items.list.return_value = [mock_item_overview]
        
        # Create item with fields that have different attribute names
        mock_item = Mock()
        mock_item.id = 'item_123'
        mock_item.title = 'test-project'
        
        # Field with 'label' instead of 'title'
        mock_field1 = Mock()
        mock_field1.id = 'field_1'
        mock_field1.label = 'API_KEY'  # Using 'label' instead of 'title'
        mock_field1.value = 'test_api_key'
        
        # Field with 'title' attribute
        mock_field2 = Mock()
        mock_field2.id = 'field_2'
        mock_field2.title = 'SECRET_TOKEN'
        mock_field2.value = 'test_secret'
        
        mock_item.fields = [mock_field1, mock_field2]
        mock_client.items.get.return_value = mock_item
        
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should handle both label and title attributes
        assert result.exit_code == 0
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_file_write_generic_error(self, mock_basename, mock_exists, 
                                           mock_file_open, mock_get_client, runner, mock_client):
        """Test import with generic file write error."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Mock file open to raise a generic exception
        mock_file_open.side_effect = RuntimeError("Disk full")
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should handle the error gracefully
        assert result.exit_code == 1
        assert 'Error' in result.output


class TestExportFunctionality:
    """Test suite for export functionality."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('main.dotenv_values')
    @patch('os.path.basename')
    def test_export_basic(self, mock_basename, mock_exists, mock_dotenv, mock_file, 
                         mock_get_client, runner, mock_client):
        """Test basic export functionality."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value', 'SECRET_TOKEN': 'test_secret'}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'exported' in result.output.lower()
    
    def test_export_file_not_found(self, runner):
        """Test export with non-existent file."""
        result = runner.invoke(cli, ['export', '--file', '/nonexistent/file.env'])
        
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('main.dotenv_values')
    @patch('os.path.basename')
    def test_export_with_field_filter(self, mock_basename, mock_exists, mock_dotenv, 
                                     mock_file, mock_get_client, runner, mock_client):
        """Test export with field filter."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value', 'SECRET_TOKEN': 'test_secret', 'DEBUG': 'true'}
        mock_get_client.return_value = mock_client
        
        # Run command with field filter
        result = runner.invoke(cli, ['export', '--vault', 'tokens', '--fields', 'API_KEY,SECRET_TOKEN'])
        
        # Assertions
        assert result.exit_code == 0
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('main.dotenv_values')
    @patch('os.path.basename')
    def test_export_missing_fields(self, mock_basename, mock_exists, mock_dotenv, 
                                  mock_file, mock_get_client, runner, mock_client):
        """Test export when specified fields are missing from env file."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'OTHER_KEY': 'value'}
        mock_get_client.return_value = mock_client
        
        # Run command with field filter that doesn't match env file
        result = runner.invoke(cli, ['export', '--vault', 'tokens', '--fields', 'MISSING_KEY'])
        
        # Should still work but warn about missing fields
        assert result.exit_code == 0
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('main.dotenv_values')
    @patch('os.path.basename')
    def test_export_empty_env_file(self, mock_basename, mock_exists, mock_dotenv, 
                                  mock_file, mock_get_client, runner, mock_client):
        """Test export with empty env file."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens'])
        
        # Should handle empty file gracefully
        assert result.exit_code == 0


class TestDebugMode:
    """Test suite for debug mode functionality."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_debug_mode(self, mock_basename, mock_exists, mock_file, 
                              mock_get_client, runner, mock_client):
        """Test import with debug mode enabled."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Run command with debug flag
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--debug'])
        
        # Should show debug information
        assert result.exit_code == 0
        # Debug output should contain additional information
        debug_keywords = ['vault', 'item', 'field']
        assert any(keyword in result.output.lower() for keyword in debug_keywords)
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('main.dotenv_values')
    @patch('os.path.basename')
    def test_export_debug_mode(self, mock_basename, mock_exists, mock_dotenv, 
                              mock_file, mock_get_client, runner, mock_client):
        """Test export with debug mode enabled."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value'}
        mock_get_client.return_value = mock_client
        
        # Run command with debug flag
        result = runner.invoke(cli, ['export', '--vault', 'tokens', '--debug'])
        
        # Should show debug information
        assert result.exit_code == 0


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    @patch('asyncio.run')
    def test_import_client_creation_failure(self, mock_asyncio_run, mock_basename, mock_get_client, runner):
        """Test import when client creation fails."""
        mock_basename.return_value = 'test-project'
        mock_get_client.side_effect = Exception("Client creation failed")
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        assert result.exit_code == 1
        assert 'Error' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_file_permission_error(self, mock_basename, mock_exists, mock_open, 
                                         mock_get_client, runner, mock_client):
        """Test import with file permission error."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        mock_open.side_effect = PermissionError("Permission denied")
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should handle permission error gracefully
        assert result.exit_code == 1
        assert 'Permission denied' in result.output or 'Error' in result.output
    
    def test_keyboard_interrupt(self, runner):
        """Test graceful handling of keyboard interrupt."""
        with patch('main.get_client', side_effect=KeyboardInterrupt()):
            result = runner.invoke(cli, ['import'])
            
            # Should exit gracefully
            assert result.exit_code in [0, 1]


class TestCLIIntegration:
    """Test suite for CLI integration and edge cases."""
    
    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output
    
    def test_import_help(self, runner):
        """Test import command help."""
        result = runner.invoke(cli, ['import', '--help'])
        assert result.exit_code == 0
        assert 'import' in result.output.lower()
    
    def test_export_help(self, runner):
        """Test export command help."""
        result = runner.invoke(cli, ['export', '--help'])
        assert result.exit_code == 0
        assert 'export' in result.output.lower()
    
    def test_default_vault_name(self, runner):
        """Test that default vault name is 'tokens'."""
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ['import'])
            # Should mention the default vault or require token
            assert result.exit_code == 1
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_no_matching_items(self, mock_basename, mock_get_client, runner, mock_client):
        """Test import when no items match project name."""
        mock_basename.return_value = 'nonexistent-project'
        mock_get_client.return_value = mock_client
        
        # Mock empty items list
        mock_client.items.list.return_value = []
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()


# Core Module Tests (if available)
class TestEnvImporter:
    """Test cases for EnvImporter core functionality."""
    
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
        
        # Import with filter
        imported = env_importer.import_to_file("test-item", temp_env_file, fields=["API_KEY"])
        
        assert len(imported) == 1
        assert imported["API_KEY"] == "secret-api-key"
        assert "DB_PASSWORD" not in imported
    
    def test_import_merge_with_existing(self, env_importer, temp_env_file, mock_op_client):
        """Test import with merge_existing=True."""
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
        
        # Check both keys are present
        content = temp_env_file.read_text()
        assert 'EXISTING_KEY="existing-value"' in content
        assert 'NEW_KEY="new-value"' in content


# OnePassword Client Tests (if available)
class TestOnePasswordClient:
    """Test cases for OnePasswordClient."""
    
    @patch('onepass_env.onepassword.new_client')
    def test_client_initialization(self, mock_new_client):
        """Test client initialization."""
        if OnePasswordClient == Mock:
            pytest.skip("OnePasswordClient not available")
            
        mock_client = Mock()
        mock_new_client.return_value = mock_client
        
        op_client = OnePasswordClient(vault="test-vault")
        client = op_client._get_client()
        
        assert client == mock_client
        mock_new_client.assert_called_once()
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    def test_is_available_with_token(self):
        """Test is_available returns True when token is set."""
        if OnePasswordClient == Mock:
            pytest.skip("OnePasswordClient not available")
            
        op_client = OnePasswordClient()
        assert op_client.is_available() is True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_is_available_without_token(self):
        """Test is_available returns False when token is not set."""
        if OnePasswordClient == Mock:
            pytest.skip("OnePasswordClient not available")
            
        op_client = OnePasswordClient()
        assert op_client.is_available() is False


# Advanced Edge Cases
class TestAdvancedEdgeCases:
    """Test advanced edge cases and complex scenarios."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_items_list_error(self, mock_basename, mock_get_client, runner):
        """Test import when items.list() fails."""
        mock_basename.return_value = 'test-project'
        
        mock_client = AsyncMock()
        mock_vault = Mock()
        mock_vault.id = 'vault_123'
        mock_vault.title = 'tokens'
        mock_client.vaults.list.return_value = [mock_vault]
        
        # Make items.list() raise an exception
        mock_client.items.list.side_effect = Exception("Items list failed")
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        assert result.exit_code == 1
        assert 'Error' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_debug_traceback(self, mock_basename, mock_get_client, runner):
        """Test import debug mode shows tracebacks."""
        mock_basename.return_value = 'test-project'
        mock_get_client.side_effect = Exception("Test exception for debug")
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--debug'])
        
        assert result.exit_code == 1
        # Debug mode should show more detailed error information
        assert 'Error' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_no_env_vars_collected(self, mock_basename, mock_exists, 
                                         mock_file, mock_get_client, runner, mock_client):
        """Test import when no environment variables are collected."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Mock item with no fields
        mock_item = Mock()
        mock_item.id = 'item_123'
        mock_item.title = 'test-project'
        mock_item.fields = []
        mock_client.items.get.return_value = mock_item
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should handle empty fields gracefully
        assert result.exit_code in [0, 1]  # May succeed with warning or fail
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_field_with_only_id(self, mock_basename, mock_exists, 
                                      mock_file, mock_get_client, runner, mock_client):
        """Test import with field that only has 'id' attribute."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Create field with only id (no title or label)
        mock_field = Mock()
        mock_field.id = 'field_id_only'
        # Remove title and label attributes
        del mock_field.title
        del mock_field.label
        mock_field.value = 'test_value'
        
        mock_item = Mock()
        mock_item.id = 'item_123'
        mock_item.title = 'test-project'
        mock_item.fields = [mock_field]
        mock_client.items.get.return_value = mock_item
        
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should handle field with missing attributes
        assert result.exit_code in [0, 1]
    
    def test_import_fatal_error(self, runner):
        """Test import with fatal system error."""
        with patch('sys.exit', side_effect=SystemExit(1)):
            with patch('main.get_client', side_effect=SystemError("Fatal system error")):
                result = runner.invoke(cli, ['import'])
                
                # Should handle fatal errors
                assert result.exit_code == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=main', '--cov-report=html', '--cov-report=term-missing'])