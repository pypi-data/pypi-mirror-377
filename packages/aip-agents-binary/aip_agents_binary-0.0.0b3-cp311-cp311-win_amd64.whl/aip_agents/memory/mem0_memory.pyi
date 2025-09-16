from _typeshed import Incomplete
from aip_agents.memory.base import BaseMemory as BaseMemory, ChatMessage as ChatMessage
from aip_agents.memory.constants import MemoryDefaults as MemoryDefaults
from aip_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete

class Mem0Memory(BaseMemory):
    '''Mem0-backed memory.

    Recommended usage pattern per mem0 docs:
    - Retrieve: search(query, user_id, limit=K) → use results["results"] list
    - Add: add(messages=[{"role": ...}], user_id=user_id) → mem0 distills and stores
    '''
    namespace: Incomplete
    limit: Incomplete
    max_chars: Incomplete
    def __init__(self, *, namespace: str | None = None, limit: int = ..., max_chars: int = ...) -> None:
        """Initialize the Mem0Memory adapter.

        Args:
            namespace: Optional namespace for the memory store.
            limit: Maximum number of memories to retrieve per search.
            max_chars: Maximum characters per memory entry when saving.
        """
    def get_messages(self) -> list[ChatMessage]:
        """Get all stored messages.

        Note:
            Not used by LangGraph path; present for compatibility with other parts
            of the framework.

        Returns:
            list[ChatMessage]: An empty list (not implemented).
        """
    def add_message(self, message: ChatMessage) -> None:
        """Add a single message to memory.

        Provides compatibility with the BaseMemory interface by converting a
        ChatMessage to the format expected by the mem0 client and saving it.

        Args:
            message: The ChatMessage object containing role and content information
                to be stored in memory.
        """
    def clear(self) -> None:
        """Clear all memories.

        Not implemented in this adapter. A real implementation would need to
        call mem0's delete API with user_id/namespace parameters.

        Raises:
            NotImplementedError: Always, as this method is not implemented.
        """
    def search(self, query: str, *, user_id: str, limit: int | None = None) -> list[dict[str, Any]]:
        '''Search for relevant memories.

        Args:
            query: The user query used to retrieve relevant memories.
            user_id: The mem0 user identifier (scopes memory per agent/user).
            limit: Optional number of results to retrieve; defaults to adapter limit.

        Returns:
            list[dict[str, Any]]: A list of hit dictionaries (prefers a `{"results": [...]}` payload).
        '''
    def save_interaction(self, *, user_text: str, ai_text: str, user_id: str) -> None:
        """Persist a single user/assistant turn.

        Truncates strings by ``max_chars`` and lets mem0 distill key facts from
        the conversation turn for storage.

        Args:
            user_text: The user input text.
            ai_text: The assistant output text.
            user_id: The mem0 user identifier (scopes memory per agent/user).
        """
    def format_hits(self, hits: list[dict[str, Any]], max_items: int = ...) -> str:
        """Render hits into a compact prefix block for prompts.

        Args:
            hits: A list of search results from mem0.
            max_items: The maximum number of memories to include in the prefix.

        Returns:
            str: A compact memory block to be prepended to the user query.
        """
    @classmethod
    def validate_env(cls) -> None:
        """Validate presence of mem0 API key (hosted setups).

        Raises:
            ValueError: If MEM0_API_KEY is not set in the environment.
        """
