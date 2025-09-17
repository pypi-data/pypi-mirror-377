from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.agent.types import A2AClientConfig as A2AClientConfig

async def main(query: str):
    """Main function demonstrating the Multi-Agent Coordinator streaming client.

    Args:
        query: The query to send to the coordinator agent.
    """
