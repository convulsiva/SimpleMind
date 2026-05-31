import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.config import get_settings
from bot.keyboards.explanation import (
    ACTION_PREFIX,
    MODE_PREFIX,
    explanation_actions_keyboard,
)
from bot.services.explainer import AIServiceError, explain_term
from bot.services.telegram_formatting import to_telegram_html
from bot.services.user_context import get_user_term


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith(MODE_PREFIX))
async def handle_mode_callback(callback: CallbackQuery) -> None:
    mode = callback.data.removeprefix(MODE_PREFIX) if callback.data else "beginner"
    await _answer_with_explanation(callback, mode=mode)


@router.callback_query(F.data.startswith(ACTION_PREFIX))
async def handle_action_callback(callback: CallbackQuery) -> None:
    action = callback.data.removeprefix(ACTION_PREFIX) if callback.data else "simpler"
    await _answer_with_explanation(callback, action=action)


async def _answer_with_explanation(
    callback: CallbackQuery,
    mode: str = "beginner",
    action: str | None = None,
) -> None:
    user_id = callback.from_user.id
    term = get_user_term(user_id)

    if not term:
        logger.info("Callback without saved term from user_id=%s", user_id)
        await callback.answer("Сначала отправь слово или тему.", show_alert=True)
        return

    logger.info(
        "Received explanation callback from user_id=%s mode=%s action=%s",
        user_id,
        mode,
        action,
    )
    await callback.answer("Готовлю ответ...")

    try:
        explanation = await explain_term(term, get_settings(), mode=mode, action=action)
    except AIServiceError as error:
        logger.warning("AI callback explanation failed for user_id=%s: %s", user_id, error)
        await _send_or_edit(callback.message, str(error))
        return

    await _send_or_edit(callback.message, explanation, with_keyboard=True)


async def _send_or_edit(
    message: Message | None,
    text: str,
    with_keyboard: bool = False,
) -> None:
    if not message:
        return

    reply_markup = explanation_actions_keyboard() if with_keyboard else None
    await message.answer(
        to_telegram_html(text),
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
