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
    await Chatbot.idempotently().Create(context, channel_id="channel")


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
