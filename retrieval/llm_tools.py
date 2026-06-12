"""
LLM API Tools for ChatIndex Retrieval

This module provides tools that LLMs can use to interact with a ChatIndex/CTree
for intelligent conversation retrieval.
"""

import json
import os
from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Optional
from anthropic import Anthropic
from openai import OpenAI
from ctree import CTree, TopicNode, MessageNode
from retrieval.vector_index import VectorIndex


DEFAULT_RETRIEVAL_PROVIDER = "anthropic"
DEFAULT_RETRIEVAL_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o-mini",
}
PROVIDER_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}


@dataclass
class LLMProviderConfig:
    """Configuration for the LLM used by retrieval."""

    provider: str = DEFAULT_RETRIEVAL_PROVIDER
    model: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 8192


@dataclass
class TextBlock:
    """Provider-neutral text content block."""

    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    """Provider-neutral tool-use content block."""

    id: str
    name: str
    input: Dict[str, Any]
    type: str = "tool_use"


@dataclass
class RetrievalResponse:
    """Provider-neutral response used by the retrieval loop."""

    stop_reason: str
    content: List[Any]
    raw_response: Any = None


def _block_type(block: Any) -> Optional[str]:
    if isinstance(block, dict):
        return block.get("type")
    return getattr(block, "type", None)


def _block_value(block: Any, key: str, default: Any = None) -> Any:
    if isinstance(block, dict):
        return block.get(key, default)
    return getattr(block, key, default)


def _normalize_provider(provider: Optional[str]) -> str:
    normalized = (provider or DEFAULT_RETRIEVAL_PROVIDER).strip().lower()
    aliases = {
        "claude": "anthropic",
        "anthropic": "anthropic",
        "chatgpt": "openai",
        "openai": "openai",
    }
    if normalized not in aliases:
        supported = ", ".join(sorted(DEFAULT_RETRIEVAL_MODELS))
        raise ValueError(f"Unsupported retrieval provider '{provider}'. Supported providers: {supported}")
    return aliases[normalized]


def _resolve_provider_config(
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    config: Optional[LLMProviderConfig] = None,
) -> LLMProviderConfig:
    if config is None:
        resolved = LLMProviderConfig(
            provider=provider or DEFAULT_RETRIEVAL_PROVIDER,
            model=model,
            api_key=api_key,
            max_tokens=max_tokens or LLMProviderConfig.max_tokens,
        )
    else:
        resolved = LLMProviderConfig(
            provider=provider or config.provider,
            model=model or config.model,
            api_key=api_key or config.api_key,
            max_tokens=max_tokens or config.max_tokens,
        )

    resolved.provider = _normalize_provider(resolved.provider)
    if not resolved.model:
        resolved.model = DEFAULT_RETRIEVAL_MODELS[resolved.provider]

    if not resolved.api_key:
        resolved.api_key = os.getenv(PROVIDER_ENV_VARS[resolved.provider])

    if not resolved.api_key:
        env_var = PROVIDER_ENV_VARS[resolved.provider]
        raise ValueError(
            f"API key required for retrieval provider '{resolved.provider}'. "
            f"Pass api_key=... or set {env_var}."
        )

    return resolved


def _anthropic_content(content: Any) -> Any:
    if isinstance(content, str):
        return content

    converted = []
    for block in content:
        block_type = _block_type(block)
        if block_type == "text":
            converted.append({"type": "text", "text": _block_value(block, "text", "")})
        elif block_type == "tool_use":
            converted.append({
                "type": "tool_use",
                "id": _block_value(block, "id"),
                "name": _block_value(block, "name"),
                "input": _block_value(block, "input", {}),
            })
        elif block_type == "tool_result":
            converted.append(block)
    return converted


def _anthropic_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {"role": message["role"], "content": _anthropic_content(message["content"])}
        for message in messages
    ]


