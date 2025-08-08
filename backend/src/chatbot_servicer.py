import asyncio
import json
from chat.v1.channel_rbt import Channel
from chat.v1.message_rbt import Details, Message
from chatbot.v1.chatbot_rbt import (
    ApproveRequest,
    ApproveResponse,
    Chatbot,
    CreateRequest,
    CreateResponse,
    ControlLoopRequest,
    ControlLoopResponse,
    ListPostsForApprovalRequest,
    ListPostsForApprovalResponse,
)
from google.protobuf.json_format import MessageToDict
from langchain.chat_models import init_chat_model
from langchain_core.messages.ai import AIMessage
from pubsub.v1.pubsub_rbt import PubSub
from queues.v1.queue_rbt import Queue
from reboot.aio.contexts import (
    ReaderContext,
    TransactionContext,
    WorkflowContext,
)
from reboot.aio.workflows import at_most_once
from uuid import uuid4
from value import as_string

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


class ChatbotServicer(Chatbot.alpha.Servicer):

    async def Create(
        self,
        context: TransactionContext,
        request: CreateRequest,
    ) -> CreateResponse:
        self.state.channel_id = request.channel_id

        # Schedule our control loop.
        await self.ref().schedule().ControlLoop(
            context,
            name=request.name,
            channel_id=request.channel_id,
            prompt=request.prompt,
            human_in_the_loop=request.human_in_the_loop,
        )

        return CreateResponse()

    async def ListPostsForApproval(
        self,
        context: ReaderContext,
        request: ListPostsForApprovalRequest,
    ) -> ListPostsForApprovalResponse:
        return ListPostsForApprovalResponse(
            posts=self.state.posts_for_approval,
        )

    async def Approve(
        self,
        context: TransactionContext,
        request: ApproveRequest,
    ) -> ApproveResponse:
        for i in range(len(self.state.posts_for_approval)):
            post = self.state.posts_for_approval[i]
            if post.id == request.id:
                channel = Channel.ref(self.state.channel_id)
                await channel.Post(context, author=post.author, text=post.text)
                del self.state.state.posts_for_approval[i]
                break

        # TODO: return an error if the post was never found?

        return ApproveResponse()

    async def ControlLoop(
        self,
        context: WorkflowContext,
        request: ControlLoopRequest,
    ):
        channel = Channel.ref(request.channel_id)

        pub_sub = PubSub.ref(f"{request.channel_id}-pub-sub")

        queue = Queue.ref(f"{context.state_id}-messages-queue")

        await pub_sub.Subscribe(
            context,
            topic="messages",
            queue_id=queue.state_id,
        )

        async for iteration in context.loop("Control loop"):

            dequeue = await queue.Dequeue(context, bulk=True)

            # responses = await Message.forall(
            #     [as_string(item.value) for item in dequeue.items]
            # ).Get(context)

            responses = await asyncio.gather(
                *[
                    Message.ref(as_string(item.value)).GetDetails(context)
                    # Expecting the message ID as a string.
                    for item in dequeue.items
                ]
            )

            messages = [response.details for response in responses]

            # Filter out messages from us.
            #
            # TODO: do we get better results if we include the bot
            # messages when we call the model?
            messages = [
                message for message in messages if message.author != "bot"
            ]

            # Check if there are any messages excluding those from us.
            if len(messages) == 0:
                continue

            llm_messages = [
                {
                    "role": "system",
                    "content": request.prompt,
                },
                {
                    "role": "user",
                    "content": "Here are the latest messages in JSON: "
                    f"{json.dumps([MessageToDict(message) for message in messages], indent=2)}"
                }
            ]

            async def generate() -> AIMessage:
                return await llm.ainvoke(llm_messages)

            try:
                message = await at_most_once(
                    "Generate", context, generate, type=AIMessage
                )
                print(f"CHATBOT: LLM generated {message}")

                result = json.loads(message.content)

                if len(result) == 0:
                    continue

                if "fact" in result and not result["fact"]:
                    text = result["reason"]

                    if request.human_in_the_loop:

                        async def add_post_for_approval(state):
                            state.posts_for_approval.append(
                                Post(
                                    id=uuid4(),
                                    author=request.name,
                                    text=text,
                                ),
                            )

                        await self.ref().Write(context, add_post_for_approval)
                    else:
                        await channel.Post(
                            context,
                            author=request.name,
                            text=text,
                        )
            except:
                import traceback
                traceback.print_exc()
                continue
