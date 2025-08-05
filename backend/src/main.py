import asyncio
from reboot.aio.applications import Application
from channel_servicer import ChannelServicer
from user_servicer import UserServicer
from message_servicer import MessageServicer
from reboot.std.collections import sorted_map


async def main():
    await Application(
        servicers=[
            ChannelServicer,
            UserServicer,
            MessageServicer,
        ] + sorted_map.servicers(),
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
