from chat.v1.user_rbt import (
    User,
    CreateRequest,
    CreateResponse,
    GetMessagesReactionsRequest,
    GetMessagesReactionsResponse,
)


class UserServicer(User.Alpha.Servicer):

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

        message_reactions_map = await SortedMap.ref(
            f'{context.state_id}-message-reactions')

        message_reactions = await message_reactions_map.Range(
            context, limit=request.page * request.items_per_page)

        return GetMessagesReactionsResponse(reactions=message_reactions)
