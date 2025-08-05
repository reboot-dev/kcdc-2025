from channel_servicer import ChannelServicer
from user_servicer import UserServicer
from message_servicer import MessageServicer
from reboot.std.collections.sorted_map import sorted_map


async def initialize(context: ExternalContext):
    pass


async def main():
    await Application(
        servicers=[
            ChannelServicer,
            UserServicer,
            MessageServicer,
        ] + sorted_map.servicers(),
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
