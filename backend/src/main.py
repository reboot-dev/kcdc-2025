import asyncio
from channel_servicer import ChannelServicer
from chatbot.v1.chatbot_rbt import Chatbot
from chatbot_servicer import ChatbotServicer
from list_servicer import ListServicer
from message_servicer import MessageServicer
from pubsub_servicer import PubSubServicer
from queue_servicer import QueueServicer
from reboot.aio.applications import Application
from user_servicer import UserServicer, UsersServicer
from reboot.std.presence.v1 import presence 

async def initialize(context):
    await Chatbot.idempotently().Create(
        context,
        name="Fact Checker",
        channel_id="channel",
        prompt="You are a chatbot who reads messages and if the messages "
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
        "a snippet of the text.",
        human_in_the_loop=False,
    )


async def main():

    await Application(
        servicers=[
            ChannelServicer,
            UserServicer,
            UsersServicer,
            MessageServicer,
            ListServicer,
            ChatbotServicer,
            QueueServicer,
            PubSubServicer, 
        ] + presence.servicers(),
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
