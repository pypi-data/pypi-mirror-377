# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from agents_adapter.models import CreateResponse
from agents_adapter.server.common.id_generator.id_generator import IdGenerator


class AgentRunContext:
    def __init__(self, request: CreateResponse, id_generator: IdGenerator, response_id: str, conversation_id: str):
        self._request = request
        self._id_generator = id_generator
        self._response_id = response_id
        self._conversation_id = conversation_id

    @property
    def request(self) -> CreateResponse:
        return self._request

    @property
    def id_generator(self) -> IdGenerator:
        return self._id_generator

    @property
    def response_id(self) -> str:
        return self._response_id

    @property
    def conversation_id(self) -> str:
        return self._conversation_id
