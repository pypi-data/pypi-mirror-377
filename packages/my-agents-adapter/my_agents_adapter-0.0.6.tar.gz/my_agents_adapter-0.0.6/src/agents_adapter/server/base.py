import inspect
import json
import os
from abc import abstractmethod
from typing import Any, AsyncGenerator, Generator, Union

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from ..logger import get_logger
from ..models.azureaiagents.models import CreateResponse
from ..models.openai.models import ImplicitUserMessage, ItemParam, Response as OpenAIResponse, ResponseStreamEvent
from .common.agent_run_context import AgentRunContext
from .common.id_generator.foundry_id_generator import FoundryIdGenerator

logger = get_logger()


class FoundryCBAgent:
    def __init__(self):
        async def runs_endpoint(request):
            payload = await request.json()
            try:
                request_body = _deserialize_create_response(payload)

                id_generator = FoundryIdGenerator.from_request(request_body)
                context = AgentRunContext(
                    request_body, id_generator, id_generator.response_id, id_generator.conversation_id
                )
            except Exception as e:  # noqa: BLE001
                logger.exception("Invalid request body for /runs")
                return JSONResponse({"error": str(e)}, status_code=400)
            resp = await self.agent_run(request_body, context)

            if inspect.isgenerator(resp):

                def gen():
                    for event in resp:
                        yield _event_to_sse_chunk(event)

                return StreamingResponse(gen(), media_type="text/event-stream")
            if inspect.isasyncgen(resp):

                async def gen():
                    async for event in resp:
                        yield _event_to_sse_chunk(event)

                return StreamingResponse(gen(), media_type="text/event-stream")
            return JSONResponse(resp.as_dict())

        async def liveness_endpoint(request):
            result = await self.agent_liveness(request)
            return _to_response(result)

        async def readiness_endpoint(request):
            result = await self.agent_readiness(request)
            return _to_response(result)

        routes = [
            Route("/runs", runs_endpoint, methods=["POST"], name="agent_run"),
            Route("/responses", runs_endpoint, methods=["POST"], name="agent_response"),
            Route("/liveness", liveness_endpoint, methods=["GET"], name="agent_liveness"),
            Route("/readiness", readiness_endpoint, methods=["GET"], name="agent_readiness"),
        ]

        self.app = Starlette(routes=routes)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @abstractmethod
    async def agent_run(
        self, request_body: CreateResponse, context: AgentRunContext
    ) -> Union[OpenAIResponse, Generator[ResponseStreamEvent, Any, Any], AsyncGenerator[ResponseStreamEvent, Any]]:
        raise NotImplementedError

    async def agent_liveness(self, request) -> Union[Response, dict]:
        return Response(status_code=200)

    async def agent_readiness(self, request) -> Union[Response, dict]:
        return {"status": "ready"}

    async def run_async(
        self,
        port: int = int(os.environ.get("DEFAULT_AD_PORT", 8088)),
    ) -> None:
        """
        Awaitable server starter for use **inside** an existing event loop.
        """
        config = uvicorn.Config(self.app, host="0.0.0.0", port=port, loop="asyncio")
        server = uvicorn.Server(config)
        logger.info(f"Starting FoundryCBAgent server async on port {port}")
        await server.serve()

    def run(self, port: int = int(os.environ.get("DEFAULT_AD_PORT", 8088))) -> None:
        """
        Start a Starlette server on localhost:<port> exposing:
          POST  /runs
          GET   /liveness
          GET   /readiness
        """
        logger.info(f"Starting FoundryCBAgent server on port {port}")
        uvicorn.run(self.app, host="0.0.0.0", port=port)


def _deserialize_create_response(payload: dict) -> CreateResponse:
    _deserialized = CreateResponse._deserialize(payload, [])

    raw_input = payload.get("input")
    if raw_input:
        if isinstance(raw_input, str):
            raw_input = {"content": {"type": "input_text", "text": raw_input}}
            _deserialized.input = [ImplicitUserMessage._deserialize(raw_input, [])]
        
        elif isinstance(raw_input, list):
            _deserialized_input = []
            for input in raw_input:
                if isinstance(input, dict):
                    if "type" in input:
                        _deserialized_input.append(ItemParam._deserialize(input, []))
                    # Hack code to support multiple inputs
                    elif "role" in input and "content" in input:
                        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
                        role = input["role"]
                        content = input["content"]
                        if role == "user":
                            _deserialized_input.append(HumanMessage(content=content))
                        elif role == "system":
                            _deserialized_input.append(SystemMessage(content=content))
                        elif role == "assistant":
                            _deserialized_input.append(AIMessage(content=content))
                    else:
                        _deserialized_input.append(ImplicitUserMessage._deserialize(input, []))
                else:
                    logger.warning(f"Unexpected input type in 'input' list: {type(input).__name__}")
            _deserialized.input = _deserialized_input
    return _deserialized


def _event_to_sse_chunk(event: ResponseStreamEvent) -> str:
    event_data = json.dumps(event.as_dict())
    if event.type:
        return f"event: {event.type}\ndata: {event_data}\n\n"
    return f"data: {event_data}\n\n"


def _to_response(result: Union[Response, dict]) -> Response:
    return result if isinstance(result, Response) else JSONResponse(result)
