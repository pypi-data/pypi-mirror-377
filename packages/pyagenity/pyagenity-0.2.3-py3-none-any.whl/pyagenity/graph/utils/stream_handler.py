from __future__ import annotations

import logging
import time
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any, TypeVar

from injectq import inject

from pyagenity.exceptions import GraphRecursionError
from pyagenity.graph.edge import Edge
from pyagenity.graph.node import Node
from pyagenity.state import AgentState, ExecutionStatus
from pyagenity.utils import (
    END,
    Message,
    ResponseGranularity,
    add_messages,
)
from pyagenity.utils.streaming import ContentType, Event, EventModel, EventType

from .utils import (
    call_realtime_sync,
    get_next_node,
    load_or_create_state,
    process_node_result,
    publish_event,
    sync_data,
)


StateT = TypeVar("StateT", bound=AgentState)

logger = logging.getLogger(__name__)


class StreamHandler[StateT: AgentState]:
    @inject
    def __init__(
        self,
        nodes: dict[str, Node],
        edges: list[Edge],
        interrupt_before: list[str] | None = None,
        interrupt_after: list[str] | None = None,
    ):
        self.nodes: dict[str, Node] = nodes
        self.edges: list[Edge] = edges
        self.interrupt_before = interrupt_before or []
        self.interrupt_after = interrupt_after or []

    async def _check_interrupted(
        self,
        state: StateT,
        input_data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        if state.is_interrupted():
            logger.info(
                "Resuming from interrupted state at node '%s'", state.execution_meta.current_node
            )
            # This is a resume case - clear interrupt and merge input data
            if input_data:
                config["resume_data"] = input_data
                logger.debug("Added resume data with %d keys", len(input_data))
            state.clear_interrupt()
        elif not input_data.get("messages") and not state.context:
            # This is a fresh execution - validate input data
            error_msg = "Input data must contain 'messages' for new execution."
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            logger.info(
                "Starting fresh execution with %d messages", len(input_data.get("messages", []))
            )

        return config

    async def _check_and_handle_interrupt(
        self,
        current_node: str,
        interrupt_type: str,
        state: StateT,
        config: dict[str, Any],
    ) -> bool:
        """Check for interrupts and save state if needed. Returns True if interrupted."""
        interrupt_nodes = (
            self.interrupt_before if interrupt_type == "before" else self.interrupt_after
        )

        if current_node in interrupt_nodes:
            status = (
                ExecutionStatus.INTERRUPTED_BEFORE
                if interrupt_type == "before"
                else ExecutionStatus.INTERRUPTED_AFTER
            )
            state.set_interrupt(
                current_node,
                f"interrupt_{interrupt_type}: {current_node}",
                status,
            )
            # Save state and interrupt
            await sync_data(
                state=state,
                config=config,
                messages=[],
                trim=True,
            )
            logger.debug("Node '%s' interrupted", current_node)
            return True

        logger.debug(
            "No interrupts found for node '%s', continuing execution",
            current_node,
        )
        return False

    async def _execute_graph(
        self,
        state: StateT,
        config: dict[str, Any],
    ) -> AsyncIterable[EventModel | dict[str, Any]]:
        """
        Execute the entire graph with support for interrupts and resuming.

        Why so many chunks are yielded?
        We allow user to set response type, if they want low granularity
        Only few chunks like Message will be sent to user
        """
        logger.info(
            "Starting graph execution from node '%s' at step %d",
            state.execution_meta.current_node,
            state.execution_meta.step,
        )
        messages: list[Message] = []
        messages_ids = set()
        max_steps = config.get("recursion_limit", 25)
        logger.debug("Max steps limit set to %d", max_steps)

        last_human_message = state.context[-1] if state.context else None
        if last_human_message and last_human_message.role != "user":
            msg = [msg for msg in reversed(state.context) if msg.role == "user"]
            last_human_message = msg[0] if msg else None

        if last_human_message:
            logger.debug("Last human message: %s", last_human_message.content)
            messages.append(last_human_message)

        # Get current execution info from state
        current_node = state.execution_meta.current_node
        step = state.execution_meta.step

        # Create event for graph execution
        event = EventModel.default(
            config,
            data={"state": state.model_dump(exclude={"execution_meta"})},
            content_type=[ContentType.STATE],
            extra={"step": step, "current_node": current_node},
            event=Event.GRAPH_EXECUTION,
            node_name=current_node,
        )

        try:
            while current_node != END and step < max_steps:
                logger.debug("Executing step %d at node '%s'", step, current_node)

                # Update execution metadata
                state.set_current_node(current_node)
                state.execution_meta.step = step
                await call_realtime_sync(state, config)

                # Update event with current step info
                event.data["step"] = step
                event.data["current_node"] = current_node
                event.event_type = EventType.PROGRESS
                event.metadata["status"] = f"Executing step {step} at node '{current_node}'"
                publish_event(event)
                yield event

                # Check for interrupt_before
                if await self._check_and_handle_interrupt(
                    current_node,
                    "before",
                    state,
                    config,
                ):
                    logger.info("Graph execution interrupted before node '%s'", current_node)
                    event.event_type = EventType.INTERRUPTED
                    event.metadata["status"] = "Graph execution interrupted before node execution"
                    event.metadata["interrupted"] = "Before"
                    event.data["interrupted"] = "Before"
                    publish_event(event)
                    yield event
                    return

                # Execute current node
                logger.debug("Executing node '%s'", current_node)
                node = self.nodes[current_node]

                # Node execution
                result = node.stream(config, state)  # type: ignore

                logger.debug("Node '%s' execution completed", current_node)

                # Process result and get next node
                next_node = None
                async for rs in result:
                    if isinstance(rs, EventModel):
                        # Forward node events
                        yield rs
                    elif isinstance(rs, dict) and "is_non_streaming" in rs:
                        state = rs.get("state", state)
                        new_messages = rs.get("messages", [])
                        for m in new_messages:
                            if m.message_id not in messages_ids:
                                messages.append(m)
                                messages_ids.add(m.message_id)
                        next_node = rs.get("next_node", next_node)
                    elif isinstance(rs, Message):
                        if rs.message_id not in messages_ids:
                            messages.append(rs)
                            messages_ids.add(rs.message_id)
                            state.context = add_messages(state.context, [rs])
                        logger.debug(
                            "Appended message from node '%s', total messages: %d",
                            current_node,
                            len(messages),
                        )
                    else:
                        # Process as node result
                        try:
                            state, messages, next_node = process_node_result(
                                rs,
                                state,
                                messages,
                            )
                        except Exception as e:
                            logger.error("Failed to process node result: %s", e)

                logger.debug(
                    "Node result processed, next_node=%s, total_messages=%d",
                    next_node,
                    len(messages),
                )

                # Add collected messages to state context
                if messages:
                    state.context = add_messages(state.context, messages)
                    logger.debug("Added %d messages to state context", len(messages))

                # Call realtime sync after node execution
                await call_realtime_sync(state, config)
                event.event_type = EventType.UPDATE
                event.data["state"] = state.model_dump()
                event.data["messages"] = [m.model_dump() for m in messages] if messages else []
                event.content_type = [ContentType.STATE, ContentType.MESSAGE]
                publish_event(event)
                yield event

                # Check for interrupt_after
                if await self._check_and_handle_interrupt(
                    current_node,
                    "after",
                    state,
                    config,
                ):
                    logger.info("Graph execution interrupted after node '%s'", current_node)
                    # For interrupt_after, advance to next node before pausing
                    if next_node is None:
                        next_node = get_next_node(current_node, state, self.edges)
                    state.set_current_node(next_node)

                    event.event_type = EventType.INTERRUPTED
                    event.data["interrupted"] = "After"
                    event.metadata["interrupted"] = "After"
                    event.data["state"] = state.model_dump()
                    publish_event(event)
                    yield event
                    return

                # Get next node
                if next_node is None:
                    current_node = get_next_node(current_node, state, self.edges)
                    logger.debug("Next node determined by graph logic: '%s'", current_node)
                else:
                    current_node = next_node
                    logger.debug("Next node determined by command: '%s'", current_node)

                # Advance step after successful node execution
                step += 1
                state.advance_step()
                await call_realtime_sync(state, config)

                event.event_type = EventType.UPDATE
                event.metadata["State_Updated"] = "State Updated"
                event.data["state"] = state.model_dump()
                publish_event(event)
                yield event

                if step >= max_steps:
                    error_msg = "Graph execution exceeded maximum steps"
                    logger.error(error_msg)
                    state.error(error_msg)
                    await call_realtime_sync(state, config)

                    event.event_type = EventType.ERROR
                    event.data["state"] = state.model_dump()
                    event.metadata["error"] = error_msg
                    event.metadata["step"] = step
                    event.metadata["current_node"] = current_node
                    publish_event(event)
                    yield event

                    raise GraphRecursionError(
                        f"Graph execution exceeded recursion limit: {max_steps}"
                    )

            # Execution completed successfully
            logger.info(
                "Graph execution completed successfully at node '%s' after %d steps",
                current_node,
                step,
            )
            state.complete()
            is_context_trimmed = await sync_data(
                state=state,
                config=config,
                messages=messages,
                trim=True,
            )

            # Create completion event
            event.event_type = EventType.END
            event.data["state"] = state.model_dump()
            event.data["messages"] = [m.model_dump() for m in messages] if messages else []
            event.content_type = [ContentType.STATE, ContentType.MESSAGE]
            event.metadata["status"] = "Graph execution completed"
            event.metadata["step"] = step
            event.metadata["current_node"] = current_node
            event.metadata["is_context_trimmed"] = is_context_trimmed
            publish_event(event)
            yield event

        except Exception as e:
            # Handle execution errors
            logger.exception("Graph execution failed: %s", e)
            state.error(str(e))

            # Publish error event
            event.event_type = EventType.ERROR
            event.metadata["error"] = str(e)
            event.data["state"] = state.model_dump()
            publish_event(event)

            await sync_data(
                state=state,
                config=config,
                messages=messages,
                trim=True,
            )
            raise

    async def stream(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any],
        default_state: StateT,
        response_granularity: ResponseGranularity = ResponseGranularity.LOW,
    ) -> AsyncGenerator[EventModel]:
        """Execute the graph asynchronously.

        Auto-detects whether to start fresh execution or resume from interrupted state
        based on the AgentState's execution metadata.

        Args:
            input_data: Input dict with 'messages' key (for new execution) or
                       additional data for resuming
            config: Configuration dictionary
            response_granularity: Response parsing granularity

        Returns:
            Response dict based on granularity
        """
        logger.info(
            "Starting asynchronous graph execution with %d input keys, granularity=%s",
            len(input_data) if input_data else 0,
            response_granularity,
        )
        config = config or {}
        input_data = input_data or {}

        start_time = time.time()

        # Load or initialize state
        logger.debug("Loading or creating state from input data")
        new_state = await load_or_create_state(
            input_data,
            config,
            default_state,
        )
        state: StateT = new_state  # type: ignore[assignment]
        logger.debug(
            "State loaded: interrupted=%s, current_node=%s, step=%d",
            state.is_interrupted(),
            state.execution_meta.current_node,
            state.execution_meta.step,
        )

        cfg = config.copy()
        if "user" in cfg:
            # This will be available when you are calling
            # vi pyagenity api
            del cfg["user"]

        event = EventModel.default(
            config,
            data={"state": state},
            content_type=[ContentType.STATE],
            extra={
                "is_interrupted": state.is_interrupted(),
                "current_node": state.execution_meta.current_node,
                "step": state.execution_meta.step,
                "config": cfg,
                "response_granularity": response_granularity.value,
            },
        )

        # Publish graph initialization event
        publish_event(event)

        # Check if this is a resume case
        config = await self._check_interrupted(state, input_data, config)

        # Now start Execution
        # Execute graph
        logger.debug("Beginning graph execution")
        result = self._execute_graph(state, config)
        async for chunk in result:
            # only StreamChunk will be shared with caller
            # Other types are used for internal handling
            if isinstance(chunk, EventModel):
                yield chunk

        # Publish graph completion event
        time_taken = time.time() - start_time
        logger.info("Graph execution finished in %.2f seconds", time_taken)

        event.event_type = EventType.END
        event.metadata.update(
            {
                "time_taken": time_taken,
                "state": state.model_dump(),
                "step": state.execution_meta.step,
                "current_node": state.execution_meta.current_node,
                "is_interrupted": state.is_interrupted(),
                "total_messages": len(state.context) if state.context else 0,
            }
        )
        publish_event(event)
