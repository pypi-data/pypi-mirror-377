"""Pytest fixtures for agent_server_client tests."""

from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from sema4ai_docint.agent_server_client.client import AgentServerClient
from sema4ai_docint.agent_server_client.transport.base import (
    ResponseMessage,
    TransportBase,
    TransportResponseWrapper,
)
from tests.agent_server_client.fast_api_dummy_server import FastAPIAgentDummyServer


class MockTransport(TransportBase):
    """A mock transport implementation for testing that implements all abstract methods.

    This mock can be used to test the AgentServerClient without testing the transport.

    You can set a prompts_generate_return_value which will be returned
    by the prompts_generate method.

    Example:

        mock_response = ResponseMessage(
            content=[{"text": json.dumps({"key": "value"}), "kind": "text"}]
        )
        mock_transport.prompts_generate_return_value = mock_response
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompts_generate_return_value = MagicMock(spec=ResponseMessage)
        self._is_connected = True

    def connect(self) -> None:
        """Mock connect implementation."""
        self._is_connected = True

    def is_connected(self) -> bool:
        """Mock is_connected implementation."""
        return self._is_connected

    def close(self) -> None:
        """Mock close implementation."""
        self._is_connected = False

    def request(
        self,
        method: str,
        path: str,
        *,
        content: bytes | str | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> TransportResponseWrapper:
        """Mock request implementation."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": [{"text": "{}", "kind": "text"}]}
        return TransportResponseWrapper(mock_response)

    def get_file(self, name: str) -> Path:
        """Mock get_file implementation."""
        return Path(f"/mock/path/{name}")

    def prompts_generate(self, payload: dict[str, Any]) -> ResponseMessage:
        """Mock prompts_generate implementation that can be configured by tests."""
        return self.prompts_generate_return_value


@pytest.fixture
def mock_transport() -> MockTransport:
    """Fixture providing a MockTransport instance."""
    return MockTransport(agent_id="test_agent")


@pytest.fixture
def agent_server_client(mock_transport: MockTransport) -> AgentServerClient:
    """Fixture providing an AgentServerClient with MockTransport."""
    return AgentServerClient(transport=mock_transport)


@pytest.fixture
def mock_response_message() -> Callable[[str, str], ResponseMessage]:
    """Factory fixture for creating ResponseMessage instances."""

    def _create_response(content_text: str, content_kind: str = "text"):
        return ResponseMessage(content=[{"text": content_text, "kind": content_kind}])

    return _create_response


@pytest.fixture
def fastapi_agent_dummy_server(request):
    """Start FastAPIAgentDummyServer for testing with configurable responses.

    You can set this fixture up via indirect parametrization or by modifying the
    responses and file_responses parameters before calling an endpoint that uses them.


    Example usage:
        # For prompt responses only:
        @pytest.mark.parametrize(
            "fastapi_agent_dummy_server",
            [["Response 1", "Response 2", json.dumps({"custom": "response"})]],
            indirect=True
        )
        def test_something(fastapi_agent_dummy_server):
            # Server will return responses in order
            pass

        # For both prompt and file responses:
        @pytest.mark.parametrize(
            "fastapi_agent_dummy_server",
            [(
                ["Prompt response"],  # responses
                {"test_file.txt": {"content": "Custom file content", "mime_type": "text/plain"}}
                # file_responses
            )],
            indirect=True
        )
        def test_with_files(fastapi_agent_dummy_server):
            # Server will return custom file responses
            pass
    """
    import os

    # Get responses and file_responses from test parameter if provided
    param = getattr(request, "param", None)

    # Handle different parameter formats
    if param is None:
        responses = None
        file_responses = None
    elif isinstance(param, list | tuple) and len(param) == 2:
        # Tuple format: (responses, file_responses)
        responses, file_responses = param
    else:
        # Legacy format: just responses
        responses = param
        file_responses = None

    # Start the dummy server
    server = FastAPIAgentDummyServer(responses, file_responses)
    server.start()

    # Set environment variables to point to the dummy server
    original_agents_url = os.environ.get("SEMA4AI_AGENTS_SERVICE_URL")
    original_file_url = os.environ.get("SEMA4AI_FILE_MANAGEMENT_URL")

    os.environ["SEMA4AI_AGENTS_SERVICE_URL"] = f"http://localhost:{server.get_port()}"

    # Set up file management URL for test data
    test_data_dir = Path(__file__).parent / "assets"
    os.environ["SEMA4AI_FILE_MANAGEMENT_URL"] = f"file://{test_data_dir.absolute()}"

    try:
        yield server
    finally:
        # Cleanup
        server.stop()

        # Restore original environment variables
        if original_agents_url is not None:
            os.environ["SEMA4AI_AGENTS_SERVICE_URL"] = original_agents_url
        else:
            os.environ.pop("SEMA4AI_AGENTS_SERVICE_URL", None)

        if original_file_url is not None:
            os.environ["SEMA4AI_FILE_MANAGEMENT_URL"] = original_file_url
        else:
            os.environ.pop("SEMA4AI_FILE_MANAGEMENT_URL", None)
