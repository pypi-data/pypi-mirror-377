import typing
import inspect
import collections.abc

from functools import cached_property
from pydantic import BaseModel
from zodchy.codex.cqea import Task, Message

type InboxMessageTaskAdapterFunc = collections.abc.Callable[[BaseModel], Task]


class TaskExecutorContract(typing.Protocol):
    async def run(self, task: Task) -> list[Message]: ...


class Adapter:
    def __init__(self, adapter_func: InboxMessageTaskAdapterFunc):
        self._adapter_func = adapter_func

    @cached_property
    def input_model(self) -> type[BaseModel]:
        for param in inspect.signature(self._adapter_func).parameters.values():
            if BaseModel in param.annotation.__mro__:
                return param.annotation
        raise ValueError("Adapter has no input model")

    def __call__(self, body: dict) -> Task:
        return self._adapter_func(self.input_model.model_validate(body))


class InboxRoute:
    def __init__(self, key: str, adapter: InboxMessageTaskAdapterFunc):
        self._key = key
        self._adapter_func = adapter

    @property
    def key(self) -> str:
        return self._key

    @property
    def adapter(self) -> Adapter:
        return Adapter(self._adapter_func)


class InboxRouter:
    def __init__(self, *routes: InboxRoute):
        self._routes = {}
        self.register_routes(*routes)

    def register_routes(
        self,
        *routes: InboxRoute,
    ):
        for route in routes:
            self._routes[route.key] = route

    def __iter__(self):
        return iter(self._routes.values())

    def __add__(self, other: InboxRoute):
        return InboxRouter(
            *self._routes.values(),
            *other,
        )

    def __getitem__(self, key: str) -> Adapter | None:
        try:
            return self._routes[key].adapter
        except KeyError:
            return None
