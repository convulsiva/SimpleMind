import logging

from aiogram import F, Router
from aiogram.types import Message

from bot.config import get_settings
from bot.keyboards.explanation import explanation_actions_keyboard
from bot.services.explainer import AIServiceError, explain_term
from bot.services.user_context import save_user_term


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    term = message.text.strip()

    if not term:
        await message.answer("Отправь слово или тему, которую нужно объяснить.")
        return

    user_id = message.from_user.id if message.from_user else message.chat.id
    save_user_term(user_id, term)
    logger.info("Received explanation request from user_id=%s", user_id)

    processing_message = await message.answer("Думаю над объяснением...")

    try:
        explanation = await explain_term(term, get_settings())
    except AIServiceError as error:
        logger.warning("AI explanation failed for user_id=%s: %s", user_id, error)
        await processing_message.edit_text(str(error))
        return

    await processing_message.delete()
    await message.answer(explanation, reply_markup=explanation_actions_keyboard())
