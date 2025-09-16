from _typeshed import Incomplete
from aip_agents.agent import LangGraphAgent as LangGraphAgent
from aip_agents.examples.tools.image_artifact_tool import ImageArtifactTool as ImageArtifactTool
from aip_agents.examples.tools.table_generator_tool import TableGeneratorTool as TableGeneratorTool
from aip_agents.examples.tools.time_tool import TimeTool as TimeTool
from aip_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the Multi-Agent Coordinator A2A server."""
