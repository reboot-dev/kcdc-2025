from queues.v1.queue_rbt import (
    EnqueueRequest,
    EnqueueResponse,
    Item,
    DequeueRequest,
    DequeueResponse,
    Queue,
)
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import WorkflowContext, WriterContext
from reboot.aio.workflows import until
from typing import Optional


class QueueServicer(Queue.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Enqueue(
        self,
        context: WriterContext,
        request: EnqueueRequest,
    ) -> EnqueueResponse:
        # TODO: assert only one of `value`, `bytes`, `any`, or `items`.
        items = request.items if len(request.items) > 0 else [
            Item(
                value=request.value if request.HasField("value") else None,
                #bytes=request.bytes if request.HasField("bytes") else None,
                any=request.any if request.HasField("any") else None,
            )
        ]

        self.state.items.extend(items)

        return EnqueueResponse()

    async def Dequeue(
        self,
        context: WorkflowContext,
        request: DequeueRequest,
    ) -> DequeueResponse:
        bulk = request.bulk
        at_most: Optional[int] = None
        if request.bulk and request.HasField("at_most"):
            at_most = request.at_most

        async def have_items():

            async def slice_items(state):
                if len(state.items) > 0:
                    count = 1 if not bulk else (at_most or len(state.items))
                    items = state.items[:count]
                    del state.items[:count]
                    return items
                return False

            state = await self.ref().Read(context)
            if len(state.items) > 0:
                return await self.ref().Write(context, slice_items, type=list)

            return False

        items = await until("Have items", context, have_items, type=list)

        if not bulk:
            assert(len(items) == 1)
            item = items[0]
            return DequeueResponse(
                value=item.value if item.HasField("value") else None,
                #bytes=item.bytes if item.HasField("bytes") else None,
                any=item.any if item.HasField("any") else None,
            )
        else:
            return DequeueResponse(items=items)
