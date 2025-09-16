import time
from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from ...models.openai import models as openai_models
from . import LangGraphResponseConverter
from .utils import extract_function_call


class LangGraphStreamAsyncResponseConverter(LangGraphResponseConverter):
    def __init__(self, stream, run_details, logger):
        self.stream = stream
        self.run_details = run_details
        self.logger = logger
        self.sequence_number = 0

    async def convert(self):
        # response create event
        yield openai_models.ResponseCreatedEvent(
            response=openai_models.Response(
                id=self.run_details.run_id, status="in_progress", created_at=int(time.time())
            ),
            sequence_number=self.sequence_number,
        )
        self.sequence_number += 1

        # response in progress
        yield openai_models.ResponseInProgressEvent(
            response=openai_models.Response(
                id=self.run_details.run_id, status="in_progress", created_at=int(time.time())
            ),
            sequence_number=self.sequence_number,
        )
        self.sequence_number += 1

        output_index = 0
        async for message, metadata in self.stream:
            try:
                converted = self.convert_message_to_events(message, metadata, output_index)
                for event in converted:
                    yield event  # yield each event separately
                output_index += 1
            except Exception as e:
                self.logger.error(f"Error converting message {message}: {e}")
                raise ValueError(f"Error converting message {message}") from e

        # response done event
        yield openai_models.ResponseCompletedEvent(
            response=openai_models.Response(
                id=self.run_details.run_id, status="completed", created_at=int(time.time())
            ),
            sequence_number=self.sequence_number,
        )

    def convert_message_to_events(self, message, metadata, output_index):
        if isinstance(message, HumanMessage):
            return self.convert_human_message(message, output_index)
        if isinstance(message, SystemMessage):
            return self.convert_system_message(message, output_index)
        if isinstance(message, AIMessage):
            if message.tool_calls:
                return self.convert_tool_call_messages(message, output_index)
            return self.convert_ai_message(message, output_index)
        if isinstance(message, ToolMessage):
            return self.convert_tool_message(message, output_index)
        raise ValueError(f"Unknown message type: {type(message)}")

    def convert_tool_call_messages(
        self, message: AIMessage, output_index: int
    ) -> List[openai_models.ResponseStreamEvent]:
        if len(message.tool_calls) > 1:
            self.logger.warning(
                f"There are {len(message.tool_calls)} tool calls found. " + "Only the first one will be processed."
            )

        tool_call = message.tool_calls[0]
        name, call_id, argument = extract_function_call(tool_call)

        converted_events = []
        # output_item.added
        output_item_added = openai_models.ResponseOutputItemAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.FunctionToolCallItemResource(
                id=message.id,
                call_id=call_id,
                name=name,
                status="in_progress",
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_added)

        # function_call_argments_delta
        function_call_arguments_delta = openai_models.ResponseFunctionCallArgumentsDeltaEvent(
            output_index=output_index, sequence_number=self.sequence_number, item_id=message.id, delta=argument
        )
        self.sequence_number += 1
        converted_events.append(function_call_arguments_delta)

        # function_call.done
        function_call_done = openai_models.ResponseFunctionCallArgumentsDoneEvent(
            output_index=output_index, sequence_number=self.sequence_number, item_id=message.id, arguments=argument
        )
        self.sequence_number += 1
        converted_events.append(function_call_done)

        # output_item.done
        output_item_done = openai_models.ResponseOutputItemDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.FunctionToolCallItemResource(
                id=message.id,
                call_id=call_id,
                name=name,
                arguments=argument,
                status="completed",
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_done)

        return converted_events

    def convert_tool_message(self, message: ToolMessage, output_index: int) -> List[openai_models.ResponseStreamEvent]:
        converted_events = []
        # output_item.added
        output_item_added = openai_models.ResponseOutputItemAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.FunctionToolCallOutputItemResource(
                id=message.id,
                call_id=message.tool_call_id,
                output="",
                status="in_progress",
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_added)

        output_content_events = self.convert_content_events(
            content=message.content, message_id=message.id, output_index=output_index, content_index=0
        )
        converted_events.extend(output_content_events)

        # output_item.done
        output_item_done = openai_models.ResponseOutputItemDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.FunctionToolCallOutputItemResource(
                id=message.id,
                call_id=message.tool_call_id,
                output=message.content,
                status="completed",
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_done)

        return converted_events

    def convert_human_message(
        self, message: HumanMessage, output_index: int
    ) -> List[openai_models.ResponseStreamEvent]:
        converted_events = []
        # TODO: other input types
        output_item_added = openai_models.ResponseOutputItemAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesUserMessageItemResource(
                id=message.id,
                status="in_progress",
                content=[],
            ),
        )
        converted_events.append(output_item_added)
        self.sequence_number += 1

        content_events = self.convert_content_events(
            content=message.content, message_id=message.id, output_index=output_index, content_index=0
        )
        converted_events.extend(content_events)

        output_item_done = openai_models.ResponseOutputItemDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesUserMessageItemResource(
                id=message.id,
                status="completed",
                content=self.convert_MessageContent(
                    content=message.content, role=openai_models.ResponsesMessageRole.USER
                ),
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_done)

        return converted_events

    def convert_ai_message(self, message: AIMessage, output_index: int) -> List[openai_models.ResponseStreamEvent]:
        converted_events = []
        output_item_added = openai_models.ResponseOutputItemAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesAssistantMessageItemResource(
                id=message.id,
                status="in_progress",
                content=[],
            ),
        )
        converted_events.append(output_item_added)
        self.sequence_number += 1

        content_events = self.convert_content_events(
            content=message.content, message_id=message.id, output_index=output_index, content_index=0
        )
        converted_events.extend(content_events)

        output_item_done = openai_models.ResponseOutputItemDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesAssistantMessageItemResource(
                id=message.id,
                status="completed",
                content=self.convert_MessageContent(
                    content=message.content, role=openai_models.ResponsesMessageRole.ASSISTANT
                ),
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_done)

        return converted_events

    def convert_system_message(
        self, message: SystemMessage, output_index: int
    ) -> List[openai_models.ResponseStreamEvent]:
        converted_events = []
        # TODO: other input types
        output_item_added = openai_models.ResponseOutputItemAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesSystemMessageItemResource(
                id=message.id,
                status="in_progress",
                content=[],
            ),
        )
        converted_events.append(output_item_added)
        self.sequence_number += 1

        content_events = self.convert_content_events(
            content=message.content, message_id=message.id, output_index=output_index, content_index=0
        )
        converted_events.extend(content_events)

        output_item_done = openai_models.ResponseOutputItemDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item=openai_models.ResponsesSystemMessageItemResource(
                id=message.id,
                status="completed",
                content=self.convert_MessageContent(
                    content=message.content, role=openai_models.ResponsesMessageRole.SYSTEM
                ),
            ),
        )
        self.sequence_number += 1
        converted_events.append(output_item_done)

        return converted_events

    def convert_content_events(
        self,
        content: str | List[str],  # TODO: other content types
        message_id: str,
        output_index: int,
        content_index: int,
    ) -> List[openai_models.ResponseStreamEvent]:
        converted_events = []
        # content part output_text added
        output_content_add = openai_models.ResponseContentPartAddedEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item_id=message_id,
            content_index=content_index,
            part=openai_models.ItemContentOutputText(text="", annotations=[]),
        )
        self.sequence_number += 1
        converted_events.append(output_content_add)

        content_arr = [content] if isinstance(content, str) else content
        # content part output_text
        for content_str in content_arr:
            output_text_delta = openai_models.ResponseTextDeltaEvent(
                output_index=output_index,
                sequence_number=self.sequence_number,
                item_id=message_id,
                content_index=content_index,
                delta=content_str,
            )
            self.sequence_number += 1
            converted_events.append(output_text_delta)

        # content part output_text done
        output_content_done = openai_models.ResponseContentPartDoneEvent(
            output_index=output_index,
            sequence_number=self.sequence_number,
            item_id=message_id,
            part=openai_models.ItemContentOutputText(text=content_str, annotations=[]),
        )
        self.sequence_number += 1
        converted_events.append(output_content_done)
        return converted_events
