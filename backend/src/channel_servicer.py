from chat.v1.channel_rbt import (
    Channel,
    PostRequest,
    PostResponse,
    MessagesRequest,
    MessagesResponse,
)
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)


class ChannelServicer(Channel.alpha.Servicer):

    async def Post(
        self,
        context: TransactionContext,
        request: PostRequest,
    ) -> PostResponse:
        message_id = f'message-{self.state.messages}'

        self.state.messages += 1

        Message.ref(message_id).Edit(
            context,
            author=request.author,
            text=request.text,
        )

        SortedMap.ref(f'{context.state_id}-messages').Insert(
            context, entries={str(message_id): context.state_id.encode()})

        return PostResponse(message_id=message_id)

    async def Messages(
        self,
        context: ReaderContext,
        request: MessagesRequest,
    ) -> MessagesResponse:
        message_ids_map = await SortedMap.ref(f'{context.state_id}-messages')

        message_ids = await message_ids_map.Range(context, limit=32)

        responses = await asyncio.gather(*[
            Message.ref(message_id).GetDetails(context)
            for message_id in message_ids
        ])

        return MessagesResponse(
            details=[response.details for response in responses])
