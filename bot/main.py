import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers import commands, messages


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()

    dispatcher.include_router(commands.router)
    dispatcher.include_router(messages.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
