import asyncio
from chat.v1.channel_rbt import Channel
from reboot.aio.applications import Application
from reboot.std.index.v1 import index
from reboot.std.presence.v1 import presence
from servicers.channel import ChannelServicer
from servicers.message import MessageServicer
from servicers.user import UserServicer, UsersServicer


async def initialize(context):
    await Channel.Create(context, "channel")


async def main():

    await Application(
        servicers=[
            ChannelServicer,
            UserServicer,
            UsersServicer,
            MessageServicer,
        ] + index.servicers() + presence.servicers(),
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
