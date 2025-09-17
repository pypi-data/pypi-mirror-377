import inspect
import logging
import os
from functools import wraps
from typing import Callable, TypeVar

from faust import App, Stream, TopicT
from faust.agents import AgentT

from .response import Response
from .serializer import ReadStream, StreamSerializer, WriteStream

_logger = logging.getLogger(__name__)

_T = TypeVar("_T")

StreamFunction = Callable[[StreamSerializer], Response]
StreamDecorator = Callable[[StreamFunction], AgentT[_T]]


def stream(
    app: App, topic: TopicT, **kwargs
) -> Callable[[StreamDecorator], AgentT[_T]]:
    def decorator(func: StreamFunction) -> AgentT[_T]:
        @wraps(func)
        async def streaming(stream: Stream):
            async for value in stream:
                if not isinstance(value, StreamSerializer) or value.validate():
                    continue

                _logger.info(
                    f"<{stream.channel}--{value.action}> :: {value.id} :: Processing..."
                )

                # Always call func correctly and ensure result is a Response
                if inspect.iscoroutinefunction(func):
                    result = await func(value)
                else:
                    result = func(value)
                if not isinstance(result, Response):
                    raise TypeError(
                        f"Function {func.__name__} did not return a Response instance"
                        f", got {type(result)}"
                    )

                response: Response = result
                response.id = value.id
                _logger.info(
                    f"<{stream.channel}--{value.action}> :: {value.id} :: "
                    f"{response.status.value} ({response.status.phrase})"
                )
                yield response.__dict__

        agent_kwargs = {
            "sink": [app.topic(os.environ["SERVICE_NAME"])],
            **kwargs,
        }
        operation = os.getenv("SERVICE_OPERATION", "rw").lower()
        if operation in ("r", "read") and issubclass(topic.value_type, ReadStream):
            return app.agent(topic, **agent_kwargs)(streaming)
        if operation in ("w", "write") and issubclass(topic.value_type, WriteStream):
            return app.agent(topic, **agent_kwargs)(streaming)
        if operation in ("rw", "read_write"):
            return app.agent(topic, **agent_kwargs)(streaming)
        return func

    return decorator
