from chat.v1.message_rbt import MessageReaction
from chat.v1.user_rbt import (
    User,
    CreateRequest,
    CreateResponse,
    GetMessagesReactionsRequest,
    GetMessagesReactionsResponse,
    AddRequest,
    AddResponse,
    ListRequest,
    ListResponse,
)
import uuid
from rbt_collections import List
from rebootdev.aio.contexts import WriterContext, ReaderContext, TransactionContext
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
        print(f"Adding user {request.user} to users list")
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
        users = Users.ref(USERS_SINGLETON)
        # We shouldn't need to do this. The frontend should be able to send this
        # to us idempotently. But that isn't currently implemented.
        key = uuid.uuid5(uuid.NAMESPACE_DNS, context.state_id)
        await users.idempotently(key=key).Add(
            context,
            user=context.state_id
        )

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
