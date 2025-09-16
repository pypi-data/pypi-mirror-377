## Supported frameworks

- [WIP] langgraph
- [WIP] Microsoft Agent Framework

## Install

In current folder, run:
```bash
pip install -e .
```

## Usage

### langgraph

```python
# your existing agent
from my_langgraph_agent import my_awesome_agent

# langgraph utils
from agents_adapter import from_langgraph

if __name__ == "__main__":
    # with this simple line, your agent will be hosted on http://localhost:8088
    from_langgraph(my_awesome_agent).run()

```


### Microsoft Agent Framework

```python
# your existing agent
from my_framework_agent import my_awesome_agent

# agent framework utils
from agents_adapter import from_agent_framework

if __name__ == "__main__":
    # with this simple line, your agent will be hosted on http://localhost:8088
    from_agent_framework(my_awesome_agent).run()

```

### Custom Code
If your agent is not built using a supported framework, you can still make it compatible with Microsoft AI Foundry by manually implementing the predefined interface.

```python
import datetime

from agents_adapter import FoundryCBAgent
from agents_adapter.models.azureaiagents.models import CreateResponse
from agents_adapter.models.openai.models import (
    ItemContentOutputText,
    Response as OpenAIResponse,
    ResponsesAssistantMessageItemResource,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)


def stream_events(text: str):
    assembled = ""
    for i, token in enumerate(text.split(" ")):
        piece = token if i == len(text.split(" ")) - 1 else token + " "
        assembled += piece
        yield ResponseTextDeltaEvent(delta=piece)
    # Done with text
    yield ResponseTextDoneEvent(text=assembled)


async def agent_run(request_body: CreateResponse):
    agent = request_body.agent
    print(f"agent:{agent}")

    if request_body.stream:
        return stream_events("I am mock agent with no intelligence in stream mode.")

    # Build assistant output content
    output_content = [
        ItemContentOutputText(
            text="I am mock agent with no intelligence.",
            annotations=[],
        )
    ]

    response = OpenAIResponse(
        metadata={},
        temperature=0.0,
        top_p=0.0,
        user="me",
        id="id",
        created_at=datetime.datetime.now(),
        output=[
            ResponsesAssistantMessageItemResource(
                status="completed",
                content=output_content,
            )
        ],
    )
    return response


my_agent = FoundryCBAgent()
my_agent.agent_run = agent_run

if __name__ == "__main__":
    my_agent.run()

```