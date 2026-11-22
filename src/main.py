# Entry point for the browser build (pygbag looks for a main.py next to the code).
# Desktop players use `uv run spaceshooter` instead.
import asyncio

# pygbag only scans this file's imports to decide which packages to load in the
# browser: without this explicit import, pygame stays an empty stub.
import pygame  # noqa: F401

from spaceshooter.app import App


async def main() -> None:
    await App().run()


asyncio.run(main())
