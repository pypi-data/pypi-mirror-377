from _typeshed import Incomplete
from gllm_agents.agent.langflow_agent import LangflowAgent as LangflowAgent
from gllm_agents.agent.types import A2AClientConfig as A2AClientConfig
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete

async def main() -> None:
    """Main function demonstrating the Langflow client with streaming A2A capabilities."""
