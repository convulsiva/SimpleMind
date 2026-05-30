from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


MODE_PREFIX = "mode:"
ACTION_PREFIX = "action:"


def explanation_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Как новичку", callback_data=f"{MODE_PREFIX}beginner"),
                InlineKeyboardButton(text="Коротко", callback_data=f"{MODE_PREFIX}short"),
            ],
            [
                InlineKeyboardButton(text="Подробно", callback_data=f"{MODE_PREFIX}detailed"),
                InlineKeyboardButton(text="С примером", callback_data=f"{MODE_PREFIX}example"),
            ],
            [
                InlineKeyboardButton(text="Объясни проще", callback_data=f"{ACTION_PREFIX}simpler"),
                InlineKeyboardButton(text="Дай пример", callback_data=f"{ACTION_PREFIX}example"),
            ],
            [
                InlineKeyboardButton(text="Сделай короче", callback_data=f"{ACTION_PREFIX}shorter"),
                InlineKeyboardButton(text="Вопрос для проверки", callback_data=f"{ACTION_PREFIX}quiz"),
            ],
        ]
    )
