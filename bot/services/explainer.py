from openai import APIError, AsyncOpenAI

from bot.config import Settings

ExplanationMode = str
ExplanationAction = str


MODE_INSTRUCTIONS = {
    "beginner": (
        "Объясни как новичку: без сложных слов, с короткими предложениями "
        "и одной простой аналогией."
    ),
    "short": "Объясни коротко: 3-5 предложений, только самое важное.",
    "detailed": (
        "Объясни подробно: дай определение, основные идеи, пример и частые ошибки."
    ),
    "example": "Объясни через практический пример из жизни или разработки.",
}

ACTION_INSTRUCTIONS = {
    "simpler": "Переформулируй еще проще, как для человека без подготовки.",
    "example": "Дай один понятный пример и коротко разбери его.",
    "shorter": "Сделай ответ короче: максимум 4 предложения.",
    "quiz": (
        "Задай один вопрос для проверки понимания. Добавь правильный ответ "
        "после строки 'Ответ:'."
    ),
}


class AIServiceError(Exception):
    """Raised when the explanation service cannot return a useful answer."""


async def explain_term(
    term: str,
    settings: Settings,
    mode: ExplanationMode = "beginner",
    action: ExplanationAction | None = None,
) -> str:
    if not settings.openai_api_key:
        raise AIServiceError(
            "AI API пока не настроен. Добавь OPENAI_API_KEY в .env и перезапусти бота."
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    instruction = _build_instruction(mode, action)

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты объясняешь сложные слова, термины и темы простым языком. "
                        "Отвечай по-русски, дружелюбно и понятно для новичка. "
                        "Не используй длинные вступления."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Объясни простыми словами тему: {term}\n\n"
                        f"Режим: {instruction}\n\n"
                        "Сохраняй ответ понятным, структурированным и полезным."
                    ),
                },
            ],
            temperature=0.4,
        )
    except APIError as error:
        raise AIServiceError(
            "Не получилось получить ответ от AI API. Попробуй еще раз чуть позже."
        ) from error

    explanation = response.choices[0].message.content
    if not explanation:
        raise AIServiceError("AI API вернул пустой ответ. Попробуй переформулировать запрос.")

    return explanation.strip()


def _build_instruction(
    mode: ExplanationMode,
    action: ExplanationAction | None,
) -> str:
    if action:
        return ACTION_INSTRUCTIONS.get(action, ACTION_INSTRUCTIONS["simpler"])

    return MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["beginner"])
