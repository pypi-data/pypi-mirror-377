import pytest
import httpx
from httpx import Response, Request

from vps_brain_client.client import VpsBrainClient, VpsBrainClientError
from vps_brain_client.models import ProcessTextRequest, ProcessTextResponse, ResponseMetadata

BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key"


@pytest.fixture
def client():
    return VpsBrainClient(base_url=BASE_URL, api_key=API_KEY)


@pytest.mark.asyncio
async def test_get_root(httpx_mock, client: VpsBrainClient):
    httpx_mock.add_response(url=f"{BASE_URL}/", json={
        "message": "VPS Brain API is running. Use /process_text to interact with the LLM.",
        "default_model": "phi3:mini",
    })
    response = await client.get_root()
    assert response["message"] == "VPS Brain API is running. Use /process_text to interact with the LLM."
    assert response["default_model"] == "phi3:mini"


@pytest.mark.asyncio
async def test_get_healthz(httpx_mock, client: VpsBrainClient):
    httpx_mock.add_response(url=f"{BASE_URL}/healthz", json={
        "status": "ok"
    })
    response = await client.get_healthz()
    assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_get_readyz(httpx_mock, client: VpsBrainClient):
    httpx_mock.add_response(url=f"{BASE_URL}/readyz", json={
        "status": "ready"
    })
    response = await client.get_readyz()
    assert response["status"] == "ready"


@pytest.mark.asyncio
async def test_process_text_success(httpx_mock, client: VpsBrainClient):
    request_payload = ProcessTextRequest(text="Hello, world!")
    mock_response_data = {
        "status": "success",
        "model": "phi3:mini",
        "task": "default",
        "input_text": "Hello, world!",
        "rendered_prompt": "Hello, world!",
        "llm_response": "Hi there! How can I help you today?",
        "meta": {
            "request_id": "123",
            "received_at": "2025-01-01T00:00:00Z",
            "request_duration_ms": 100.0,
            "inference_duration_ms": 50.0,
            "prompt_chars": 13,
            "response_chars": 35,
        },
    }
    httpx_mock.add_response(url=f"{BASE_URL}/process_text", json=mock_response_data)

    response = await client.process_text(request_payload)

    assert isinstance(response, ProcessTextResponse)
    assert response.status == "success"
    assert response.llm_response == "Hi there! How can I help you today?"
    assert response.meta.request_id == "123"


@pytest.mark.asyncio
async def test_process_text_api_error(httpx_mock, client: VpsBrainClient):
    request_payload = ProcessTextRequest(text="Too long text...")
    httpx_mock.add_response(
        url=f"{BASE_URL}/process_text",
        status_code=422,
        json={
            "detail": "Text too long",
            "body": {"text": ["ensure this value has at most 8192 characters"]}
        },
    )

    with pytest.raises(VpsBrainClientError) as exc_info:
        await client.process_text(request_payload)

    assert exc_info.value.status_code == 422
    assert "Text too long" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_text_network_error(httpx_mock, client: VpsBrainClient):
    request_payload = ProcessTextRequest(text="Hello, world!")
    httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

    with pytest.raises(VpsBrainClientError) as exc_info:
        await client.process_text(request_payload)

    assert "Connection refused" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_context_manager(httpx_mock):
    httpx_mock.add_response(url=f"{BASE_URL}/healthz", json={
        "status": "ok"
    })

    async with VpsBrainClient(base_url=BASE_URL, api_key=API_KEY) as client:
        response = await client.get_healthz()
        assert response["status"] == "ok"

    # Verify that the client was closed (e.g., no open connections)
    # This is hard to test directly without internal access to httpx, but we assume aclose is called.
