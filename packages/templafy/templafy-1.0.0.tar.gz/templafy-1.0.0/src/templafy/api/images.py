"""Images API endpoints for the Templafy API."""

from templafy.client import AuthenticatedClient, Client
from templafy.errors import get_error_from_response
from templafy.models.image import Image


def get_images(
    *,
    client: Client | AuthenticatedClient,
) -> list[Image]:
    """List images.

    Args:
        client: The API client to use

    Returns:
        List of images

    Raises:
        TemplafyError: If the API request fails
    """
    url = f"{client.base_url}/images"

    headers = {}
    if isinstance(client, AuthenticatedClient):
        headers = client.get_headers()

    response = client._client.get(url, headers=headers)  # noqa: SLF001

    if response.status_code == 200:
        data = response.json()
        return [Image(**item) for item in data]
    else:
        error = get_error_from_response(response)
        raise error
