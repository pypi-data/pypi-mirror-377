"""
LangChain integration for Noveum Trace SDK.

This module provides a callback handler that automatically traces LangChain
operations including LLM calls, chains, agents, tools, and retrieval operations.
"""

import logging
from collections.abc import Sequence
from typing import Any, Optional, Protocol
from uuid import UUID

# Try to import LangChain dependencies
try:
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.documents import Document
    from langchain_core.outputs import LLMResult

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from noveum_trace.core.span import SpanStatus

logger = logging.getLogger(__name__)

if not LANGCHAIN_AVAILABLE:
    logger.warning("LangChain not available. Install with: pip install langchain-core")

    # Create stub base class
    class BaseCallbackHandler(Protocol):  # type: ignore[no-redef]
        def __init__(self) -> None: ...


class NoveumTraceCallbackHandler(BaseCallbackHandler):
    """LangChain callback handler for Noveum Trace integration."""

    def __init__(self) -> None:
        """Initialize the callback handler."""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install with: pip install langchain-core"
            )

        super().__init__()
        self._trace_stack: list[Any] = []  # Active traces
        self._span_stack: list[Any] = []  # Active spans
        self._current_trace: Optional[Any] = None  # Current trace context

        # Import here to avoid circular imports
        from noveum_trace import get_client

        try:
            self._client = get_client()
        except Exception as e:
            logger.warning("Failed to get Noveum Trace client: %s", e)
            self._client = None  # type: ignore[assignment]

    def _should_create_trace(
        self, event_type: str, _serialized: dict[str, Any]
    ) -> bool:
        """Determine if event should create new trace or just span."""
        if event_type in ["chain_start", "agent_start"]:
            return True  # Always create trace for chains/agents

        if event_type in ["llm_start", "retriever_start", "tool_start"]:
            return len(self._trace_stack) == 0  # Only if not nested

        return False

    def _get_operation_name(self, event_type: str, serialized: dict[str, Any]) -> str:
        """Generate standardized operation names."""
        if serialized is None:
            return f"{event_type}.unknown"
        name = serialized.get("name", "unknown")

        if event_type == "llm_start":
            # Use model name instead of class name for better readability
            model_name = self._extract_model_name(serialized)
            return f"llm.{model_name}"
        elif event_type == "chain_start":
            return f"chain.{name}"
        elif event_type == "agent_start":
            return f"agent.{name}"
        elif event_type == "retriever_start":
            return f"retrieval.{name}"
        elif event_type == "tool_start":
            return f"tool.{name}"

        return f"{event_type}.{name}"

    def _extract_model_name(self, serialized: dict[str, Any]) -> str:
        """Extract model name from serialized LLM data."""
        if not serialized:
            return "unknown"

        # Try to get model name from kwargs
        kwargs = serialized.get("kwargs", {})
        model = kwargs.get("model")
        if model:
            return model

        # Fallback to provider name
        id_path = serialized.get("id", [])
        if len(id_path) >= 2:
            # e.g., "openai" from ["langchain", "chat_models", "openai", "ChatOpenAI"]
            return id_path[-2]

        # Final fallback to class name
        return serialized.get("name", "unknown")

    def _extract_agent_type(self, serialized: dict[str, Any]) -> str:
        """Extract agent type from serialized agent data."""
        if not serialized:
            return "unknown"

        # Get agent category from ID path
        id_path = serialized.get("id", [])
        if len(id_path) >= 2:
            # e.g., "react" from ["langchain", "agents", "react", "ReActAgent"]
            return id_path[-2]

        return "unknown"

    def _extract_agent_capabilities(self, serialized: dict[str, Any]) -> str:
        """Extract agent capabilities from tools in serialized data."""
        if not serialized:
            return "unknown"

        capabilities = []
        kwargs = serialized.get("kwargs", {})
        tools = kwargs.get("tools", [])

        if tools:
            capabilities.append("tool_usage")

            # Extract specific tool types
            tool_types = set()
            for tool in tools:
                if isinstance(tool, dict):
                    tool_name = tool.get("name", "").lower()
                    if "search" in tool_name or "web" in tool_name:
                        tool_types.add("web_search")
                    elif "calc" in tool_name or "math" in tool_name:
                        tool_types.add("calculation")
                    elif "file" in tool_name or "read" in tool_name:
                        tool_types.add("file_operations")
                    elif "api" in tool_name or "request" in tool_name:
                        tool_types.add("api_calls")

            if tool_types:
                capabilities.extend(tool_types)

        # Add default capabilities
        if not capabilities:
            capabilities = ["reasoning"]

        return ",".join(capabilities)

    def _extract_tool_function_name(self, serialized: dict[str, Any]) -> str:
        """Extract function name from serialized tool data."""
        if not serialized:
            return "unknown"

        kwargs = serialized.get("kwargs", {})
        func_name = kwargs.get("name")
        if func_name:
            return func_name

        # Fallback to class name
        return serialized.get("name", "unknown")

    def _create_tool_span_from_action(
        self, action: "AgentAction", run_id: UUID
    ) -> None:
        """Create a tool span from an agent action (when on_tool_start/on_tool_end aren't triggered)."""
        try:
            tool_name = action.tool
            tool_input = str(action.tool_input)

            # Create a tool span similar to on_tool_start
            span = self._client.start_span(
                name=f"tool:{tool_name}:{tool_name}",
                attributes={
                    "langchain.run_id": str(run_id),
                    "tool.name": tool_name,
                    "tool.operation": tool_name,
                    "tool.input.input_str": tool_input,
                    "tool.input.argument_count": 1,
                    "tool.input.expression": tool_input,  # For calculator tools
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error creating tool span from action: %s", e)

    def _complete_tool_spans_from_finish(self, finish: "AgentFinish") -> None:
        """Complete any pending tool spans when agent finishes."""
        try:
            # Look for tool spans and complete them
            tool_spans_to_complete = []
            for i in range(len(self._span_stack) - 1, -1, -1):
                span = self._span_stack[i]
                span_name = getattr(span, "name", "")
                if span_name.startswith("tool:"):
                    tool_spans_to_complete.append(self._span_stack.pop(i))

            # Complete tool spans with the final result
            for tool_span in tool_spans_to_complete:
                # Extract result from the finish log
                result = "Tool execution completed"
                if hasattr(finish, "log") and finish.log:
                    # Try to extract the result from the log
                    log_lines = finish.log.split("\n")
                    for line in log_lines:
                        if "Observation:" in line:
                            result = line.replace("Observation:", "").strip()
                            break
                        elif "Final Answer:" in line:
                            result = line.replace("Final Answer:", "").strip()
                            break

                tool_span.set_attributes(
                    {
                        "tool.output.output": result,
                    }
                )
                tool_span.set_status(SpanStatus.OK)
                self._client.finish_span(tool_span)

        except Exception as e:
            logger.error("Error completing tool spans from finish: %s", e)

    def _ensure_client(self) -> bool:
        """Ensure we have a valid client."""
        if self._client is None:
            try:
                from noveum_trace import get_client

                self._client = get_client()
                return True
            except Exception as e:
                logger.warning("Noveum Trace client not available: %s", e)
                return False
        return True

    # LLM Events
    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Handle LLM start event."""
        if not self._ensure_client():
            return

        operation_name = self._get_operation_name("llm_start", serialized)

        try:
            if self._should_create_trace("llm_start", serialized):
                # Standalone LLM call - create new trace
                self._current_trace = self._client.start_trace(operation_name)
                self._trace_stack.append(self._current_trace)

            # Create span (either in new trace or existing trace)
            span = self._client.start_span(
                name=operation_name,
                attributes={
                    "langchain.run_id": str(run_id),
                    "llm.model": (
                        serialized.get("name", "unknown") if serialized else "unknown"
                    ),
                    "llm.provider": (
                        serialized.get("id", ["unknown"])[-1]
                        if serialized and isinstance(serialized.get("id"), list)
                        else (
                            serialized.get("id", "unknown") if serialized else "unknown"
                        )
                    ),
                    "llm.operation": "completion",
                    # Input attributes
                    "llm.input.prompts": prompts[:5] if len(prompts) > 5 else prompts,
                    "llm.input.prompt_count": len(prompts),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["tags", "metadata"]
                        and isinstance(v, (str, int, float, bool))
                    },
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error handling LLM start event: %s", e)

    def on_llm_end(self, response: "LLMResult", run_id: UUID, **kwargs: Any) -> None:
        """Handle LLM end event."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            span = self._span_stack.pop()

            # Add response data
            generations = []
            token_usage = {}

            if hasattr(response, "generations") and response.generations:
                generations = [
                    gen.text
                    for generation_list in response.generations
                    for gen in generation_list
                ][
                    :10
                ]  # Limit number of generations

            if hasattr(response, "llm_output") and response.llm_output:
                token_usage = response.llm_output.get("token_usage", {})

            # Flatten usage attributes to match ContextManager format
            usage_attrs = {}
            if token_usage:
                usage_attrs.update(
                    {
                        "llm.input_tokens": token_usage.get("prompt_tokens", 0),
                        "llm.output_tokens": token_usage.get("completion_tokens", 0),
                        "llm.total_tokens": token_usage.get("total_tokens", 0),
                    }
                )

            span.set_attributes(
                {
                    # Output attributes
                    "llm.output.response": generations,
                    "llm.output.response_count": len(generations),
                    "llm.output.finish_reason": (
                        response.llm_output.get("finish_reason")
                        if hasattr(response, "llm_output") and response.llm_output
                        else None
                    ),
                    # Flattened usage attributes
                    **usage_attrs,
                }
            )

            span.set_status(SpanStatus.OK)
            self._client.finish_span(span)

            # Finish trace if this was a standalone LLM call
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling LLM end event: %s", e)

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Handle LLM error event."""
        if not self._ensure_client() or not self._span_stack:
            return None

        try:
            span = self._span_stack.pop()
            span.record_exception(error)
            span.set_status(SpanStatus.ERROR, str(error))
            self._client.finish_span(span)

            # Finish trace if this was a standalone LLM call
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling LLM error event: %s", e)

        return None

    # Chain Events
    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Handle chain start event."""
        if not self._ensure_client():
            return

        operation_name = self._get_operation_name("chain_start", serialized)

        try:
            if self._should_create_trace("chain_start", serialized):
                # Create new trace for chain
                self._current_trace = self._client.start_trace(operation_name)
                self._trace_stack.append(self._current_trace)

            # Create span for chain
            span = self._client.start_span(
                name=operation_name,
                attributes={
                    "langchain.run_id": str(run_id),
                    "chain.name": (
                        serialized.get("name", "unknown") if serialized else "unknown"
                    ),
                    "chain.operation": "execution",
                    # Input attributes
                    "chain.inputs": {k: str(v) for k, v in inputs.items()},
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["tags", "metadata"]
                        and isinstance(v, (str, int, float, bool))
                    },
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error handling chain start event: %s", e)

    def on_chain_end(
        self, outputs: dict[str, Any], run_id: UUID, **kwargs: Any
    ) -> None:
        """Handle chain end event."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            span = self._span_stack.pop()

            span.set_attributes(
                {
                    # Output attributes
                    "chain.output.outputs": {k: str(v) for k, v in outputs.items()}
                }
            )

            span.set_status(SpanStatus.OK)
            self._client.finish_span(span)

            # Finish trace if this was the top-level chain
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling chain end event: %s", e)

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Handle chain error event."""
        if not self._ensure_client() or not self._span_stack:
            return None

        try:
            span = self._span_stack.pop()
            span.record_exception(error)
            span.set_status(SpanStatus.ERROR, str(error))
            self._client.finish_span(span)

            # Finish trace if this was the top-level chain
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling chain error event: %s", e)

        return None

    # Tool Events
    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        run_id: UUID,
        inputs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Handle tool start event."""
        if not self._ensure_client():
            return

        operation_name = self._get_operation_name("tool_start", serialized)

        try:
            # Check if we should create a new trace for this tool call
            if self._should_create_trace("tool_start", serialized):
                # Standalone tool call - create new trace
                self._current_trace = self._client.start_trace(operation_name)
                self._trace_stack.append(self._current_trace)

            tool_name = serialized.get("name", "unknown") if serialized else "unknown"

            # Extract actual function name from serialized data
            func_name = self._extract_tool_function_name(serialized)

            # Prepare input attributes
            input_attrs = {
                "tool.input.input_str": input_str,  # String representation for compatibility
            }

            # Add structured inputs if available
            if inputs:
                for key, value in inputs.items():
                    # Convert values to strings for attribute storage
                    input_attrs[f"tool.input.{key}"] = str(value)
                input_attrs["tool.input.argument_count"] = str(len(inputs))
            else:
                input_attrs["tool.input.argument_count"] = "0"

            span = self._client.start_span(
                name=f"tool:{tool_name}:{func_name}",
                attributes={
                    "langchain.run_id": str(run_id),
                    "tool.name": tool_name,
                    "tool.operation": func_name,
                    # Input attributes
                    **input_attrs,
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["tags", "metadata", "inputs"]
                        and isinstance(v, (str, int, float, bool))
                    },
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error handling tool start event: %s", e)

    def on_tool_end(self, output: str, run_id: UUID, **kwargs: Any) -> None:
        """Handle tool end event."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            # Find and finish the most recent tool span
            # Look for tool spans (both "tool:" and "tool_call:" patterns)
            tool_span = None
            for i in range(len(self._span_stack) - 1, -1, -1):
                span_name = getattr(self._span_stack[i], "name", "")
                if span_name.startswith("tool:") or span_name.startswith("tool_call:"):
                    tool_span = self._span_stack.pop(i)
                    break

            if tool_span:
                tool_span.set_attributes({"tool.output.output": output})
                tool_span.set_status(SpanStatus.OK)
                self._client.finish_span(tool_span)
            else:
                # Fallback to the last span if no tool span found
                span = self._span_stack.pop()
                span.set_attributes({"tool.output.output": output})
                span.set_status(SpanStatus.OK)
                self._client.finish_span(span)

            # Finish trace if this was a standalone tool call
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling tool end event: %s", e)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Handle tool error event."""
        if not self._ensure_client() or not self._span_stack:
            return None

        try:
            span = self._span_stack.pop()
            span.record_exception(error)
            span.set_status(SpanStatus.ERROR, str(error))
            self._client.finish_span(span)

        except Exception as e:
            logger.error("Error handling tool error event: %s", e)

        return None

    # Agent Events
    def on_agent_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        """Handle agent start event."""
        if not self._ensure_client():
            return

        operation_name = self._get_operation_name("agent_start", serialized)

        try:
            if self._should_create_trace("agent_start", serialized):
                # Create new trace for agent
                self._current_trace = self._client.start_trace(operation_name)
                self._trace_stack.append(self._current_trace)

            # Create span for agent
            agent_name = serialized.get("name", "unknown") if serialized else "unknown"

            # Extract actual agent information from serialized data
            agent_type = self._extract_agent_type(serialized)
            agent_capabilities = self._extract_agent_capabilities(serialized)

            span = self._client.start_span(
                name=operation_name,
                attributes={
                    "langchain.run_id": str(run_id),
                    "agent.name": agent_name,
                    "agent.type": agent_type,
                    "agent.operation": "execution",
                    "agent.capabilities": agent_capabilities,
                    # Input attributes
                    "agent.input.inputs": {k: str(v) for k, v in inputs.items()},
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["tags", "metadata"]
                        and isinstance(v, (str, int, float, bool))
                    },
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error handling agent start event: %s", e)

    def on_agent_action(
        self, action: "AgentAction", run_id: UUID, **kwargs: Any
    ) -> None:
        """Handle agent action event."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            span = self._span_stack[-1]  # Add to current span

            # Add agent output attributes
            span.set_attributes(
                {
                    "agent.output.action.tool": action.tool,
                    "agent.output.action.tool_input": str(action.tool_input),
                    "agent.output.action.log": action.log,
                }
            )

            # Add event for agent action (tool call decision)
            span.add_event(
                "agent_action",
                {
                    "action.tool": action.tool,
                    "action.tool_input": str(action.tool_input),
                    "action.log": action.log,
                },
            )

            # Also create a tool span for the tool execution
            # This handles cases where LangChain doesn't trigger on_tool_start/on_tool_end
            self._create_tool_span_from_action(action, run_id)

        except Exception as e:
            logger.error("Error handling agent action event: %s", e)

    def on_agent_finish(
        self, finish: "AgentFinish", run_id: UUID, **kwargs: Any
    ) -> None:
        """Handle agent finish event."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            # Complete any pending tool spans first
            self._complete_tool_spans_from_finish(finish)

            span = self._span_stack.pop()  # Pop the agent span

            # Add agent output attributes
            span.set_attributes(
                {
                    "agent.output.finish.return_values": {
                        k: str(v) for k, v in finish.return_values.items()
                    },
                    "agent.output.finish.log": finish.log,
                }
            )

            # Add event for agent finish
            span.add_event(
                "agent_finish",
                {
                    "finish.return_values": {
                        k: str(v) for k, v in finish.return_values.items()
                    },
                    "finish.log": finish.log,
                },
            )

            span.set_status(SpanStatus.OK)
            self._client.finish_span(span)

            # Finish trace if this was the top-level agent
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling agent finish event: %s", e)

    # Retrieval Events
    def on_retriever_start(
        self, serialized: dict[str, Any], query: str, run_id: UUID, **kwargs: Any
    ) -> None:
        """Handle retriever start event."""
        if not self._ensure_client():
            return

        operation_name = self._get_operation_name("retriever_start", serialized)

        try:
            if self._should_create_trace("retriever_start", serialized):
                # Standalone retrieval - create new trace
                self._current_trace = self._client.start_trace(operation_name)
                self._trace_stack.append(self._current_trace)

            # Create span
            span = self._client.start_span(
                name=operation_name,
                attributes={
                    "langchain.run_id": str(run_id),
                    "retrieval.type": "search",
                    "retrieval.operation": (
                        serialized.get("name", "unknown") if serialized else "unknown"
                    ),
                    # Input attributes
                    "retrieval.query": query,
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["tags", "metadata"]
                        and isinstance(v, (str, int, float, bool))
                    },
                },
            )
            self._span_stack.append(span)

        except Exception as e:
            logger.error("Error handling retriever start event: %s", e)

    def on_retriever_end(
        self,
        documents: Sequence["Document"],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Handle retriever end event."""
        if not self._ensure_client() or not self._span_stack:
            return None

        try:
            span = self._span_stack.pop()

            # Extract document content safely
            doc_previews = []
            for doc in documents[:10]:  # Limit to first 10 documents
                if hasattr(doc, "page_content"):
                    doc_previews.append(doc.page_content)

            span.set_attributes(
                {
                    # Output attributes
                    "retrieval.result_count": len(documents),
                    "retrieval.sample_results": doc_previews,
                    "retrieval.results_truncated": len(documents) > 10,
                }
            )

            span.set_status(SpanStatus.OK)
            self._client.finish_span(span)

            # Finish trace if this was a standalone retrieval
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling retriever end event: %s", e)

        return None

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Handle retriever error event."""
        if not self._ensure_client() or not self._span_stack:
            return None

        try:
            span = self._span_stack.pop()
            span.record_exception(error)
            span.set_status(SpanStatus.ERROR, str(error))
            self._client.finish_span(span)

            # Finish trace if this was a standalone retrieval
            if self._current_trace and len(self._span_stack) == 0:
                self._client.finish_trace(self._current_trace)
                if self._trace_stack:
                    self._trace_stack.pop()
                self._current_trace = None

        except Exception as e:
            logger.error("Error handling retriever error event: %s", e)

        return None

    def on_text(self, text: str, run_id: UUID, **kwargs: Any) -> None:
        """Handle text event (optional, for debugging)."""
        if not self._ensure_client() or not self._span_stack:
            return

        try:
            span = self._span_stack[-1]
            span.add_event("text_output", {"text": text})
        except Exception as e:
            logger.error("Error handling text event: %s", e)

    def __repr__(self) -> str:
        """String representation of the callback handler."""
        return (
            f"NoveumTraceCallbackHandler("
            f"active_traces={len(self._trace_stack)}, "
            f"active_spans={len(self._span_stack)})"
        )


# For backwards compatibility and ease of import
__all__ = ["NoveumTraceCallbackHandler"]
