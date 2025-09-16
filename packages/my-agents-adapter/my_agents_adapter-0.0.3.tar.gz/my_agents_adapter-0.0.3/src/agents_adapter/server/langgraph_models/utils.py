import json

from langchain_core import messages as lg_messages

from ...models.openai import models as openai_models


def extract_function_call(tool_call):
    """
    Extract function call details from tool_call dict.
    Returns a tuple of (name, call_id, argument).
    """
    name = tool_call.get("name")
    call_id = tool_call.get("id")
    argument = None
    arguments_raw = tool_call.get("args")
    if isinstance(arguments_raw, str):
        argument = arguments_raw
    elif isinstance(arguments_raw, dict):
        argument = json.dumps(arguments_raw)
    return name, call_id, argument


def create_item_resource(message: lg_messages.AnyMessage) -> openai_models.ItemResource:
    """
    Create an ItemResource from a LangChain message.
    """
    return openai_models.ItemResource(id=message.id, content=message.content, metadata=message.metadata)
