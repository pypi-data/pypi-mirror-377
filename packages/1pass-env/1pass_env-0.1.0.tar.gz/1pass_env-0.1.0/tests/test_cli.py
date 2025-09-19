"""Tests for the CLI module - import command only."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from pathlib import Path

from onepass_env.cli import cli


class TestImportCLI:
    """Test cases for the import CLI command."""
    
    def test_version(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1pass-env version' in result.output
    
    def test_help(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Import environment variables from 1Password' in result.output
    
    def test_no_command_shows_welcome(self):
        """Test that running without a command shows welcome message."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert '1pass-env' in result.output
        assert 'import' in result.output
    
    def test_import_help(self):
        """Test import command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '--help'])
        assert result.exit_code == 0
        assert 'Import environment variables from a 1Password item' in result.output
        assert '--vault' in result.output
        assert '--name' in result.output
        assert '--fields' in result.output
        assert '--file' in result.output
        assert '--debug' in result.output
    
    @patch.dict('os.environ', {}, clear=True)
    def test_import_no_token(self):
        """Test import command when service account token is not set."""
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '--name', 'test-item'])
        
        assert result.exit_code == 1
        assert 'OP_SERVICE_ACCOUNT_TOKEN environment variable not set' in result.output
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_command_success(self, mock_op_client_class):
        """Test successful import command."""
        # Mock the 1Password client
        mock_field1 = Mock()
        mock_field1.label = "API_KEY"
        mock_field1.value = "secret-api-key"
        
        mock_field2 = Mock()
        mock_field2.label = "DB_PASSWORD"
        mock_field2.value = "secret-db-password"
        
        mock_item = Mock()
        mock_item.title = "test-project"
        mock_item.id = "item-123"
        mock_item.fields = [mock_field1, mock_field2]
        
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_client.get_item_by_title.return_value = mock_item
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['import', '--name', 'test-project'])
            
            assert result.exit_code == 0
            assert 'Successfully imported 2 variables' in result.output
            assert 'Saved to: 1pass.env' in result.output
            
            # Check that file was created
            assert Path('1pass.env').exists()
            
            # Check file contents
            content = Path('1pass.env').read_text()
            assert 'API_KEY="secret-api-key"' in content
            assert 'DB_PASSWORD="secret-db-password"' in content
            assert '# Environment variables imported from 1Password' in content
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_with_fields_filter(self, mock_op_client_class):
        """Test import command with fields filter."""
        # Mock the 1Password client
        mock_field1 = Mock()
        mock_field1.label = "API_KEY"
        mock_field1.value = "secret-api-key"
        
        mock_field2 = Mock()
        mock_field2.label = "DB_PASSWORD"
        mock_field2.value = "secret-db-password"
        
        mock_item = Mock()
        mock_item.title = "test-project"
        mock_item.id = "item-123"
        mock_item.fields = [mock_field1, mock_field2]
        
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_client.get_item_by_title.return_value = mock_item
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['import', '--name', 'test-project', '--fields', 'API_KEY'])
            
            assert result.exit_code == 0
            assert 'Successfully imported 1 variables' in result.output
            
            # Check file contents - should only have API_KEY
            content = Path('1pass.env').read_text()
            assert 'API_KEY="secret-api-key"' in content
            assert 'DB_PASSWORD' not in content
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_custom_vault_and_file(self, mock_op_client_class):
        """Test import with custom vault and file."""
        mock_field = Mock()
        mock_field.label = "SECRET_KEY"
        mock_field.value = "super-secret"
        
        mock_item = Mock()
        mock_item.title = "my-app"
        mock_item.id = "item-456"
        mock_item.fields = [mock_field]
        
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_client.get_item_by_title.return_value = mock_item
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                'import', 
                '--vault', 'secrets', 
                '--name', 'my-app', 
                '--file', '.env.production'
            ])
            
            assert result.exit_code == 0
            assert 'Successfully imported 1 variables' in result.output
            assert 'Saved to: .env.production' in result.output
            
            # Check custom file was created
            assert Path('.env.production').exists()
            content = Path('.env.production').read_text()
            assert 'SECRET_KEY="super-secret"' in content
            assert '# Vault: secrets' in content
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_item_not_found(self, mock_op_client_class):
        """Test import when item is not found."""
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_client.get_item_by_title.return_value = None
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '--name', 'nonexistent-item'])
        
        assert result.exit_code == 1
        assert "Item 'nonexistent-item' not found" in result.output
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_authentication_failed(self, mock_op_client_class):
        """Test import when authentication fails."""
        mock_client = Mock()
        mock_client.is_authenticated.return_value = False
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(cli, ['import', '--name', 'test-item'])
        
        assert result.exit_code == 1
        assert "Not authenticated with 1Password" in result.output
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_with_existing_file(self, mock_op_client_class):
        """Test import when file already exists."""
        mock_field = Mock()
        mock_field.label = "NEW_KEY"
        mock_field.value = "new-value"
        
        mock_item = Mock()
        mock_item.title = "test-app"
        mock_item.id = "item-789"
        mock_item.fields = [mock_field]
        
        mock_client = Mock()
        mock_client.is_authenticated.return_value = True
        mock_client.get_item_by_title.return_value = mock_item
        mock_op_client_class.return_value = mock_client
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create existing file
            Path('1pass.env').write_text('EXISTING_KEY="existing-value"\n')
            
            # Import with confirmation
            result = runner.invoke(cli, ['import', '--name', 'test-app'], input='y\n')
            
            assert result.exit_code == 0
            
            # Check that both existing and new variables are present
            content = Path('1pass.env').read_text()
            assert 'EXISTING_KEY="existing-value"' in content
            assert 'NEW_KEY="new-value"' in content
    
    @patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'})
    @patch('onepass_env.cli.OnePasswordClient')
    def test_import_cancel_overwrite(self, mock_op_client_class):
        """Test import cancellation when file exists."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create existing file
            Path('1pass.env').write_text('EXISTING_KEY="existing-value"\n')
            
            # Import with cancellation
            result = runner.invoke(cli, ['import', '--name', 'test-app'], input='n\n')
            
            assert result.exit_code == 0
            assert 'Operation cancelled' in result.output
    
    def test_import_automatic_folder_name(self):
        """Test that import uses current folder name when --name is not provided."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a directory and change into it
            Path('my-project').mkdir()
            import os
            os.chdir('my-project')
            
            # Mock the environment and client
            with patch.dict('os.environ', {'OP_SERVICE_ACCOUNT_TOKEN': 'test-token'}):
                with patch('onepass_env.cli.OnePasswordClient') as mock_op_client_class:
                    mock_client = Mock()
                    mock_client.is_authenticated.return_value = True
                    mock_client.get_item_by_title.return_value = None  # Item not found
                    mock_op_client_class.return_value = mock_client
                    
                    result = runner.invoke(cli, ['import'])
                    
                    # Should try to find item with folder name 'my-project'
                    mock_client.get_item_by_title.assert_called_with('my-project')
                    assert result.exit_code == 1
                    assert "Item 'my-project' not found" in result.output
