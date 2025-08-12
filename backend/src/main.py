import asyncio
from reboot.aio.applications import Application
from servicers.user import UserServicer, UsersServicer


async def main():

    await Application(
        servicers=[
            UserServicer,
            UsersServicer,
        ],
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
