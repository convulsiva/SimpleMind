from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Привет! Я SimpleMind, бот для простых объяснений.\n\n"
        "Отправь мне слово, термин или тему, а я объясню их понятным языком. "
        "После ответа можно выбрать режим или попросить пример кнопками."
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Можно отправить любой термин, тему или вопрос.\n\n"
        "Примеры:\n"
        "- TCP/IP\n"
        "- ковариация\n"
        "- уравнение Матье\n"
        "- Docker\n"
        "- что такое API\n"
        "- React hooks\n\n"
        "После объяснения можно нажать кнопки: объяснить проще, дать пример, "
        "сделать короче или задать вопрос для проверки."
    )
