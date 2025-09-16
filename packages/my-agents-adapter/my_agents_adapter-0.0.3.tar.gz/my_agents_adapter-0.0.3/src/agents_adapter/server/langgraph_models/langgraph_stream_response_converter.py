from typing import List

from langchain_core.messages import AnyMessage

from ...models.openai import models as openai_models
from ..common.agent_run_context import AgentRunContext
from .response_event_generators.response_event_generator import ResponseEventGenerator, StreamEventState
from .response_event_generators.response_stream_event_generator import ResponseStreamEventGenerator


class LangGraphStreamResponseConverter:
    def __init__(self, stream, context: AgentRunContext, logger):
        self.stream = stream
        self.context = context
        self.logger = logger

        self.stream_state = StreamEventState()
        self.current_generator: ResponseEventGenerator = None

    async def convert(self):
        async for message, _ in self.stream:
            try:
                if self.current_generator is None:
                    self.current_generator = ResponseStreamEventGenerator(self.logger, None)

                converted = self.try_process_message(message, self.context)
                for event in converted:
                    yield event  # yield each event separately
            except Exception as e:
                self.logger.error(f"Error converting message {message}: {e}")
                raise ValueError(f"Error converting message {message}") from e

        self.logger.info("Stream ended, finalizing response.")
        # finalize the stream
        converted = self.try_process_message(None, self.context)
        for event in converted:
            yield event  # yield each event separately

    def try_process_message(
        self, event: AnyMessage, context: AgentRunContext
    ) -> List[openai_models.ResponseStreamEvent]:
        if event and not self.current_generator:
            self.current_generator = ResponseStreamEventGenerator(self.logger, None)

        is_processed = False
        next_processor = self.current_generator
        returned_events = []
        while not is_processed:
            is_processed, next_processor, processed_events = self.current_generator.try_process_message(
                event, context, self.stream_state
            )
            returned_events.extend(processed_events)
            if not is_processed and next_processor == self.current_generator:
                self.logger.warning(f"Message can not be processed by current generator: {event}")
                break
            if next_processor != self.current_generator:
                self.logger.info(
                    f"Switching processor from {type(self.current_generator).__name__} "
                    + f"to {type(next_processor).__name__}"
                )
                self.current_generator = next_processor
        return returned_events
