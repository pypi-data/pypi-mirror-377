"""Tests for the Templafy API client."""

from templafy import AuthenticatedClient, Client


def test_client_initialization(base_url):
    """Test client initialization with base URL."""
    client = Client(base_url=base_url)
    assert client.base_url == base_url


def test_authenticated_client_initialization(base_url, api_token):
    """Test authenticated client initialization."""
    client = AuthenticatedClient(base_url=base_url, token=api_token)
    assert client.base_url == base_url
    assert client.token == api_token


def test_authenticated_client_headers(mock_authenticated_client, api_token):
    """Test authenticated client generates correct headers."""
    headers = mock_authenticated_client.get_headers()
    assert headers["Authorization"] == f"Bearer {api_token}"
    assert headers["Content-Type"] == "application/json"
