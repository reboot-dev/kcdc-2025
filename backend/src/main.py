import asyncio
from reboot.aio.applications import Application
from reboot.std.presence.v1 import presence
from servicers.user import UserServicer, UsersServicer


async def main():

    await Application(
        servicers=[
            UserServicer,
            UsersServicer,
        ] + presence.servicers(),
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
