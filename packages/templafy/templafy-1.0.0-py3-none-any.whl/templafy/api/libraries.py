"""Libraries API endpoints for the Templafy API."""

from templafy.client import AuthenticatedClient, Client
from templafy.errors import get_error_from_response
from templafy.models.library import Library


def get_libraries(
    *,
    client: Client | AuthenticatedClient,
) -> list[Library]:
    """List libraries.

    Args:
        client: The API client to use

    Returns:
        List of libraries

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/libraries"

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return [Library(**item) for item in data]
    else:
        error = get_error_from_response(response)
        raise error
