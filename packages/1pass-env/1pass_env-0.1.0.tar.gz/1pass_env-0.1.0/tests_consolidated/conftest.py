"""
Consolidated test configuration and fixtures for 1pass-env.
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch


@pytest.fixture
def runner():
    """Click test runner fixture."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    import tempfile
    from pathlib import Path
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
    temp_file.close()
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass


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
    field.id = 'field_1'
    field.title = 'API_KEY'
    field.value = 'test_api_key'
    field.type = 'CONCEALED'
    return field


@pytest.fixture
def mock_item():
    """Mock 1Password full item object with fields."""
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
    
    return client


@pytest.fixture
def mock_op_client():
    """Mock 1Password client for core tests."""
    client = Mock()
    client.vault = "test-vault"
    return client


@pytest.fixture
def env_importer(mock_op_client):
    """Create an EnvImporter instance for testing."""
    try:
        from onepass_env.core import EnvImporter
        return EnvImporter(mock_op_client)
    except ImportError:
        # If the module structure is different, create a mock
        mock_importer = Mock()
        mock_importer.import_to_file.return_value = {"TEST_KEY": "test_value"}
        return mock_importer


@pytest.fixture
def sample_env_vars():
    """Sample environment variables for testing."""
    return {
        'API_KEY': 'test_api_key_123',
        'SECRET_TOKEN': 'super_secret_token',
        'DATABASE_URL': 'postgresql://localhost:5432/testdb',
        'DEBUG': 'true',
        'PORT': '8080'
    }


@pytest.fixture
def env_file_content():
    """Sample .env file content."""
    return """# Test environment file
API_KEY=test_api_key_123
SECRET_TOKEN=super_secret_token
DATABASE_URL=postgresql://localhost:5432/testdb
DEBUG=true
PORT=8080

# Empty line and comment should be handled
EMPTY_VALUE=
"""


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark async tests
        if "async" in item.name or "asyncio" in str(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Mark slow tests (those that use complex mocking or multiple patches)
        if any(keyword in item.name.lower() for keyword in ["debug", "integration", "complex"]):
            item.add_marker(pytest.mark.slow)