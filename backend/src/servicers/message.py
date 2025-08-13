from chat.v1.message_rbt import (
    Details,
    EditRequest,
    EditResponse,
    GetRequest,
    GetResponse,
    Message,
)
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WriterContext,
)
from reboot.std.index.v1.index import Index


class MessageServicer(Message.Servicer):

    def authorizer(self):
        return allow()

    async def Edit(
        self,
        context: WriterContext,
        request: EditRequest,
    ) -> EditResponse:
        # We want people call this as the first function. Ensure pattern.
        if context.constructor:
            self.state.author = request.author
        else:
            assert self.state.author == request.author

        self.state.text = request.text

        return EditResponse()

    async def Get(
        self,
        context: ReaderContext,
        request: GetRequest,
    ) -> GetResponse:
        return GetResponse(
            details=Details(
                id=context.state_id,
                author=self.state.author,
                text=self.state.text,
            )
        )