def _normalize_anthropic_response(response: Any) -> RetrievalResponse:
    content = []
    for block in response.content:
        block_type = _block_type(block)
        if block_type == "text":
            content.append(TextBlock(text=_block_value(block, "text", "")))
        elif block_type == "tool_use":
            content.append(ToolUseBlock(
                id=_block_value(block, "id"),
                name=_block_value(block, "name"),
                input=_block_value(block, "input", {}),
            ))
    return RetrievalResponse(
        stop_reason=response.stop_reason,
        content=content,
        raw_response=response,
    )


def _openai_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        for tool in tools
    ]


def _openai_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted = []

    for message in messages:
        role = message["role"]
        content = message["content"]

        if isinstance(content, str):
            converted.append({"role": role, "content": content})
            continue

        if role == "assistant":
            text_parts = []
            tool_calls = []
            for block in content:
                block_type = _block_type(block)
                if block_type == "text":
                    text_parts.append(_block_value(block, "text", ""))
                elif block_type == "tool_use":
                    tool_calls.append({
                        "id": _block_value(block, "id"),
                        "type": "function",
                        "function": {
                            "name": _block_value(block, "name"),
                            "arguments": json.dumps(_block_value(block, "input", {})),
                        },
                    })

            openai_message = {
                "role": "assistant",
                "content": "".join(text_parts) if text_parts else None,
            }
            if tool_calls:
                openai_message["tool_calls"] = tool_calls
            converted.append(openai_message)
            continue

        for block in content:
            if _block_type(block) == "tool_result":
                converted.append({
                    "role": "tool",
                    "tool_call_id": _block_value(block, "tool_use_id"),
                    "content": _block_value(block, "content", ""),
                })

    return converted


def _parse_tool_arguments(arguments: Optional[str]) -> Dict[str, Any]:
    if not arguments:
        return {}
    try:
        parsed = json.loads(arguments)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_openai_response(response: Any) -> RetrievalResponse:
    message = response.choices[0].message
    content = []

    if getattr(message, "content", None):
        content.append(TextBlock(text=message.content))

    tool_calls = getattr(message, "tool_calls", None) or []
    for tool_call in tool_calls:
        content.append(ToolUseBlock(
            id=tool_call.id,
            name=tool_call.function.name,
            input=_parse_tool_arguments(tool_call.function.arguments),
        ))

    return RetrievalResponse(
        stop_reason="tool_use" if tool_calls else "end_turn",
        content=content,
        raw_response=response,
    )


class AnthropicRetrievalClient:
    """Retrieval client backed by Anthropic Messages."""

    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = Anthropic(api_key=config.api_key)

    def create_message(
        self,
        system: str,
        tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
    ) -> RetrievalResponse:
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=system,
            tools=tools,
            messages=_anthropic_messages(messages),
        )
        return _normalize_anthropic_response(response)

    def stream_message(
        self,
        system: str,
        tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        on_text_chunk: Optional[Callable[[str], None]] = None,
    ) -> RetrievalResponse:
        with self.client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=system,
            tools=tools,
            messages=_anthropic_messages(messages),
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                    if on_text_chunk:
                        on_text_chunk(event.delta.text)

            return _normalize_anthropic_response(stream.get_final_message())


