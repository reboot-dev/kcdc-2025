import asyncio
from chat.v1.channel_rbt import (
    Channel,
    PostRequest,
    PostResponse,
    MessagesRequest,
    MessagesResponse,
)
from chat.v1.message_rbt import Message
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)
from rbt_collections import List
from reboot.aio.auth.authorizers import allow


class ChannelServicer(Channel.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Post(
        self,
        context: TransactionContext,
        request: PostRequest,
    ) -> PostResponse:
        message_id = f'message-{self.state.messages}'

        self.state.messages += 1

        await Message.ref(message_id).Edit(
            context,
            author=request.author,
            text=request.text,
        )

        await List(str).ref(f'{context.state_id}-messages').Append(
            context,
            item=message_id,
        ),

        return PostResponse(message_id=message_id)

    async def Messages(
        self,
        context: ReaderContext,
        request: MessagesRequest,
    ) -> MessagesResponse:
        page = await List(str).ref(f'{context.state_id}-messages').GetPage(
            context,
            page=request.page or -1,
            items_per_page=request.items_per_page or 20,
        )

        responses = await asyncio.gather(
            *[Message.ref(item).GetDetails(context) for item in page.items])

        return MessagesResponse(
            details=[response.details for response in responses])
