from chat.v1.message_rbt import (
    AddReactionRequest,
    AddReactionResponse,
    AppendReactionToUsersMessageReactionsRequest,
    AppendReactionToUsersMessageReactionsResponse,
    Details,
    EditRequest,
    EditResponse,
    GetDetailsRequest,
    GetDetailsResponse,
    GetReactionsRequest,
    GetReactionsResponse,
    Message,
    MessageReaction,
    RemoveReactionRequest,
    RemoveReactionResponse,
)
from rbt_collections import List
from rebootdev.aio.contexts import (
    WriterContext,
    ReaderContext,
    TransactionContext,
    WorkflowContext,
)
from reboot.aio.auth.authorizers import allow


class MessageServicer(Message.alpha.Servicer):
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

    async def GetDetails(
        self,
        context: ReaderContext,
        request: GetDetailsRequest,
    ) -> GetDetailsResponse:
        return GetDetailsResponse(details=Details(
            id=context.state_id,
            author=self.state.author,
            text=self.state.text,
            reactions=self.state.reactions,
        ))

    async def AddReaction(
        self,
        context: TransactionContext,
        request: AddReactionRequest,
    ) -> AddReactionResponse:
        assert request.author != ''

        if request.author in self.state.reactions[request.unicode].ids:
            return AddReactionResponse()

        user_message_reactions = List(MessageReaction).ref(
            f'{self.state.author}-message-reactions')

        snippet = ' '.join(self.state.text.split()[:3])

        if len(snippet) < len(self.state.text):
            snippet += "..."

        await user_message_reactions.Append(
            context,
            item=MessageReaction(
                message_id=context.state_id,
                unicode=request.unicode,
                author=request.author,
                snippet=snippet,
            ),
        )

        self.state.reactions[request.unicode].ids.append(request.author)

        return AddReactionResponse()

    async def RemoveReaction(
        self,
        context: TransactionContext,
        request: RemoveReactionRequest,
    ) -> RemoveReactionResponse:
        assert request.author != ''

        if request.author not in self.state.reactions[request.unicode].ids:
            return RemoveReactionResponse()

        user_message_reactions = List(MessageReaction).ref(
            f'{self.state.author}-message-reactions')

        await user_message_reactions.Remove(
            context,
            item=MessageReaction(
                message_id=context.state_id,
                unicode=request.unicode,
                author=request.author,
            ),
        )

        self.state.reactions[request.unicode].ids.remove(request.author)

        if len(self.state.reactions[request.unicode].ids) == 0:
            del self.state.reactions[request.unicode]

        return RemoveReactionResponse()

    async def AppendReactionToUsersMessageReactions(
        self,
        context: WorkflowContext,
        request: AppendReactionToUsersMessageReactionsRequest,
    ):
        user_message_reactions = List(MessageReaction).ref(
            f'{request.user}-message-reactions')

        await user_message_reactions.Append(
            context,
            Options(idempotency_alias='user message reactions append'),
            item=MessageReaction(
                message_id=context.state_id,
                unicode=request.unicode,
                author=request.author,
            ),
        )

        return AppendReactionToUsersMessageReactionsResponse()

    async def GetReactions(
        self,
        context: ReaderContext,
        request: GetReactionsRequest,
    ):
        return GetReactionsResponse(reactions=self.state.reactions)
