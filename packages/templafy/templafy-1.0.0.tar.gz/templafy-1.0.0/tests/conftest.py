from pathlib import Path

import pytest

from templafy import AuthenticatedClient, Client

collect_ignore_glob = ["assets/**"]
pytest_plugins = []


@pytest.fixture(scope="session")
def assets_dir() -> Path:
    """Return a path to the test assets directory."""
    return Path(__file__).parent / "assets"


@pytest.fixture
def base_url():
    """Base URL for testing."""
    return "https://test.api.templafy.com/v3"


@pytest.fixture
def api_token():
    """Mock API token for testing."""
    return "test_token_12345"


@pytest.fixture
def mock_client(base_url):
    """Mock unauthenticated client for testing."""
    return Client(base_url=base_url)


@pytest.fixture
def mock_authenticated_client(base_url, api_token):
    """Mock authenticated client for testing."""
    return AuthenticatedClient(base_url=base_url, token=api_token)


@pytest.fixture
def mock_space_data():
    """Mock space data for testing."""
    return [
        {
            "id": "space1",
            "name": "Test Space 1",
            "description": "A test space",
            "is_active": True,
        },
        {
            "id": "space2",
            "name": "Test Space 2",
            "description": "Another test space",
            "is_active": True,
        },
    ]


@pytest.fixture
def mock_document_data():
    """Mock document data for testing."""
    return [
        {
            "id": "doc1",
            "name": "Test Document 1",
            "description": "A test document",
            "template_type": "word",
            "library_id": "lib1",
        },
        {
            "id": "doc2",
            "name": "Test Document 2",
            "description": "Another test document",
            "template_type": "powerpoint",
            "library_id": "lib1",
        },
    ]


@pytest.fixture
def mock_library_data():
    """Mock library data for testing."""
    return [
        {
            "id": "lib1",
            "name": "Test Library 1",
            "description": "A test library",
            "space_id": "space1",
            "is_active": True,
        },
    ]
