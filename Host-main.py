import asyncio

from icons_utils import update_icon


async def MainLoop():
    while True:
        update_icon()
        await asyncio.sleep(300)


if __name__ == '__main__':
    try:
        asyncio.run(MainLoop())
    except KeyboardInterrupt:
        pass