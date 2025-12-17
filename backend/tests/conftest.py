import pytest
import os

@pytest.fixture(scope="session")
def mock_api_key():
    """Provide mock API key for testing"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key-123"
    yield
    del os.environ["ANTHROPIC_API_KEY"]