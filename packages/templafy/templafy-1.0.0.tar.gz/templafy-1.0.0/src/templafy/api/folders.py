"""Folders API endpoints for the Templafy API."""

from templafy.client import AuthenticatedClient, Client
from templafy.errors import get_error_from_response
from templafy.models.folder import Folder


def get_folders(
    *,
    client: Client | AuthenticatedClient,
) -> list[Folder]:
    """List folders.

    Args:
        client: The API client to use

    Returns:
        List of folders

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/folders"

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return [Folder(**item) for item in data]
    else:
        error = get_error_from_response(response)
        raise error
