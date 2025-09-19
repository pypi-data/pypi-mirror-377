"""Test configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from onepass_env.core import EnvImporter
from onepass_env.onepassword import OnePasswordClient


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        env_file = Path(f.name)
        yield env_file
        # Cleanup
        if env_file.exists():
            env_file.unlink()


@pytest.fixture
def mock_op_client():
    """Mock 1Password client."""
    with patch('onepass_env.core.OnePasswordClient') as mock:
        client = Mock(spec=OnePasswordClient)
        client.is_available.return_value = True
        client.is_authenticated.return_value = True
        client.store_secret.return_value = "mock-item-id"
        client.get_secret.return_value = "mock-secret-value"
        mock.return_value = client
        yield client


@pytest.fixture
def env_importer(mock_op_client):
    """Create an EnvImporter instance for testing."""
    importer = EnvImporter(vault="test-vault")
    return importer
