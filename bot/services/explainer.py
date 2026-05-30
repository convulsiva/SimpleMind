from openai import APIError, AsyncOpenAI

from bot.config import Settings


class AIServiceError(Exception):
    """Raised when the explanation service cannot return a useful answer."""


async def explain_term(term: str, settings: Settings) -> str:
    if not settings.openai_api_key:
        raise AIServiceError(
            "AI API пока не настроен. Добавь OPENAI_API_KEY в .env и перезапусти бота."
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key)

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
                        "Формат ответа:\n"
                        "1. Короткое объяснение.\n"
                        "2. Простая аналогия или пример.\n"
                        "3. Когда это может пригодиться."
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
