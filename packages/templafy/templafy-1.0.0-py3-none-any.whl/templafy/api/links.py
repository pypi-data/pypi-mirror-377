"""Links API endpoints for the Templafy API."""

from templafy.client import AuthenticatedClient, Client
from templafy.errors import get_error_from_response
from templafy.models.link import Link


def get_links(
    *,
    client: Client | AuthenticatedClient,
) -> list[Link]:
    """List links.

    Args:
        client: The API client to use

    Returns:
        List of links

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/links"

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return [Link(**item) for item in data]
    else:
        error = get_error_from_response(response)
        raise error
