from aiogram import F, Router
from aiogram.types import Message

from bot.config import get_settings
from bot.services.explainer import AIServiceError, explain_term


router = Router()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    term = message.text.strip()

    if not term:
        await message.answer("Отправь слово или тему, которую нужно объяснить.")
        return

    processing_message = await message.answer("Думаю над объяснением...")

    try:
        explanation = await explain_term(term, get_settings())
    except AIServiceError as error:
        await processing_message.edit_text(str(error))
        return

    await processing_message.delete()
    await message.answer(explanation)
