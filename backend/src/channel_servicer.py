from chat.v1.channel_rbt import (
    Channel,
    PostRequest,
    PostResponse,
    MessageRequest,
    MessageResponse,
)
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)


class ChannelServicer(Channel.Servicer):

    async def Post(
        self,
        context: TransactionContext,
        state: Channel.State,
        request: PostRequest,
    ) -> PostResponse:
        message_id = f'message-{state.messages}'

        state.messages += 1

        Message.ref(message_id).Edit(
            context,
            author=request.author,
            text=request.text,
        )

        SortedMap.ref(f'{context.actor_id}-messages').Insert(
            context, entries={str(message_id): context.state_id.encode()})

        return PostResponse(message_id=message_id)

    async def Messages(
        self,
        context: ReaderContext,
        state: Channel.State,
        request: MessagesRequest,
    ) -> MessageResponse:
        message_ids_map = await SortedMap.ref(f'{context.actor_id}-messages')

        message_ids = await message_ids_map.Range(context, limit=32)

        responses = await asyncio.gather(*[
            Message.ref(message_id).GetDetails(context)
            for message_id in message_ids
        ])

        return MessagesResponse(
            details=[response.details for response in responses])
