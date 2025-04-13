import asyncio
from database import init_db

async def on_startup(dp):
    await init_db()
