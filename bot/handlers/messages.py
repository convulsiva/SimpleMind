from aiogram import F, Router
from aiogram.types import Message

from bot.services.explainer import explain_term_mock


router = Router()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    term = message.text.strip()

    if not term:
        await message.answer("Отправь слово или тему, которую нужно объяснить.")
        return

    explanation = await explain_term_mock(term)
    await message.answer(explanation)
