from zodchy.codex.transport import CommunicationMessage

from .contracts import TaskExecutorContract, InboxRouter


class InboxApi:
    def __init__(self, task_executor: TaskExecutorContract, router: InboxRouter):
        self._task_executor = task_executor
        self._router = router

    async def __call__(self, message: CommunicationMessage):
        adapter = self._router[message.routing_key]
        if adapter is None:
            print(f"Adapter not found for key: {message.key}")
            return
        task = adapter(message.body)
        return await self._task_executor.run(task)
