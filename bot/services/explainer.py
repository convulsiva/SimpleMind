import logging
from typing import Any

import httpx

from bot.config import Settings


logger = logging.getLogger(__name__)

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
    if not settings.openrouter_api_key:
        raise AIServiceError(
            "Qwen через OpenRouter пока не настроен. "
            "Добавь OPENROUTER_API_KEY в .env и перезапусти бота."
        )

    instruction = _build_instruction(mode, action)
    payload = {
        "model": settings.openrouter_model,
        "messages": [
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
        "temperature": 0.4,
    }

    try:
        response_data = await _send_openrouter_request(settings, payload)
    except httpx.TimeoutException as error:
        logger.warning("OpenRouter request timed out")
        raise AIServiceError(
            "Qwen не успел ответить. Попробуй еще раз чуть позже."
        ) from error
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 402:
            logger.warning("OpenRouter API requires payment or free quota is exhausted")
            raise AIServiceError(
                "OpenRouter вернул 402 Payment Required. "
                "Проверь, не закончился ли бесплатный лимит, не стоит ли credit limit "
                "на API key и доступна ли выбранная free-модель для твоего аккаунта."
            ) from error

        logger.exception(
            "OpenRouter API returned status %s",
            error.response.status_code,
        )
        raise AIServiceError(
            "Не получилось получить ответ от Qwen через OpenRouter. "
            "Проверь API key или попробуй позже."
        ) from error
    except httpx.RequestError as error:
        logger.exception("OpenRouter API request failed: %s", error.__class__.__name__)
        raise AIServiceError(
            "Не получилось подключиться к OpenRouter. Попробуй еще раз чуть позже."
        ) from error

    explanation = _extract_message_content(response_data)
    if not explanation:
        logger.warning("OpenRouter API returned an empty explanation")
        raise AIServiceError("Qwen вернул пустой ответ. Попробуй переформулировать запрос.")

    return explanation.strip()


async def _send_openrouter_request(
    settings: Settings,
    payload: dict[str, Any],
) -> dict[str, Any]:
    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.openrouter_timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


def _extract_message_content(response_data: dict[str, Any]) -> str | None:
    choices = response_data.get("choices")
    if not choices:
        return None

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return None

    message = first_choice.get("message")
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    return content if isinstance(content, str) else None


def _build_instruction(
    mode: ExplanationMode,
    action: ExplanationAction | None,
) -> str:
    if action:
        return ACTION_INSTRUCTIONS.get(action, ACTION_INSTRUCTIONS["simpler"])

    return MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["beginner"])
