"""Tests for the documents API."""

from unittest.mock import Mock, patch

from templafy.api.documents import get_document, get_documents
from templafy.models.document import Document


def test_get_documents_success(mock_authenticated_client, mock_document_data):
    """Test successful documents listing returns document list."""
    with patch.object(mock_authenticated_client._client, "get") as mock_get:  # noqa: SLF001
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_document_data
        mock_get.return_value = mock_response

        result = get_documents(client=mock_authenticated_client)

        assert len(result) == len(mock_document_data)


def test_get_document_success(mock_authenticated_client, mock_document_data):
    """Test successful single document retrieval."""
    with patch.object(mock_authenticated_client._client, "get") as mock_get:  # noqa: SLF001
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_document_data[0]
        mock_get.return_value = mock_response

        result = get_document(client=mock_authenticated_client, document_id="doc1")

        assert isinstance(result, Document)
