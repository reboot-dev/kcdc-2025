from chat.v1.message_rbt import MessageReaction
from chat.v1.user_rbt import (
    User,
    CreateRequest,
    CreateResponse,
    GetMessagesReactionsRequest,
    GetMessagesReactionsResponse,
)
from rbt_collections import List
from rebootdev.aio.contexts import WriterContext, ReaderContext
from reboot.aio.auth.authorizers import allow


class UserServicer(User.alpha.Servicer):
    def authorizer(self):
        return allow()

    async def Create(
        self,
        context: WriterContext,
        request: CreateRequest,
    ) -> CreateResponse:
        return CreateResponse()

    async def GetMessagesReactions(
        self,
        context: ReaderContext,
        request: GetMessagesReactionsRequest,
    ):
        reactions: list[MessageReaction] = []

        user_reactions_list = List(MessageReaction).ref(
            f'{context.state_id}-message-reactions'
        )

        page = await user_reactions_list.GetPage(
            context,
            page=request.page,
            items_per_page=request.items_per_page,
        )

        return GetMessagesReactionsResponse(reactions=page.items)
