import time
from chat.v1.channel_rbt import (
    Channel,
    ChannelCreateRequest,
    ChannelCreateResponse,
    MessagesRequest,
    MessagesResponse,
    PostRequest,
    PostResponse,
)
from chat.v1.message_rbt import Message
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import ReaderContext, TransactionContext
from reboot.protobuf import as_str, from_str
from reboot.std.index.v1.index import Index
from uuid import uuid4


def messages_id(state_id: str):
    return f"{state_id}-messages"


class ChannelServicer(Channel.Servicer):

    def authorizer(self):
        return allow()

    async def Create(
        self,
        context: TransactionContext,
        request: ChannelCreateRequest,
    ) -> ChannelCreateResponse:
        await Index.Create(
            context,
            messages_id(context.state_id),
            order=100,
        )
        return ChannelCreateResponse()

    async def Post(
        self,
        context: TransactionContext,
        request: PostRequest,
    ) -> PostResponse:
        # Generate a unique ID for this message.
        message_id = str(uuid4())

        await Message.ref(message_id).Edit(
            context,
            author=request.author,
            text=request.text,
        )

        await self._messages.Insert(
            context,
            key=f'{round(time.time() * 1000)}',
            value=from_str(message_id),
        )

        return PostResponse(message_id=message_id)

    async def Messages(
        self,
        context: ReaderContext,
        request: MessagesRequest,
    ) -> MessagesResponse:
        response = await self._messages.ReverseRange(
            context,
            limit=request.limit,
        )

        timestamps = [entry.key for entry in response.entries]
        message_ids = [as_str(entry.value) for entry in response.entries]

        responses = await Message.forall(message_ids).Get(context)

        return MessagesResponse(
            messages={
                timestamps[i]: response.details
                for i, response in enumerate(responses)
            }
        )

    @property
    def _messages(self):
        return Index.ref(messages_id(self.ref().state_id))
