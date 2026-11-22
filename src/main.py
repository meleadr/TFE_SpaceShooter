# Entry point for the browser build (pygbag looks for a main.py next to the code).
# Desktop players use `uv run spaceshooter` instead.
import asyncio

from spaceshooter.app import App


async def main() -> None:
    await App().run()


asyncio.run(main())
