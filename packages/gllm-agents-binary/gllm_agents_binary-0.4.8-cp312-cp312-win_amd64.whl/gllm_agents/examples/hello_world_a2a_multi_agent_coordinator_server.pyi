from _typeshed import Incomplete
from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.examples.tools.image_artifact_tool import ImageArtifactTool as ImageArtifactTool
from gllm_agents.examples.tools.table_generator_tool import TableGeneratorTool as TableGeneratorTool
from gllm_agents.examples.tools.time_tool import TimeTool as TimeTool
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the Multi-Agent Coordinator A2A server."""
