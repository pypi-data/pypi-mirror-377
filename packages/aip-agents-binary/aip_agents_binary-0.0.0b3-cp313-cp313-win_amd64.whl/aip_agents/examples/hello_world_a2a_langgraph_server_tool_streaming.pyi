from _typeshed import Incomplete
from aip_agents.agent import LangChainAgent as LangChainAgent
from aip_agents.examples.tools.langgraph_streaming_tool import LangGraphStreamingTool as LangGraphStreamingTool
from aip_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the LangGraph Agent Wrapper A2A server."""
