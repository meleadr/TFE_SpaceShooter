import asyncio

from spaceshooter.app import App


def main() -> None:
    asyncio.run(App().run())


if __name__ == "__main__":
    main()
