"""
Shared pytest configuration and fixtures.
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock


@pytest.fixture(scope="session")
def temp_test_dir():
    """Create a temporary directory for the entire test session."""
    temp_path = tempfile.mkdtemp(prefix="1pass_env_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_1password_client():
    """Create a comprehensive mock 1Password client."""
    client = AsyncMock()
    
    # Mock vault
    vault = Mock()
    vault.id = 'test_vault_id_123'
    vault.title = 'tokens'
    
    # Mock multiple vaults for testing
    vault2 = Mock()
    vault2.id = 'test_vault_id_456'
    vault2.title = 'development'
    
    client.vaults.list.return_value = [vault, vault2]
    
    # Mock item overviews
    item1 = Mock()
    item1.id = 'item_id_123'
    item1.title = 'test-project'
    
    item2 = Mock()
    item2.id = 'item_id_456'
    item2.title = 'test-project-dev'
    
    client.items.list.return_value = [item1, item2]
    
    # Mock full item with fields
    full_item = Mock()
    full_item.id = 'item_id_123'
    full_item.title = 'test-project'
    
    # Create various field types
    fields = []
    
    # Standard field
    field1 = Mock()
    field1.id = 'username'
    field1.title = 'API_KEY'
    field1.value = 'test_api_key_value'
    field1.type = 'CONCEALED'
    fields.append(field1)
    
    # Password field
    field2 = Mock()
    field2.id = 'password'
    field2.title = 'SECRET_TOKEN'
    field2.value = 'secret_token_value'
    field2.type = 'CONCEALED'
    fields.append(field2)
    
    # Text field
    field3 = Mock()
    field3.id = 'notes'
    field3.title = 'DATABASE_URL'
    field3.value = 'postgresql://localhost:5432/testdb'
    field3.type = 'STRING'
    fields.append(field3)
    
    # Field with minimal attributes (edge case)
    field4 = Mock()
    field4.id = 'minimal_field'
    field4.value = 'minimal_value'
    # Remove title and type attributes
    if hasattr(field4, 'title'):
        delattr(field4, 'title')
    if hasattr(field4, 'type'):
        delattr(field4, 'type')
    fields.append(field4)
    
    full_item.fields = fields
    client.items.get.return_value = full_item
    
    # Mock item creation
    client.items.create.return_value = Mock(id='new_item_123')
    
    return client


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
        if "async" in item.name.lower():
            item.add_marker(pytest.mark.asyncio)
        
        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["complex", "comprehensive", "large"]):
            item.add_marker(pytest.mark.slow)