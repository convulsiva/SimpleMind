import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import get_settings
from bot.handlers import callbacks, commands, messages
from bot.logging_config import setup_logging


logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting SimpleMind bot")

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()

    dispatcher.include_router(commands.router)
    dispatcher.include_router(messages.router)
    dispatcher.include_router(callbacks.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
