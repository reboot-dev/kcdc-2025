import asyncio
import json
from chat.v1.channel_rbt import Channel
from chat.v1.message_rbt import Details, Message
from chatbot.v1.chatbot_rbt import (
    Chatbot,
    CreateRequest,
    CreateResponse,
    ControlLoopRequest,
    ControlLoopResponse,
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
from value import as_string

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


class ChatbotServicer(Chatbot.alpha.Servicer):

    async def Create(
        self,
        context: TransactionContext,
        request: CreateRequest,
    ) -> CreateResponse:
        # Schedule our control loop.
        await self.ref().schedule().ControlLoop(
            context, channel_id=request.channel_id
        )

        return CreateResponse()

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

            system = ("You are a chatbot who reads messages and if the messages "
                      "appear to be making any factual claims then you fact check "
                      "the claims and respond whether or not you believe the "
                      "claims are true or false. If the messages are not making "
                      "any factual claims, just return with an empty JSON '{}'. "
                      "If the factual claims are true, then "
                      "you respond with the JSON '{ fact: true }', otherwise if "
                      "the messages are false you respond with the JSON "
                      "{ fact: false, reason: '...' } where the 'reason' property "
                      "contains text of the reason you believe the statements to be "
                      "false. Always start the 'reason' with something that "
                      "first explains which factual claim you are referring to, "
                      "directly including the author and the text or at least "
                      "a snippet of the text.")

            llm_messages = [
                {
                    "role": "system",
                    "content": system
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
                    await channel.Post(
                        context,
                        author="bot",
                        text=result["reason"],
                    )
            except:
                import traceback
                traceback.print_exc()
                continue
