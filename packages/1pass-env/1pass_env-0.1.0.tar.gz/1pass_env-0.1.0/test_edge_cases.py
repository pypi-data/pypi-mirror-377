"""
Additional comprehensive tests for edge cases and async scenarios.
This file extends the main test suite to achieve 95%+ coverage.
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open, MagicMock
from click.testing import CliRunner
import tempfile
import shutil

from main import cli, get_client


@pytest.fixture
def runner():
    """Click test runner fixture."""
    return CliRunner()


class TestAsyncEdgeCases:
    """Test async edge cases and complex scenarios."""
    
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


class TestComplexImportScenarios:
    """Test complex import scenarios and edge cases."""
    
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
        
        # Create a client with items that have unusual field attributes
        mock_client = AsyncMock()
        
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        item_overview = Mock()
        item_overview.id = 'item_123'
        item_overview.title = 'test-project'
        mock_client.items.list.return_value = [item_overview]
        
        # Create item with fields that only have 'id' attribute (no title/label)
        item = Mock()
        item.id = 'item_123'
        item.title = 'test-project'
        
        field = Mock()
        field.id = 'field_1'
        # Remove title and label attributes, only id exists
        del field.title
        field.value = 'test_value'
        field.type = 'CONCEALED'
        
        item.fields = [field]
        mock_client.items.get.return_value = item
        mock_get_client.return_value = mock_client
        
        # Run command
        result = runner.invoke(cli, ['import', '--vault', 'tokens'])
        
        # Should still work, using field.id as fallback
        assert result.exit_code == 0
        assert 'Successfully imported' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_file_write_generic_error(self, mock_basename, mock_exists, 
                                           mock_open, mock_get_client, runner):
        """Test import with generic file write error."""
        # Setup mocks
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        item_overview = Mock()
        item_overview.id = 'item_123'
        item_overview.title = 'test-project'
        mock_client.items.list.return_value = [item_overview]
        
        item = Mock()
        item.fields = [Mock(id='f1', title='TEST_VAR', value='value', type='TEXT')]
        mock_client.items.get.return_value = item
        mock_get_client.return_value = mock_client
        
        # Make file writing fail with generic error
        mock_open.side_effect = IOError("Disk full")
        
        result = runner.invoke(cli, ['import'])
        
        assert result.exit_code == 0
        assert 'Error: Failed to write file' in result.output
        assert 'Disk full' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_items_list_error(self, mock_basename, mock_get_client, runner):
        """Test import when items.list fails."""
        mock_basename.return_value = 'test-project'
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        # Make items.list fail
        mock_client.items.list.side_effect = Exception("API rate limit exceeded")
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import', '--name', 'test-item'])
        
        assert result.exit_code == 0
        assert 'Error: Failed to fetch items from vault' in result.output
        assert 'API rate limit exceeded' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('os.path.basename')
    def test_import_debug_traceback(self, mock_basename, mock_get_client, runner):
        """Test import debug mode shows full traceback on error."""
        mock_basename.return_value = 'test-project'
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        # Make items.list fail
        mock_client.items.list.side_effect = Exception("Test error for traceback")
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import', '--debug', '--name', 'test-item'])
        
        assert result.exit_code == 0
        assert 'Debug: Full traceback:' in result.output
        assert 'Traceback' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_no_env_vars_collected(self, mock_basename, mock_exists, 
                                         mock_file, mock_get_client, runner):
        """Test import when no environment variables are collected."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        item_overview = Mock()
        item_overview.id = 'item_123'
        item_overview.title = 'test-project'
        mock_client.items.list.return_value = [item_overview]
        
        # Item with no fields
        item = Mock()
        item.fields = []
        mock_client.items.get.return_value = item
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import'])
        
        assert result.exit_code == 0
        assert 'Warning: No environment variables found to import' in result.output


class TestComplexExportScenarios:
    """Test complex export scenarios and edge cases."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_dotenv_read_error(self, mock_basename, mock_exists, 
                                     mock_dotenv, mock_get_client, runner):
        """Test export when dotenv_values fails."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.side_effect = Exception("File encoding error")
        
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['export'])
        
        assert result.exit_code == 0
        assert 'Error: Failed to read file' in result.output
        assert 'File encoding error' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_vault_list_error(self, mock_basename, mock_exists, 
                                    mock_dotenv, mock_get_client, runner):
        """Test export when vault listing fails."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'TEST': 'value'}
        
        mock_client = AsyncMock()
        mock_client.vaults.list.side_effect = Exception("Network timeout")
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['export'])
        
        assert result.exit_code == 0
        assert 'Error: Failed to list vaults' in result.output
        assert 'Network timeout' in result.output
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('main.dotenv_values')
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_export_item_create_error(self, mock_basename, mock_exists, 
                                     mock_dotenv, mock_get_client, runner):
        """Test export when item creation fails."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = True
        mock_dotenv.return_value = {'TEST': 'value'}
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        mock_client.items.create.side_effect = Exception("Insufficient permissions")
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['export'])
        
        assert result.exit_code == 0
        assert 'Error: Failed to create item in vault' in result.output
        assert 'Insufficient permissions' in result.output


