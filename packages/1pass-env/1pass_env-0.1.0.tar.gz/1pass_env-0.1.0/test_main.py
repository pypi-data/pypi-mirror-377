import pytest
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open, MagicMock
from click.testing import CliRunner
import tempfile
import shutil
from pathlib import Path

# Import the main module
from main import (
    cli, import_env, export, get_client, 
    validate_output_path, validate_fields
)


# Test Fixtures
@pytest.fixture
def runner():
    """Click test runner fixture."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_env_file(temp_dir):
    """Create a sample .env file for testing."""
    env_path = os.path.join(temp_dir, '.env')
    with open(env_path, 'w') as f:
        f.write('API_KEY=test_api_key\n')
        f.write('SECRET_TOKEN=test_secret\n')
        f.write('DATABASE_URL=postgresql://localhost:5432/testdb\n')
    return env_path


@pytest.fixture
def mock_vault():
    """Mock 1Password vault object."""
    vault = Mock()
    vault.id = 'vault_123'
    vault.title = 'tokens'
    return vault


@pytest.fixture
def mock_item_overview():
    """Mock 1Password item overview object."""
    item = Mock()
    item.id = 'item_123'
    item.title = 'test-project'
    return item


@pytest.fixture
def mock_item_field():
    """Mock 1Password item field object."""
    field = Mock()
    field.id = 'field_123'
    field.title = 'API_KEY'
    field.value = 'test_value_123'
    field.type = 'CONCEALED'
    return field


@pytest.fixture
def mock_item():
    """Mock 1Password full item object with fields."""
    item = Mock()
    item.id = 'item_123'
    item.title = 'test-project'
    
    # Create mock fields
    field1 = Mock()
    field1.id = 'field_1'
    field1.title = 'API_KEY'
    field1.value = 'test_api_key'
    field1.type = 'CONCEALED'
    
    field2 = Mock()
    field2.id = 'field_2'
    field2.title = 'SECRET_TOKEN'
    field2.value = 'test_secret'
    field2.type = 'CONCEALED'
    
    item.fields = [field1, field2]
    return item


@pytest.fixture
def mock_client():
    """Mock 1Password client with common operations."""
    client = AsyncMock()
    
    # Mock vaults
    vault = Mock()
    vault.id = 'vault_123'
    vault.title = 'tokens'
    client.vaults.list.return_value = [vault]
    
    # Mock items
    item_overview = Mock()
    item_overview.id = 'item_123'
    item_overview.title = 'test-project'
    client.items.list.return_value = [item_overview]
    
    # Mock full item
    item = Mock()
    item.id = 'item_123'
    item.title = 'test-project'
    
    field1 = Mock()
    field1.id = 'field_1'
    field1.title = 'API_KEY'
    field1.value = 'test_api_key'
    field1.type = 'CONCEALED'
    
    field2 = Mock()
    field2.id = 'field_2'
    field2.title = 'SECRET_TOKEN'
    field2.value = 'test_secret'
    field2.type = 'CONCEALED'
    
    item.fields = [field1, field2]
    client.items.get.return_value = item
    client.items.create.return_value = Mock()
    
    return client


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
        long_field = 'A' * 101  # 101 characters
        valid, error = validate_fields([long_field])
        assert valid is False
        assert 'too long' in error
    
    def test_validate_output_path_valid(self, temp_dir):
        """Test validate_output_path with valid path."""
        test_file = os.path.join(temp_dir, 'test.env')
        valid, error = validate_output_path(test_file)
        assert valid is True
        assert error is None
    
    def test_validate_output_path_existing_writable(self, temp_dir):
        """Test validate_output_path with existing writable file."""
        test_file = os.path.join(temp_dir, 'existing.env')
        with open(test_file, 'w') as f:
            f.write('TEST=value\n')
        
        valid, error = validate_output_path(test_file)
        assert valid is True
        assert error is None
    
    def test_validate_output_path_create_directory(self, temp_dir):
        """Test validate_output_path creates missing directories."""
        nested_file = os.path.join(temp_dir, 'new_dir', 'test.env')
        valid, error = validate_output_path(nested_file)
        assert valid is True
        assert error is None
        assert os.path.exists(os.path.dirname(nested_file))
    
    @patch('os.access')
    def test_validate_output_path_not_writable_dir(self, mock_access, temp_dir):
        """Test validate_output_path with non-writable directory."""
        mock_access.return_value = False
        test_file = os.path.join(temp_dir, 'test.env')
        
        valid, error = validate_output_path(test_file)
        assert valid is False
        assert 'not writable' in error
    
    @patch('os.access')
    def test_validate_output_path_not_writable_file(self, mock_access, temp_dir):
        """Test validate_output_path with existing non-writable file."""
        test_file = os.path.join(temp_dir, 'readonly.env')
        with open(test_file, 'w') as f:
            f.write('TEST=value\n')
        
        # Mock file as not writable
        def mock_access_func(path, mode):
            if path == test_file and mode == os.W_OK:
                return False
            return True
        
        mock_access.side_effect = mock_access_func
        
        valid, error = validate_output_path(test_file)
        assert valid is False
        assert 'not writable' in error


class TestAuthentication:
    """Test suite for authentication and client creation."""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.Client')
    async def test_get_client_success(self, mock_client_class):
        """Test successful client authentication."""
        mock_client = AsyncMock()
        mock_client_class.authenticate = AsyncMock(return_value=mock_client)
        
        client = await get_client()
        
        mock_client_class.authenticate.assert_called_once_with(
            auth='test_token',
            integration_name="My 1Password Integration",
            integration_version="v1.0.0"
        )
        assert client == mock_client
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {}, clear=True)
    async def test_get_client_missing_token(self):
        """Test client creation with missing token."""
        with pytest.raises(ValueError, match="OP_SERVICE_ACCOUNT_TOKEN environment variable is required"):
            await get_client()
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'invalid_token'})
    @patch('main.Client')
    async def test_get_client_auth_failure(self, mock_client_class):
        """Test client authentication failure."""
        mock_client_class.authenticate.side_effect = Exception("Authentication failed")
        
        with pytest.raises(Exception, match="Authentication failed"):
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
        mock_confirm.return_value = True
        mock_validate_path.return_value = (True, None)  # Mock validation success
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Successfully imported' in result.output
        mock_confirm.assert_called_once()
        mock_file.assert_called_once()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.validate_output_path')
    @patch('os.path.exists')
    @patch('os.path.basename')
    @patch('click.confirm')
    def test_import_file_exists_confirm_no(self, mock_confirm, mock_basename, mock_exists, 
                                         mock_validate_path, mock_get_client, runner, mock_client):
        """Test import with existing file and user cancels overwrite."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_confirm.return_value = False
        mock_validate_path.return_value = (True, None)  # Mock validation success
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Operation cancelled' in result.output
        mock_confirm.assert_called_once()
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_vault_not_found(self, mock_basename, mock_get_client, runner):
        """Test import with non-existent vault."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_client = AsyncMock()
        mock_client.vaults.list.return_value = []
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'nonexistent'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Vault \'nonexistent\' not found' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_specific_item_not_found(self, mock_basename, mock_get_client, runner, mock_client):
        """Test import with specific item that doesn't exist."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_client.items.list.return_value = []
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--name', 'nonexistent'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Item \'nonexistent\' not found' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_with_field_filter(self, mock_basename, mock_exists, mock_file, 
                                    mock_get_client, runner, mock_client):
        """Test import with field filtering."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens', '--fields', 'API_KEY'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Successfully imported' in result.output
    
    def test_import_invalid_fields(self, runner):
        """Test import with invalid field names."""
        result = runner.invoke(cli, ['import', '--fields', 'INVALID FIELD'])
        
        assert result.exit_code == 0
        assert 'Validation Error' in result.output
        assert 'contains spaces' in result.output
    
    @patch.dict(os.environ, {}, clear=True)
    def test_import_missing_token(self, runner):
        """Test import with missing authentication token."""
        result = runner.invoke(cli, ['import'])
        
        assert result.exit_code == 0
        assert 'Configuration Error' in result.output


class TestExportFunctionality:
    """Test suite for export functionality."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_basic(self, mock_basename, mock_exists, mock_dotenv, mock_get_client, 
                         runner, mock_client):
        """Test basic export functionality."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value', 'SECRET': 'test_secret'}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Successfully exported' in result.output
        mock_client.items.create.assert_called_once()
    
    def test_export_file_not_found(self, runner):
        """Test export with non-existent input file."""
        result = runner.invoke(cli, ['export', '--file', 'nonexistent.env'])
        
        assert result.exit_code == 0
        assert 'Validation Error' in result.output
        assert 'not found' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_with_field_filter(self, mock_basename, mock_exists, mock_dotenv, 
                                     mock_get_client, runner, mock_client):
        """Test export with field filtering."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value', 'SECRET': 'test_secret', 'OTHER': 'value'}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens', '--fields', 'API_KEY'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Successfully exported' in result.output
        assert 'Filtered' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_missing_fields(self, mock_basename, mock_exists, mock_dotenv, 
                                  mock_get_client, runner, mock_client):
        """Test export with fields not found in file."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value'}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens', '--fields', 'MISSING_FIELD'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Warning: Fields not found' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_empty_env_file(self, mock_basename, mock_exists, mock_dotenv, 
                                  mock_get_client, runner, mock_client):
        """Test export with empty env file."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {}
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['export', '--vault', 'tokens'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'No environment variables found' in result.output


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
        
        # Run command with debug
        result = runner.invoke(cli, ['import', '--debug'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Debug:' in result.output
        assert 'Successfully authenticated' in result.output
        assert 'Fetching vault list' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_debug_mode(self, mock_basename, mock_exists, mock_dotenv, 
                              mock_get_client, runner, mock_client):
        """Test export with debug mode enabled."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'API_KEY': 'test_value'}
        mock_get_client.return_value = mock_client
        
        # Run command with debug
        result = runner.invoke(cli, ['export', '--debug'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Debug:' in result.output


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    @patch('asyncio.run')
    def test_import_client_creation_failure(self, mock_asyncio_run, mock_basename, mock_get_client, runner):
        """Test import when client creation fails."""
        mock_basename.return_value = 'test-project'
        
        # Mock get_client to raise exception during asyncio.run
        def mock_run(coro_func):
            # Simulate the async function running and failing
            import asyncio
            try:
                return asyncio.run(coro_func)
            except Exception:
                raise ConnectionError("Connection failed")
        
        mock_asyncio_run.side_effect = mock_run
        mock_get_client.side_effect = ConnectionError("Connection failed")
        
        result = runner.invoke(cli, ['import'])
        
        # The CLI should handle the error and print a message
        assert result.exit_code == 0  # CLI handles the error gracefully
        # Check that some error message is present
        assert 'Fatal error' in result.output or 'Connection failed' in result.output or 'Error' in result.output
    
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
        result = runner.invoke(cli, ['import'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'Permission denied' in result.output
    
    def test_keyboard_interrupt(self, runner):
        """Test graceful handling of keyboard interrupt."""
        with patch('asyncio.run', side_effect=KeyboardInterrupt()):
            result = runner.invoke(cli, ['import'])
            
            assert result.exit_code == 0
            assert 'Operation cancelled by user' in result.output


class TestCLIIntegration:
    """Test suite for CLI integration and edge cases."""
    
    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'CLI tool to integrate with 1Password' in result.output
    
    def test_import_help(self, runner):
        """Test import command help."""
        result = runner.invoke(cli, ['import', '--help'])
        
        assert result.exit_code == 0
        assert 'Import env vars from 1Password vault' in result.output
    
    def test_export_help(self, runner):
        """Test export command help."""
        result = runner.invoke(cli, ['export', '--help'])
        
        assert result.exit_code == 0
        assert 'Export env vars from .env file' in result.output
    
    def test_default_vault_name(self, runner):
        """Test that default vault name is 'tokens'."""
        # This test checks that the default is properly set
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ['import'])
            
            assert result.exit_code == 0
            assert "vault 'tokens'" in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_no_matching_items(self, mock_basename, mock_get_client, runner, mock_client):
        """Test import when no items match project name."""
        # Setup mocks
        mock_basename.return_value = 'nonexistent-project'
        mock_client.items.list.return_value = []
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import'])
        
        # Assertions
        assert result.exit_code == 0
        assert 'No items found containing' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=main', '--cov-report=html', '--cov-report=term-missing'])