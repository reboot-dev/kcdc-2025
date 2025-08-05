import asyncio
from reboot.aio.applications import Application
from channel_servicer import ChannelServicer
from user_servicer import UserServicer
from message_servicer import MessageServicer
from list_servicer import ListServicer


async def main():
    await Application(
        servicers=[
            ChannelServicer,
            UserServicer,
            MessageServicer,
            ListServicer,
        ]
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
