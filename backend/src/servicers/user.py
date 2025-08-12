from chat.v1.user_rbt import (
    AddRequest,
    AddResponse,
    CreateRequest,
    CreateResponse,
    ListRequest,
    ListResponse,
    User,
    Users,
)
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)

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

        return CreateResponse()
