# main.py
import asyncio
from config.settings import CONFIG
from core.bot import ArbitrageBot

async def main():
    bot = ArbitrageBot(CONFIG)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())