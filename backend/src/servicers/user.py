from chat.v1.user_rbt import (
    AddRequest,
    AddResponse,
    CreateRequest,
    CreateResponse,
    ListRequest,
    ListResponse,
    MessageReaction,
    MessagesReactionsRequest,
    MessagesReactionsResponse,
    User,
    Users,
)
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)
from reboot.protobuf import unpack
from reboot.std.index.v1.index import Index

USERS_SINGLETON = "(singleton)"


class UsersServicer(Users.Servicer):

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


class UserServicer(User.Servicer):

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
            await Index.Create(
                context,
                self._messages_reactions.state_id,
                order=100,
            )

        return CreateResponse()

    async def MessagesReactions(
        self,
        context: ReaderContext,
        request: MessagesReactionsRequest,
    ):
        # Fetch all reactions to user's messages.
        response = await self._messages_reactions.ReverseRange(
            context,
            limit=request.limit,
        )

        reactions = {
            entry.key: unpack(entry.any, MessageReaction)
            for entry in response.entries
        }

        return MessagesReactionsResponse(reactions=reactions)

    @property
    def _messages_reactions(self):
        return Index.ref(f'{self.ref().state_id}-messages-reactions')
