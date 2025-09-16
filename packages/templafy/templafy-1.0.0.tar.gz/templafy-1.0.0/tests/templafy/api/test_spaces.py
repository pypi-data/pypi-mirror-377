"""Tests for the spaces API."""

from unittest.mock import Mock, patch

from templafy.api.spaces import get_spaces
from templafy.models.space import Space


def test_get_spaces_success(mock_authenticated_client, mock_space_data):
    """Test successful spaces listing returns space list."""
    with patch.object(mock_authenticated_client._client, "get") as mock_get:  # noqa: SLF001
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_space_data
        mock_get.return_value = mock_response

        result = get_spaces(client=mock_authenticated_client)

        assert len(result) == len(mock_space_data)


def test_get_spaces_returns_space_objects(mock_authenticated_client, mock_space_data):
    """Test that get_spaces returns Space objects."""
    with patch.object(mock_authenticated_client._client, "get") as mock_get:  # noqa: SLF001
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_space_data
        mock_get.return_value = mock_response

        result = get_spaces(client=mock_authenticated_client)

        assert all(isinstance(space, Space) for space in result)
