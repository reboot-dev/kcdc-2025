from chat.v1.message_rbt import MessageReaction
from chat.v1.user_rbt import (
    User,
    CreateRequest,
    CreateResponse,
    GetMessagesReactionsRequest,
    GetMessagesReactionsResponse,
    AddRequest,
    AddResponse,
    AddChatbotRequest,
    AddChatbotResponse,
    ListRequest,
    ListResponse,
    ListChatbotsRequest,
    ListChatbotsResponse,
)
import uuid
from rbt_collections import List
from reboot.aio.contexts import WriterContext, ReaderContext, TransactionContext
from reboot.aio.auth.authorizers import allow
from chat.v1.user_rbt import Users 

USERS_SINGLETON = "(singleton)"


class UsersServicer(Users.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Add(
        self,
        context: WriterContext,
        request: AddRequest,
    ) -> AddResponse:
        self.state.users.append(request.user)
        return AddResponse()


    async def List(
        self,
        context: ReaderContext,
        request: ListRequest,
    ) -> ListResponse:
       return ListResponse(users=self.state.users)


class UserServicer(User.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Create(
        self,
        context: TransactionContext,
        request: CreateRequest,
    ) -> CreateResponse:
        if context.constructor:
            users = Users.ref(USERS_SINGLETON)
            await users.Add(context, user=context.state_id)

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

    async def AddChatbot(
        self,
        context: TransactionContext,
        request: AddChatbotRequest,
    ) -> AddChatbotResponse:

        chatbot, _ = await Chatbot.Create(
            context,
            name=request.name,
            channel_id=request.channel_id,
            prompt=request.prompt,
            human_in_the_loop=request.human_in_the_loop,
        )

        self.state.chatbot_ids.append(chatbot.state_id)

        return AddChatbotResponse()

    async def ListChatbots(
        self,
        context: ReaderContext,
        request: ListChatbotsRequest,
    ) -> ListChatbotsResponse:
        return ListChatbotsResponse(chatbot_ids=self.state.chatbot_ids)