class TestValidationEdgeCases:
    """Test validation edge cases."""
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('os.access')
    def test_validate_output_path_mkdir_permission_error(self, mock_access, 
                                                        mock_exists, mock_makedirs):
        """Test validate_output_path when mkdir fails with permission error."""
        from main import validate_output_path
        
        mock_exists.return_value = False
        mock_makedirs.side_effect = PermissionError("Cannot create directory")
        
        valid, error = validate_output_path('/restricted/path/file.env')
        
        assert valid is False
        assert 'Cannot create directory' in error
    
    def test_validate_output_path_generic_exception(self):
        """Test validate_output_path with generic exception."""
        from main import validate_output_path
        
        with patch('os.path.dirname', side_effect=Exception("Unexpected error")):
            valid, error = validate_output_path('/some/path/file.env')
            
            assert valid is False
            assert 'Path validation error' in error
            assert 'Unexpected error' in error


class TestFatalErrorHandling:
    """Test fatal error scenarios."""
    
    def test_import_fatal_error(self, runner):
        """Test import command fatal error handling."""
        with patch('asyncio.run', side_effect=Exception("Fatal system error")):
            result = runner.invoke(cli, ['import'])
            
            assert result.exit_code == 0
            assert 'Fatal error: Fatal system error' in result.output
    
    def test_export_fatal_error(self, runner):
        """Test export command fatal error handling."""
        # Create a temporary file first to bypass the file validation
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=test_value\n')
            temp_file = f.name
        
        try:
            with patch('asyncio.run', side_effect=Exception("Fatal system error")):
                result = runner.invoke(cli, ['export', '--file', temp_file])
                
                assert result.exit_code == 0
                assert 'Fatal error: Fatal system error' in result.output
        finally:
            # Clean up
            import os
            try:
                os.unlink(temp_file)
            except OSError:
                pass


class TestFieldAttributeVariations:
    """Test different field attribute combinations."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_field_with_only_id(self, mock_basename, mock_exists, 
                                      mock_file, mock_get_client, runner):
        """Test import with field that only has id attribute."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        item_overview = Mock()
        item_overview.id = 'item_123'
        item_overview.title = 'test-project'
        mock_client.items.list.return_value = [item_overview]
        
        # Create field with minimal attributes
        field = Mock()
        field.id = 'minimal_field'
        field.value = 'test_value'
        # Ensure other attributes don't exist
        if hasattr(field, 'title'):
            delattr(field, 'title')
        if hasattr(field, 'label'):
            delattr(field, 'label')
        if hasattr(field, 'type'):
            delattr(field, 'type')
        
        item = Mock()
        item.fields = [field]
        mock_client.items.get.return_value = item
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import', '--debug'])
        
        assert result.exit_code == 0
        # Should use field.id as the key
        assert 'Successfully imported' in result.output


class TestDebugOutputCoverage:
    """Test debug output coverage for edge cases."""
    
    @patch.dict(os.environ, {'OP_SERVICE_ACCOUNT_TOKEN': 'test_token'})
    @patch('main.get_client')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.path.basename')
    def test_import_debug_sample_field_attributes(self, mock_basename, mock_exists, 
                                                 mock_file, mock_get_client, runner):
        """Test debug output showing sample field attributes."""
        mock_basename.return_value = 'test-project'
        mock_exists.return_value = False
        
        mock_client = AsyncMock()
        vault = Mock()
        vault.id = 'vault_123'
        vault.title = 'tokens'
        mock_client.vaults.list.return_value = [vault]
        
        # Multiple items to trigger sample field debug output
        item1 = Mock()
        item1.id = 'item_1'
        item1.title = 'test-project-1'
        
        item2 = Mock()
        item2.id = 'item_2'
        item2.title = 'test-project-2'
        
        mock_client.items.list.return_value = [item1, item2]
        
        # Create item with fields
        field = Mock()
        field.id = 'field_1'
        field.title = 'TEST_VAR'
        field.value = 'test_value'
        field.type = 'TEXT'
        
        item = Mock()
        item.fields = [field]
        mock_client.items.get.return_value = item
        mock_get_client.return_value = mock_client
        
        result = runner.invoke(cli, ['import', '--debug'])
        
        assert result.exit_code == 0
        # Should show sample field attributes for first item
        assert 'Debug: Sample field attributes:' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])