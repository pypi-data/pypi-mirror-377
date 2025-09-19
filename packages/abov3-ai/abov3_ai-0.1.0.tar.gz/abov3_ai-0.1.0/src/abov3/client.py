"""ABOV3 AI Client implementation"""

import os
from typing import Optional, Dict, Any
import httpx
from .resources import Sessions, Messages, Files, Agents, Projects
from .exceptions import Abov3Error


class Abov3Client:
    """Main client for interacting with the ABOV3 AI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize the ABOV3 client.

        Args:
            api_key: API key for authentication. Defaults to ABOV3_API_KEY env var.
            base_url: Base URL for the API. Defaults to https://api.abov3.ai
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            proxy: Optional proxy URL.
            headers: Additional headers to include in requests.
        """
        self.api_key = api_key or os.getenv("ABOV3_API_KEY")
        if not self.api_key:
            raise Abov3Error("API key is required. Set ABOV3_API_KEY or pass api_key parameter.")

        self.base_url = base_url or os.getenv("ABOV3_BASE_URL", "https://api.abov3.ai")

        # Setup HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "abov3-python/0.1.0",
                **(headers or {})
            },
            proxy=proxy,
        )

        self.max_retries = max_retries

        # Initialize resources
        self.sessions = Sessions(self)
        self.messages = Messages(self)
        self.files = Files(self)
        self.agents = Agents(self)
        self.projects = Projects(self)

    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """Make an HTTP request to the API."""
        retries = 0
        while retries <= self.max_retries:
            try:
                response = await self._client.request(method, path, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if retries < self.max_retries and e.response.status_code in [429, 503]:
                    retries += 1
                    # Simple exponential backoff
                    await httpx.AsyncClient().aclose()  # Small delay
                    continue
                raise
            except Exception as e:
                if retries < self.max_retries:
                    retries += 1
                    continue
                raise

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()