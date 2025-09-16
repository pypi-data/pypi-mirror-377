from _typeshed import Incomplete
from aip_agents.agent import LangGraphReactAgent as LangGraphReactAgent
from aip_agents.examples.tools.data_generator_tool import DataGeneratorTool as DataGeneratorTool
from aip_agents.examples.tools.data_visualization_tool import DataVisualizerTool as DataVisualizerTool
from aip_agents.storage.clients.minio_client import MinioConfig as MinioConfig, MinioObjectStorage as MinioObjectStorage
from aip_agents.storage.providers.object_storage import ObjectStorageProvider as ObjectStorageProvider
from aip_agents.utils.langgraph.tool_output_management import ToolOutputConfig as ToolOutputConfig, ToolOutputManager as ToolOutputManager
from aip_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Run the Data Visualization A2A server."""
