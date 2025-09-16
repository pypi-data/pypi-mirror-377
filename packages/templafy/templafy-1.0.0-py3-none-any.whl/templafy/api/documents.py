"""Documents API endpoints for the Templafy API."""

from templafy.client import AuthenticatedClient, Client
from templafy.errors import get_error_from_response
from templafy.models.document import Document


def get_documents(
    *,
    client: Client | AuthenticatedClient,
    library_id: str | None = None,
    folder_id: str | None = None,
) -> list[Document]:
    """List documents.

    Args:
        client: The API client to use
        library_id: Optional library ID to filter by
        folder_id: Optional folder ID to filter by

    Returns:
        List of documents

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/documents"

    params = {}
    if library_id:
        params["libraryId"] = library_id
    if folder_id:
        params["folderId"] = folder_id

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers, params=params)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return [Document(**item) for item in data]
    else:
        error = get_error_from_response(response)
        raise error


def get_document(
    *,
    client: Client | AuthenticatedClient,
    document_id: str,
) -> Document:
    """Get a specific document.

    Args:
        client: The API client to use
        document_id: The ID of the document

    Returns:
        The document

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/documents/{document_id}"

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return Document(**data)
    else:
        error = get_error_from_response(response)
        raise error