class OpenAIRetrievalClient:
    """Retrieval client backed by OpenAI Chat Completions tool calls."""

    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key)

    def create_message(
        self,
        system: str,
        tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
    ) -> RetrievalResponse:
        openai_messages = [{"role": "system", "content": system}]
        openai_messages.extend(_openai_messages(messages))
        response = self.client.chat.completions.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            tools=_openai_tools(tools),
            tool_choice="auto",
            messages=openai_messages,
        )
        return _normalize_openai_response(response)

    def stream_message(
        self,
        system: str,
        tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        on_text_chunk: Optional[Callable[[str], None]] = None,
    ) -> RetrievalResponse:
        openai_messages = [{"role": "system", "content": system}]
        openai_messages.extend(_openai_messages(messages))
        stream = self.client.chat.completions.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            tools=_openai_tools(tools),
            tool_choice="auto",
            messages=openai_messages,
            stream=True,
        )

        text_parts = []
        tool_calls_by_index = {}
        raw_chunks = []

        for chunk in stream:
            raw_chunks.append(chunk)
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if getattr(delta, "content", None):
                text_parts.append(delta.content)
                if on_text_chunk:
                    on_text_chunk(delta.content)

            for tool_call in getattr(delta, "tool_calls", None) or []:
                index = tool_call.index
                current = tool_calls_by_index.setdefault(
                    index,
                    {"id": None, "name": None, "arguments": ""},
                )
                if getattr(tool_call, "id", None):
                    current["id"] = tool_call.id
                if getattr(tool_call, "function", None):
                    if getattr(tool_call.function, "name", None):
                        current["name"] = tool_call.function.name
                    if getattr(tool_call.function, "arguments", None):
                        current["arguments"] += tool_call.function.arguments

        content = []
        if text_parts:
            content.append(TextBlock(text="".join(text_parts)))
        for tool_call in [tool_calls_by_index[key] for key in sorted(tool_calls_by_index)]:
            content.append(ToolUseBlock(
                id=tool_call["id"],
                name=tool_call["name"],
                input=_parse_tool_arguments(tool_call["arguments"]),
            ))

        return RetrievalResponse(
            stop_reason="tool_use" if tool_calls_by_index else "end_turn",
            content=content,
            raw_response=raw_chunks,
        )


def build_retrieval_client(
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    config: Optional[LLMProviderConfig] = None,
):
    """Build a retrieval LLM client from provider configuration."""

    resolved = _resolve_provider_config(
        api_key=api_key,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        config=config,
    )

    if resolved.provider == "anthropic":
        return AnthropicRetrievalClient(resolved)
    if resolved.provider == "openai":
        return OpenAIRetrievalClient(resolved)

    raise ValueError(f"Unsupported retrieval provider '{resolved.provider}'")


# Tool definitions for LLM API
TOOLS = [
    {
        "name": "view_node_and_children",
        "description": "View a specific node in the ChatIndex tree and see its children. "
                      "Returns the node's topic name, summary, message range (start_index to end_index), "
                      "and a list of all direct children with their basic information. "
                      "Use this to navigate the conversation tree structure.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_path": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Path to the node as a list of child indices from root. "
                                 "Empty array [] means root node. [0] means first child of root. "
                                 "[0, 1] means second child of first child of root, etc."
                }
            },
            "required": ["node_path"]
        }
    },
    {
        "name": "get_node_messages",
        "description": "Retrieve the actual conversation messages covered by a node using its start and end indices. "
                      "Returns all messages in the range [start_index, end_index) from the conversation history. "
                      "Use this to read the actual content of a conversation segment after identifying it with view_node_and_children.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_index": {
                    "type": "integer",
                    "description": "Starting index in the conversation (inclusive)",
                    "minimum": 0
                },
                "end_index": {
                    "type": "integer",
                    "description": "Ending index in the conversation (exclusive)",
                    "minimum": 0
                }
            },
            "required": ["start_index", "end_index"]
        }
    },
    {
        "name": "vector_search",
        "description": "Search conversation exchanges by similarity to a natural-language query. "
                      "Returns ranked matches with message_index, similarity score, previews, and "
                      "message ranges suitable for get_node_messages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language search query"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of ranked results to return",
                    "minimum": 1
                }
            },
            "required": ["query"]
        }
    }
]


