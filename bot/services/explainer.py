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
    if not settings.groq_api_key:
        raise AIServiceError(
            "Groq API пока не настроен. Добавь GROQ_API_KEY в .env и перезапусти бота."
        )

    instruction = _build_instruction(mode, action)
    payload = {
        "model": settings.groq_model,
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
        response_data = await _send_groq_request(settings, payload)
    except httpx.TimeoutException as error:
        logger.warning("Groq API request timed out")
        raise AIServiceError("Groq не успел ответить. Попробуй еще раз чуть позже.") from error
    except httpx.HTTPStatusError as error:
        api_message = _extract_error_message(error.response)

        if error.response.status_code == 429:
            retry_after = error.response.headers.get("Retry-After")
            wait_text = f" Подожди примерно {retry_after} сек. и попробуй снова." if retry_after else ""
            detail_text = f" Детали API: {api_message}" if api_message else ""
            logger.warning("Groq API rate limit exceeded: %s", api_message or "no details")
            raise AIServiceError(
                "Groq ограничил частоту запросов или бесплатную квоту."
                f"{wait_text}{detail_text}"
            ) from error

        if error.response.status_code in {401, 403}:
            logger.warning("Groq API authentication or permission error: %s", api_message)
            raise AIServiceError(
                "Groq API не принял ключ или доступ запрещен. Проверь GROQ_API_KEY."
            ) from error

        if error.response.status_code == 404:
            logger.warning("Groq model was not found: %s", api_message)
            raise AIServiceError(
                "Groq не нашел выбранную модель. Проверь значение GROQ_MODEL в .env."
            ) from error

        logger.exception("Groq API returned status %s: %s", error.response.status_code, api_message)
        raise AIServiceError(
            "Не получилось получить ответ от Groq. Попробуй еще раз чуть позже."
        ) from error
    except httpx.RequestError as error:
        logger.exception("Groq API request failed: %s", error.__class__.__name__)
        raise AIServiceError(
            "Не получилось подключиться к Groq API. Попробуй еще раз чуть позже."
        ) from error

    explanation = _extract_message_content(response_data)
    if not explanation:
        logger.warning("Groq API returned an empty explanation")
        raise AIServiceError("Groq вернул пустой ответ. Попробуй переформулировать запрос.")

    return explanation.strip()


async def _send_groq_request(
    settings: Settings,
    payload: dict[str, Any],
) -> dict[str, Any]:
    url = f"{settings.groq_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.groq_timeout) as client:
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


def _extract_error_message(response: httpx.Response) -> str | None:
    try:
        error_data = response.json()
    except ValueError:
        return None

    error = error_data.get("error")
    if not isinstance(error, dict):
        return None

    message = error.get("message")
    return message if isinstance(message, str) else None


def _build_instruction(
    mode: ExplanationMode,
    action: ExplanationAction | None,
) -> str:
    if action:
        return ACTION_INSTRUCTIONS.get(action, ACTION_INSTRUCTIONS["simpler"])

    return MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["beginner"])
