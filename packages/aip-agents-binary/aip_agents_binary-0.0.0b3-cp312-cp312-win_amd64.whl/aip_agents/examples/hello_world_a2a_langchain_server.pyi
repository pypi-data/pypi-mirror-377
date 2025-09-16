from _typeshed import Incomplete
from aip_agents.agent import LangChainAgent as LangChainAgent
from aip_agents.examples.tools.langchain_weather_tool import weather_tool as weather_tool
from aip_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the LangChain Weather A2A server."""