class ChatIndexTools:
    """Handler for ChatIndex tool operations with LLM API."""

    def __init__(self, ctree: CTree):
        """
        Initialize ChatIndex tools with a CTree instance.

        Args:
            ctree: A CTree instance with conversation data
        """
        self.ctree = ctree
        self._vector_index: Optional[VectorIndex] = None

    def _get_vector_index(self) -> VectorIndex:
        if self._vector_index is None:
            self._vector_index = VectorIndex.from_ctree(self.ctree)
        return self._vector_index

    def view_node_and_children(self, node_path: List[int]) -> Dict[str, Any]:
        """
        View a node and its children in the CTree.

        Args:
            node_path: List of child indices from root. Empty list for root.

        Returns:
            Dictionary with node information and children details
        """
        try:
            # Start from root
            current_node = self.ctree.root

            # Navigate to the target node
            for idx in node_path:
                children = getattr(current_node, "children", None)
                if (
                    children is None
                    or type(idx) is not int
                    or idx < 0
                    or idx >= len(children)
                ):
                    return {
                        "error": f"Invalid path: No child at index {idx}",
                        "valid_indices": list(range(len(children))) if children is not None else []
                    }
                current_node = children[idx]

            # Build response
            result = {
                "node_path": node_path,
                "node_type": "topic" if isinstance(current_node, TopicNode) else "message",
            }

            if isinstance(current_node, TopicNode):
                result.update({
                    "topic_name": current_node.topic_name,
                    "summary": current_node.summary if current_node.summary else "No summary available",
                    "start_index": current_node.start_index,
                    "end_index": current_node.end_index,
                    "message_count": current_node.get_message_count(),
                    "child_count": current_node.sub_node_count,
                    "children": []
                })

                # Add children information
                for i, child in enumerate(current_node.children):
                    if isinstance(child, TopicNode):
                        result["children"].append({
                            "index": i,
                            "type": "topic",
                            "topic_name": child.topic_name,
                            "summary": child.summary if child.summary else "No summary",
                            "start_index": child.start_index,
                            "end_index": child.end_index,
                            "message_count": child.get_message_count(),
                            "child_count": child.sub_node_count
                        })
                    elif isinstance(child, MessageNode):
                        result["children"].append({
                            "index": i,
                            "type": "message",
                            "message_index": child.message_index,
                            "user_preview": child.user_message["content"][:100] + "..."
                                          if len(child.user_message["content"]) > 100
                                          else child.user_message["content"],
                            "assistant_preview": child.assistant_message["content"][:100] + "..."
                                               if len(child.assistant_message["content"]) > 100
                                               else child.assistant_message["content"]
                        })
            else:  # MessageNode
                result.update({
                    "message_index": current_node.message_index,
                    "user_message": current_node.user_message,
                    "assistant_message": current_node.assistant_message,
                    "system_message": current_node.system_message
                })

            return result

        except Exception as e:
            return {"error": f"Error viewing node: {str(e)}"}

    def get_node_messages(self, start_index: int, end_index: int) -> Dict[str, Any]:
        """
        Get messages from the conversation using start and end indices.

        Args:
            start_index: Starting index (inclusive)
            end_index: Ending index (exclusive)

        Returns:
            Dictionary with messages in the specified range
        """
        try:
            if start_index < 0 or end_index < 0:
                return {"error": "Indices must be non-negative"}

            if start_index >= end_index:
                return {"error": "start_index must be less than end_index"}

            total_messages = len(self.ctree.conversation)

            if start_index >= total_messages:
                return {
                    "error": f"start_index {start_index} exceeds conversation length {total_messages}"
                }

            # Clamp end_index to conversation length
            actual_end = min(end_index, total_messages)

            messages = self.ctree.conversation[start_index:actual_end]

            return {
                "start_index": start_index,
                "end_index": actual_end,
                "requested_end_index": end_index,
                "message_count": len(messages),
                "messages": messages
            }

        except Exception as e:
            return {"error": f"Error retrieving messages: {str(e)}"}

    def vector_search(self, query: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Search indexed conversation exchanges by deterministic vector similarity.

        Args:
            query: Natural-language search query
            top_k: Maximum number of ranked results to return

        Returns:
            Dictionary with ranked vector-search matches
        """
        try:
            if not isinstance(query, str) or not query.strip():
                return {"error": "query must be a non-empty string"}

            results = self._get_vector_index().search(query.strip(), top_k=top_k)
            return {
                "query": query.strip(),
                "top_k": len(results),
                "result_count": len(results),
                "results": results,
            }

        except Exception as e:
            return {"error": f"Error performing vector search: {str(e)}"}

    def process_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a tool call from LLM.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        if tool_name == "view_node_and_children":
            return self.view_node_and_children(tool_input["node_path"])
        elif tool_name == "get_node_messages":
            return self.get_node_messages(tool_input["start_index"], tool_input["end_index"])
        elif tool_name == "vector_search":
            return self.vector_search(
                tool_input["query"],
                top_k=tool_input.get("top_k"),
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}


def query_ctree(
    api_key: Optional[str],
    ctree: CTree,
    user_query: str,
    max_turns: int = 50,
    provider: str = DEFAULT_RETRIEVAL_PROVIDER,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    config: Optional[LLMProviderConfig] = None,
    llm_client: Any = None,
) -> Dict[str, Any]:
    """
    Query a CTree to answer questions about the conversation.

    Args:
        api_key: Provider API key. Defaults to Anthropic for backward compatibility.
        ctree: CTree instance with conversation data
        user_query: User's question about the conversation
        max_turns: Maximum number of conversation turns
        provider: Retrieval provider name ("anthropic" or "openai")
        model: Provider model name. Uses provider defaults when omitted.
        max_tokens: Maximum tokens for each provider call.
        config: Optional LLMProviderConfig. Explicit arguments override matching fields.
        llm_client: Optional test/client injection implementing create_message().

    Returns:
        Dictionary with the conversation history and final response
    """
    client = llm_client or build_retrieval_client(
        api_key=api_key,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        config=config,
    )
    tools_handler = ChatIndexTools(ctree)

    # Initial system message explaining the context
    system_message = """You are an AI assistant with access to a ChatIndex tree structure containing a conversation history.

The conversation is organized hierarchically into topics and subtopics. You have three tools available:

1. view_node_and_children: Navigate the tree structure to understand topics and subtopics
2. get_node_messages: Retrieve actual message content from specific ranges
3. vector_search: Find candidate exchanges by similarity to a natural-language query

Start by viewing the root node to understand the conversation structure, then drill down into relevant topics or use vector_search to find candidate exchanges. Use get_node_messages with the returned start_index and end_index to read the raw conversation range.

Each vector_search result includes message_index, score, previews, and a message range suitable for get_node_messages.

The tree uses a path-based navigation system where each node is accessed by a list of child indices from root:
- [] = root node
- [0] = first child of root
- [0, 1] = second child of the first child of root
- etc.

Each TopicNode has start_index and end_index fields that define the range of messages it covers."""

    messages = [
        {"role": "user", "content": user_query}
    ]

    conversation_history = []

    for turn in range(max_turns):
        # Make API call to LLM
        response = client.create_message(
            system=system_message,
            tools=TOOLS,
            messages=messages,
        )

        conversation_history.append({
            "turn": turn + 1,
            "response": response.raw_response if response.raw_response is not None else response
        })

        # Check if we're done (no tool use)
        if response.stop_reason == "end_turn":
            # Extract final text response
            final_response = ""
            for block in response.content:
                if _block_type(block) == "text":
                    final_response += _block_value(block, "text", "")

            return {
                "success": True,
                "final_response": final_response,
                "turns_used": turn + 1,
                "conversation_history": conversation_history
            }

        # Process tool calls
        if response.stop_reason == "tool_use":
            # Add assistant message to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process each tool use
            tool_results = []
            for block in response.content:
                if _block_type(block) == "tool_use":
                    result = tools_handler.process_tool_call(
                        _block_value(block, "name"),
                        _block_value(block, "input", {}),
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": _block_value(block, "id"),
                        "content": json.dumps(result, indent=2)
                    })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })
        else:
            # Unexpected stop reason
            return {
                "success": False,
                "error": f"Unexpected stop reason: {response.stop_reason}",
                "turns_used": turn + 1,
                "conversation_history": conversation_history
            }

    return {
        "success": False,
        "error": f"Reached maximum turns ({max_turns})",
        "conversation_history": conversation_history
    }


def query_ctree_streaming(
    api_key: Optional[str],
    ctree: CTree,
    user_query: str,
    max_turns: int = 50,
    on_text_chunk: Optional[Callable[[str], None]] = None,
    on_tool_use: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    on_turn_complete: Optional[Callable[[int], None]] = None,
    provider: str = DEFAULT_RETRIEVAL_PROVIDER,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    config: Optional[LLMProviderConfig] = None,
    llm_client: Any = None,
) -> Dict[str, Any]:
    """
    Query a CTree with streaming output.

    Args:
        api_key: Provider API key. Defaults to Anthropic for backward compatibility.
        ctree: CTree instance with conversation data
        user_query: User's question about the conversation
        max_turns: Maximum number of conversation turns
        on_text_chunk: Callback for text chunks (chunk_text: str)
        on_tool_use: Callback for tool use (tool_name: str, tool_input: dict)
        on_turn_complete: Callback when turn completes (turn_number: int)
        provider: Retrieval provider name ("anthropic" or "openai")
        model: Provider model name. Uses provider defaults when omitted.
        max_tokens: Maximum tokens for each provider call.
        config: Optional LLMProviderConfig. Explicit arguments override matching fields.
        llm_client: Optional test/client injection implementing stream_message().

    Returns:
        Dictionary with the conversation history and final response
    """
    client = llm_client or build_retrieval_client(
        api_key=api_key,
        provider=provider,
        model=model,
        max_tokens=max_tokens,
        config=config,
    )
    tools_handler = ChatIndexTools(ctree)

    # Initial system message explaining the context
    system_message = """You are an AI assistant with access to a ChatIndex tree structure containing a conversation history.

The conversation is organized hierarchically into topics and subtopics. You have three tools available:

1. view_node_and_children: Navigate the tree structure to understand topics and subtopics
2. get_node_messages: Retrieve actual message content from specific ranges
3. vector_search: Find candidate exchanges by similarity to a natural-language query

Start by viewing the root node to understand the conversation structure, then drill down into relevant topics or use vector_search to find candidate exchanges. Use get_node_messages with the returned start_index and end_index to read the raw conversation range.

Each vector_search result includes message_index, score, previews, and a message range suitable for get_node_messages.

The tree uses a path-based navigation system where each node is accessed by a list of child indices from root:
- [] = root node
- [0] = first child of root
- [0, 1] = second child of the first child of root
- etc.

Each TopicNode has start_index and end_index fields that define the range of messages it covers."""

    messages = [
        {"role": "user", "content": user_query}
    ]

    conversation_history = []
    final_response = ""

    for turn in range(max_turns):
        # Make streaming API call to LLM
        streamed_chunks = []

        def handle_text_chunk(chunk_text: str) -> None:
            streamed_chunks.append(chunk_text)
            if on_text_chunk:
                on_text_chunk(chunk_text)

        final_message = client.stream_message(
            system=system_message,
            tools=TOOLS,
            messages=messages,
            on_text_chunk=handle_text_chunk,
        )
        final_response += "".join(streamed_chunks)

        conversation_history.append({
            "turn": turn + 1,
            "response": final_message.raw_response if final_message.raw_response is not None else final_message
        })

        if on_turn_complete:
            on_turn_complete(turn + 1)

        # Check if we're done (no tool use)
        if final_message.stop_reason == "end_turn":
            if not final_response:
                final_response = "".join(
                    _block_value(block, "text", "")
                    for block in final_message.content
                    if _block_type(block) == "text"
                )
            return {
                "success": True,
                "final_response": final_response,
                "turns_used": turn + 1,
                "conversation_history": conversation_history
            }

        # Process tool calls
        if final_message.stop_reason == "tool_use":
            # Add assistant message to conversation
            messages.append({
                "role": "assistant",
                "content": final_message.content
            })

            # Process each tool use
            tool_results = []
            for block in final_message.content:
                if _block_type(block) == "tool_use":
                    tool_name = _block_value(block, "name")
                    tool_input = _block_value(block, "input", {})
                    if on_tool_use:
                        on_tool_use(tool_name, tool_input)

                    result = tools_handler.process_tool_call(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": _block_value(block, "id"),
                        "content": json.dumps(result, indent=2)
                    })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })
        else:
            # Unexpected stop reason
            return {
                "success": False,
                "error": f"Unexpected stop reason: {final_message.stop_reason}",
                "turns_used": turn + 1,
                "conversation_history": conversation_history
            }

    return {
        "success": False,
        "error": f"Reached maximum turns ({max_turns})",
        "conversation_history": conversation_history
    }
