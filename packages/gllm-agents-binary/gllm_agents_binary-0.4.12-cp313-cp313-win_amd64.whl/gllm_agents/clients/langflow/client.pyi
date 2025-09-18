from _typeshed import Incomplete
from gllm_agents.agent.types import HttpxClientOptions as HttpxClientOptions, LangflowAgentConfig as LangflowAgentConfig
from gllm_agents.clients.langflow.types import LangflowEventType as LangflowEventType
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any, AsyncGenerator

logger: Incomplete
DEFAULT_LANGFLOW_BASE_URL: Incomplete

class LangflowApiClient:
    """HTTP client for Langflow API with streaming and non-streaming support.

    This client handles all communication with Langflow APIs, including:
    - Non-streaming execution
    - Server-Sent Events (SSE) streaming
    - Session management for conversation continuity
    - Error handling and retries
    - Credential management
    """
    config: Incomplete
    flow_id: Incomplete
    base_url: Incomplete
    api_key: Incomplete
    sessions: dict[str, str]
    client_kwargs: Incomplete
    def __init__(self, config: LangflowAgentConfig) -> None:
        """Initialize the Langflow API client.

        Args:
            config: LangflowAgentConfig containing flow ID, API settings, and credentials.
        """
    def get_or_create_session(self, thread_id: str | None = None) -> str:
        """Get existing session ID or create a new one.

        Args:
            thread_id: Optional thread ID for session mapping.

        Returns:
            Session ID for the conversation.
        """
    async def call_flow(self, input_value: str, session_id: str | None = None, **_: Any) -> dict[str, Any]:
        """Execute Langflow flow without streaming.

        Args:
            input_value: The user input to send to the flow.
            session_id: Optional session ID for conversation continuity.
            **_: Additional keyword arguments.

        Returns:
            The response from the flow execution.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
            ValueError: If the response cannot be parsed.
        """
    async def stream_flow(self, input_value: str, session_id: str | None = None, **_: Any) -> AsyncGenerator[dict[str, Any], None]:
        """Execute Langflow flow with streaming.

        Args:
            input_value: The user input to send to the flow.
            session_id: Optional session ID for conversation continuity.
            **_: Additional keyword arguments.

        Yields:
            Parsed streaming events from the Langflow API.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
            ValueError: If streaming events cannot be parsed.
        """
    def parse_stream_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse a single streaming event from Langflow.

        Args:
            event_data: Raw event data from Langflow streaming response.

        Returns:
            Parsed event dictionary or None if event should be skipped.
        """
    def clear_session(self, thread_id: str) -> None:
        """Clear session for a specific thread.

        Args:
            thread_id: Thread ID to clear session for.
        """
    def clear_all_sessions(self) -> None:
        """Clear all stored sessions."""
    async def health_check(self) -> bool:
        """Check if the Langflow API is accessible.

        Returns:
            True if the API is accessible, False otherwise.
        """
