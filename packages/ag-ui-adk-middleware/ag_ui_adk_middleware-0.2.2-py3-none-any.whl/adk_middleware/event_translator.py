# src/event_translator.py

"""Event translator for converting ADK events to AG-UI protocol events."""

from typing import AsyncGenerator, Optional, Dict, Any , List
import uuid

from google.genai import types

from ag_ui.core import (
    BaseEvent, EventType,
    TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent,
    ToolCallStartEvent, ToolCallArgsEvent, ToolCallEndEvent,
    ToolCallChunkEvent,ToolCallResultEvent,
    StateSnapshotEvent, StateDeltaEvent,
    MessagesSnapshotEvent,
    CustomEvent,
    Message, AssistantMessage, UserMessage, ToolMessage
)
import json
from google.adk.events import Event as ADKEvent

import logging
logger = logging.getLogger(__name__)


class EventTranslator:
    """Translates Google ADK events to AG-UI protocol events.
    
    This class handles the conversion between the two event systems,
    managing streaming sequences and maintaining event consistency.
    """
    
    def __init__(self):
        """Initialize the event translator."""
        # Track tool call IDs for consistency 
        self._active_tool_calls: Dict[str, str] = {}  # Tool call ID -> Tool call ID (for consistency)
        # Track streaming message state
        self._streaming_message_id: Optional[str] = None  # Current streaming message ID
        self._is_streaming: bool = False  # Whether we're currently streaming a message
        self.long_running_tool_ids: List[str] = []  # Track the long running tool IDs
    
    async def translate(
        self, 
        adk_event: ADKEvent,
        thread_id: str,
        run_id: str
    ) -> AsyncGenerator[BaseEvent, None]:
        """Translate an ADK event to AG-UI protocol events.
        
        Args:
            adk_event: The ADK event to translate
            thread_id: The AG-UI thread ID
            run_id: The AG-UI run ID
            
        Yields:
            One or more AG-UI protocol events
        """
        try:
            # Check ADK streaming state using proper methods
            is_partial = getattr(adk_event, 'partial', False)
            turn_complete = getattr(adk_event, 'turn_complete', False)
            
            # Check if this is the final response (contains complete message - skip to avoid duplication)
            is_final_response = False
            if hasattr(adk_event, 'is_final_response') and callable(adk_event.is_final_response):
                is_final_response = adk_event.is_final_response()
            elif hasattr(adk_event, 'is_final_response'):
                is_final_response = adk_event.is_final_response
            
            # Determine action based on ADK streaming pattern
            should_send_end = turn_complete and not is_partial
            
            logger.info(f"📥 ADK Event: partial={is_partial}, turn_complete={turn_complete}, "
                       f"is_final_response={is_final_response}, should_send_end={should_send_end}")
            
            # Skip user events (already in the conversation)
            if hasattr(adk_event, 'author') and adk_event.author == "user":
                logger.debug("Skipping user event")
                return
            
            # Handle text content
            if adk_event.content and hasattr(adk_event.content, 'parts') and adk_event.content.parts:
                async for event in self._translate_text_content(
                    adk_event, thread_id, run_id
                ):
                    yield event
            

            

            # call _translate_function_calls function to yield Tool Events
            if hasattr(adk_event, 'get_function_calls'):               
                function_calls = adk_event.get_function_calls()
                if function_calls:
                    logger.debug(f"ADK function calls detected: {len(function_calls)} calls")
                    
                    # CRITICAL FIX: End any active text message stream before starting tool calls
                    # Per AG-UI protocol: TEXT_MESSAGE_END must be sent before TOOL_CALL_START
                    async for event in self.force_close_streaming_message():
                        yield event
                    
                    # NOW ACTUALLY YIELD THE EVENTS
                    async for event in self._translate_function_calls(function_calls):
                        yield event
                        
            # Handle function responses and yield the tool response event
            # this is essential for scenerios when user has to render function response at frontend
            if hasattr(adk_event, 'get_function_responses'):
                function_responses = adk_event.get_function_responses()
                if function_responses:
                    # Function responses should be emmitted to frontend so it can render the response as well
                    async for event in self._translate_function_response(function_responses):
                        yield event
                    
            
            # Handle state changes
            if hasattr(adk_event, 'actions') and adk_event.actions and hasattr(adk_event.actions, 'state_delta') and adk_event.actions.state_delta:
                yield self._create_state_delta_event(
                    adk_event.actions.state_delta, thread_id, run_id
                )
                
            
            # Handle custom events or metadata
            if hasattr(adk_event, 'custom_data') and adk_event.custom_data:
                yield CustomEvent(
                    type=EventType.CUSTOM,
                    name="adk_metadata",
                    value=adk_event.custom_data
                )
                
        except Exception as e:
            logger.error(f"Error translating ADK event: {e}", exc_info=True)
            # Don't yield error events here - let the caller handle errors
    
    async def _translate_text_content(
        self,
        adk_event: ADKEvent,
        thread_id: str,
        run_id: str
    ) -> AsyncGenerator[BaseEvent, None]:
        """Translate text content from ADK event to AG-UI text message events.
        
        Args:
            adk_event: The ADK event containing text content
            thread_id: The AG-UI thread ID
            run_id: The AG-UI run ID
            
        Yields:
            Text message events (START, CONTENT, END)
        """
        # Extract text from all parts
        text_parts = []
        for part in adk_event.content.parts:
            if part.text:
                text_parts.append(part.text)
        
        if not text_parts:
            return
        
        
        # Use proper ADK streaming detection (handle None values)
        is_partial = getattr(adk_event, 'partial', False)
        turn_complete = getattr(adk_event, 'turn_complete', False)
        
        # Check if this is the final response (complete message - skip to avoid duplication)
        is_final_response = False
        if hasattr(adk_event, 'is_final_response') and callable(adk_event.is_final_response):
            is_final_response = adk_event.is_final_response()
        elif hasattr(adk_event, 'is_final_response'):
            is_final_response = adk_event.is_final_response
        
        # Handle None values: if is_final_response=True, it means streaming should end
        should_send_end = is_final_response and not is_partial
        
        logger.info(f"📥 Text event - partial={is_partial}, turn_complete={turn_complete}, "
                   f"is_final_response={is_final_response}, should_send_end={should_send_end}, "
                   f"currently_streaming={self._is_streaming}")
        
        # Skip final response events to avoid duplicate content, but send END if streaming
        if is_final_response:
            logger.info("⏭️ Skipping final response event (content already streamed)")
            
            # If we're currently streaming, this final response means we should end the stream
            if self._is_streaming and self._streaming_message_id:
                end_event = TextMessageEndEvent(
                    type=EventType.TEXT_MESSAGE_END,
                    message_id=self._streaming_message_id
                )
                logger.info(f"📤 TEXT_MESSAGE_END (from final response): {end_event.model_dump_json()}")
                yield end_event
                
                # Reset streaming state
                self._streaming_message_id = None
                self._is_streaming = False
                logger.info("🏁 Streaming completed via final response")
            
            return
        
        combined_text = "".join(text_parts)  # Don't add newlines for streaming
        
        # Handle streaming logic
        if not self._is_streaming:
            # Start of new message - emit START event
            self._streaming_message_id = str(uuid.uuid4())
            self._is_streaming = True
            
            start_event = TextMessageStartEvent(
                type=EventType.TEXT_MESSAGE_START,
                message_id=self._streaming_message_id,
                role="assistant"
            )
            logger.info(f"📤 TEXT_MESSAGE_START: {start_event.model_dump_json()}")
            yield start_event
        
        # Always emit content (unless empty)
        if combined_text:
            content_event = TextMessageContentEvent(
                type=EventType.TEXT_MESSAGE_CONTENT,
                message_id=self._streaming_message_id,
                delta=combined_text
            )
            logger.info(f"📤 TEXT_MESSAGE_CONTENT: {content_event.model_dump_json()}")
            yield content_event
        
        # If turn is complete and not partial, emit END event
        if should_send_end:
            end_event = TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=self._streaming_message_id
            )
            logger.info(f"📤 TEXT_MESSAGE_END: {end_event.model_dump_json()}")
            yield end_event
            
            # Reset streaming state
            self._streaming_message_id = None
            self._is_streaming = False
            logger.info("🏁 Streaming completed, state reset")
    
    async def translate_lro_function_calls(self,adk_event: ADKEvent)-> AsyncGenerator[BaseEvent, None]:
        """Translate long running function calls from ADK event to AG-UI tool call events.
        
        Args:
            adk_event: The ADK event containing function calls
            
        Yields:
            Tool call events (START, ARGS, END)
        """
        long_running_function_call = None
        if adk_event.content and adk_event.content.parts:
            for i, part in enumerate(adk_event.content.parts):
                if part.function_call:
                    if not long_running_function_call and part.function_call.id in (
                        adk_event.long_running_tool_ids or []
                    ):
                        long_running_function_call = part.function_call
                        self.long_running_tool_ids.append(long_running_function_call.id)
                        yield ToolCallStartEvent(
                            type=EventType.TOOL_CALL_START,
                            tool_call_id=long_running_function_call.id,
                            tool_call_name=long_running_function_call.name,
                            parent_message_id=None
                        )
                        if hasattr(long_running_function_call, 'args') and long_running_function_call.args:
                            # Convert args to string (JSON format)
                            import json
                            args_str = json.dumps(long_running_function_call.args) if isinstance(long_running_function_call.args, dict) else str(long_running_function_call.args)
                            yield ToolCallArgsEvent(
                                type=EventType.TOOL_CALL_ARGS,
                                tool_call_id=long_running_function_call.id,
                                delta=args_str
                            )
                        
                        # Emit TOOL_CALL_END
                        yield ToolCallEndEvent(
                            type=EventType.TOOL_CALL_END,
                            tool_call_id=long_running_function_call.id
                        )                       
                        
                        # Clean up tracking
                        self._active_tool_calls.pop(long_running_function_call.id, None)   
    
    async def _translate_function_calls(
        self,
        function_calls: list[types.FunctionCall],
    ) -> AsyncGenerator[BaseEvent, None]:
        """Translate function calls from ADK event to AG-UI tool call events.
        
        Args:
            adk_event: The ADK event containing function calls
            function_calls: List of function calls from the event
            thread_id: The AG-UI thread ID
            run_id: The AG-UI run ID
            
        Yields:
            Tool call events (START, ARGS, END)
        """
        # Since we're not tracking streaming messages, use None for parent message
        parent_message_id = None
        
        for func_call in function_calls:
            tool_call_id = getattr(func_call, 'id', str(uuid.uuid4()))
            
            # Track the tool call
            self._active_tool_calls[tool_call_id] = tool_call_id
            
            # Emit TOOL_CALL_START
            yield ToolCallStartEvent(
                type=EventType.TOOL_CALL_START,
                tool_call_id=tool_call_id,
                tool_call_name=func_call.name,
                parent_message_id=parent_message_id
            )
            
            # Emit TOOL_CALL_ARGS if we have arguments
            if hasattr(func_call, 'args') and func_call.args:
                # Convert args to string (JSON format)
                import json
                args_str = json.dumps(func_call.args) if isinstance(func_call.args, dict) else str(func_call.args)
                
                yield ToolCallArgsEvent(
                    type=EventType.TOOL_CALL_ARGS,
                    tool_call_id=tool_call_id,
                    delta=args_str
                )
            
            # Emit TOOL_CALL_END
            yield ToolCallEndEvent(
                type=EventType.TOOL_CALL_END,
                tool_call_id=tool_call_id
            )
            
            # Clean up tracking
            self._active_tool_calls.pop(tool_call_id, None)
    

    async def _translate_function_response(
        self,
        function_response: list[types.FunctionResponse],
    ) -> AsyncGenerator[BaseEvent, None]:
        """Translate function calls from ADK event to AG-UI tool call events.
        
        Args:
            adk_event: The ADK event containing function calls
            function_response: List of function response from the event
            
        Yields:
            Tool result events (only for tool_call_ids not in long_running_tool_ids)
        """
        
        for func_response in function_response:
            
            tool_call_id = getattr(func_response, 'id', str(uuid.uuid4()))
            # Only emit ToolCallResultEvent for tool_call_ids which are not long_running_tool
            # this is because long running tools are handle by the frontend
            if tool_call_id not in self.long_running_tool_ids:
                yield ToolCallResultEvent(
                    message_id=str(uuid.uuid4()),
                    type=EventType.TOOL_CALL_RESULT,
                    tool_call_id=tool_call_id,
                    content=json.dumps(func_response.response)
                )
            else:
                logger.debug(f"Skipping ToolCallResultEvent for long-running tool: {tool_call_id}")
  
    def _create_state_delta_event(
        self,
        state_delta: Dict[str, Any],
        thread_id: str,
        run_id: str
    ) -> StateDeltaEvent:
        """Create a state delta event from ADK state changes.
        
        Args:
            state_delta: The state changes from ADK
            thread_id: The AG-UI thread ID
            run_id: The AG-UI run ID
            
        Returns:
            A StateDeltaEvent
        """
        # Convert to JSON Patch format (RFC 6902)
        # Use "add" operation which works for both new and existing paths
        patches = []
        for key, value in state_delta.items():
            patches.append({
                "op": "add",
                "path": f"/{key}",
                "value": value
            })
        
        return StateDeltaEvent(
            type=EventType.STATE_DELTA,
            delta=patches
        )
    
    def _create_state_snapshot_event(
        self,
        state_snapshot: Dict[str, Any],
    ) -> StateSnapshotEvent:
        """Create a state snapshot event from ADK state changes.
        
        Args:
            state_snapshot: The state changes from ADK
            
        Returns:
            A StateSnapshotEvent
        """
 
        return StateSnapshotEvent(
            type=EventType.STATE_SNAPSHOT,
            snapshot=state_snapshot
        )
    
    async def force_close_streaming_message(self) -> AsyncGenerator[BaseEvent, None]:
        """Force close any open streaming message.
        
        This should be called before ending a run to ensure proper message termination.
        
        Yields:
            TEXT_MESSAGE_END event if there was an open streaming message
        """
        if self._is_streaming and self._streaming_message_id:
            logger.warning(f"🚨 Force-closing unterminated streaming message: {self._streaming_message_id}")
            
            end_event = TextMessageEndEvent(
                type=EventType.TEXT_MESSAGE_END,
                message_id=self._streaming_message_id
            )
            logger.info(f"📤 TEXT_MESSAGE_END (forced): {end_event.model_dump_json()}")
            yield end_event
            
            # Reset streaming state
            self._streaming_message_id = None
            self._is_streaming = False
            logger.info("🔄 Streaming state reset after force-close")

    def reset(self):
        """Reset the translator state.
        
        This should be called between different conversation runs
        to ensure clean state.
        """
        self._active_tool_calls.clear()
        self._streaming_message_id = None
        self._is_streaming = False
        self.long_running_tool_ids.clear()
        logger.debug("Reset EventTranslator state (including streaming state)")