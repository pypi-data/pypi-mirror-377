from typing import Any, Dict, Optional

import httpx
from pydantic import ValidationError

from .models import ProcessTextRequest, ProcessTextResponse, ResponseMetadata


class VpsBrainClientError(Exception):
    """Custom exception for VPS Brain client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class VpsBrainClient:
    """A Python client for the VPS Brain API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.timeout = timeout
        self._client = httpx.AsyncClient(headers=self.headers, timeout=self.timeout)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            try:
                response_data = e.response.json()
            except Exception:
                response_data = {"detail": e.response.text}
            raise VpsBrainClientError(
                f"API request failed with status {status_code}: {response_data.get('detail', 'Unknown error')}",
                status_code=status_code,
                response_data=response_data,
            ) from e
        except httpx.RequestError as e:
            raise VpsBrainClientError(f"An error occurred while requesting {e.request.url!r}: {e}") from e
        except ValidationError as e:
            raise VpsBrainClientError(f"Failed to validate API response: {e}") from e

    async def get_root(self) -> Dict[str, str]:
        """Get the root endpoint message."""
        return await self._request("GET", "/")

    async def get_healthz(self) -> Dict[str, str]:
        """Get the health status of the API."""
        return await self._request("GET", "/healthz")

    async def get_readyz(self) -> Dict[str, str]:
        """Get the readiness status of the API (checks Ollama connectivity)."""
        return await self._request("GET", "/readyz")

    async def process_text(self, payload: ProcessTextRequest) -> ProcessTextResponse:
        """Process text through the configured Ollama model."""
        response_data = await self._request("POST", "/process_text", json=payload.model_dump())
        return ProcessTextResponse.model_validate(response_data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._client.aclose()
