"""Base client classes for the Templafy API."""

import httpx


class Client:
    """A client for the Templafy API."""

    def __init__(
        self,
        base_url: str,
        *,
        httpx_client: httpx.Client | None = None,
        timeout: float = 10.0,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the client.

        Args:
            base_url: The base URL for the API
            httpx_client: An optional httpx client to use
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._client = httpx_client or httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
        )

    def __enter__(self) -> "Client":
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self._client.close()

    def close(self) -> None:
        """Close the client."""
        self._client.close()


class AuthenticatedClient(Client):
    """An authenticated client for the Templafy API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        httpx_client: httpx.Client | None = None,
        timeout: float = 10.0,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the authenticated client.

        Args:
            base_url: The base URL for the API
            token: The API token for authentication
            httpx_client: An optional httpx client to use
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        super().__init__(
            base_url=base_url,
            httpx_client=httpx_client,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.token = token
        if httpx_client is None:
            self._client = httpx.Client(
                timeout=timeout,
                verify=verify_ssl,
                headers={"Authorization": f"Bearer {token}"},
            )

    def get_headers(self) -> dict[str, str]:
        """Get the headers for authenticated requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
