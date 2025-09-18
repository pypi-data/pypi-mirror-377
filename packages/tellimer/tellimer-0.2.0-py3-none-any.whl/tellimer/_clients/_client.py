import httpx

from tellimer import __version__
from tellimer._clients._data import DataClient
from tellimer.errors import (
    AuthError,
    BadGatewayError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    InternalServerError,
    MethodNotAllowedError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
)


class Client:
    """
    A client for the Tellimer API. This client is used to interact with the Tellimer API.

    Args:
        api_key: The API key to use for the client.
        timeout: The timeout to use for the client. Defaults to httpx's default timeout.
    """

    def __init__(self, api_key: str, timeout: float = 30):
        """
        Initialize the client.

        Args:
            api_key: The API key to use for the client.
            timeout: The timeout to use for the client. Defaults to httpx's default timeout.
        """
        self.api_key = api_key
        # self._base_url = "http://localhost:8000"
        self._base_url = "https://sdk.tellimer.com/"
        self._timeout = timeout

        self.data = DataClient(self._make_request)
        # self.articles = ArticlesClient(self._make_request)
        # self.news = NewsClient(self._make_request)

    def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """
        Internal method that creates a fresh httpx client for each request
        and properly closes it after the request is complete.
        """
        with httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"tellimer-sdk/{__version__}",
            },
            timeout=self._timeout,
        ) as client:
            try:
                resp = getattr(client, method)(url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_message = e.response.text
                if status_code == 400:
                    raise BadRequestError("Bad request") from e
                elif status_code == 401:
                    raise AuthError("Invalid API key") from e
                elif status_code == 403:
                    raise ForbiddenError("Forbidden") from e
                elif status_code == 404:
                    raise NotFoundError("Resource not found") from e
                elif status_code == 405:
                    raise MethodNotAllowedError("Method not allowed") from e
                elif status_code == 429:
                    raise RateLimitError("Rate limit exceeded") from e
                elif status_code == 500:
                    raise InternalServerError("Internal server error") from e
                elif status_code == 502:
                    raise BadGatewayError("Bad gateway") from e
                elif status_code == 503:
                    raise ServiceUnavailableError("Service unavailable") from e
                elif status_code == 504:
                    raise GatewayTimeoutError("Gateway timeout") from e
                else:
                    raise httpx.HTTPStatusError(
                        f"HTTP {status_code}: {error_message}",
                        request=None,
                        response=None,
                    )
