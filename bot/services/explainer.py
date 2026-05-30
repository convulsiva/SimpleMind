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
    if not settings.gemini_api_key:
        raise AIServiceError(
            "Gemini API пока не настроен. Добавь GEMINI_API_KEY в .env и перезапусти бота."
        )

    instruction = _build_instruction(mode, action)
    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Ты объясняешь сложные слова, термины и темы простым языком. "
                        "Отвечай по-русски, дружелюбно и понятно для новичка. "
                        "Не используй длинные вступления."
                    )
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Объясни простыми словами тему: {term}\n\n"
                            f"Режим: {instruction}\n\n"
                            "Сохраняй ответ понятным, структурированным и полезным."
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
        },
    }

    try:
        response_data = await _send_gemini_request(settings, payload)
    except httpx.TimeoutException as error:
        logger.warning("Gemini API request timed out")
        raise AIServiceError("Gemini не успел ответить. Попробуй еще раз чуть позже.") from error
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 429:
            retry_after = error.response.headers.get("Retry-After")
            wait_text = f" Подожди примерно {retry_after} сек. и попробуй снова." if retry_after else ""
            logger.warning("Gemini API rate limit exceeded")
            raise AIServiceError(
                "Gemini ограничил частоту запросов или бесплатную квоту."
                f"{wait_text} Попробуй позже или выбери другую Gemini-модель."
            ) from error

        if error.response.status_code in {401, 403}:
            logger.warning("Gemini API authentication or permission error")
            raise AIServiceError(
                "Gemini API не принял ключ или доступ запрещен. "
                "Проверь GEMINI_API_KEY и доступность модели для аккаунта."
            ) from error

        if error.response.status_code == 404:
            logger.warning("Gemini model was not found")
            raise AIServiceError(
                "Gemini не нашел выбранную модель. Проверь значение GEMINI_MODEL в .env."
            ) from error

        logger.exception("Gemini API returned status %s", error.response.status_code)
        raise AIServiceError(
            "Не получилось получить ответ от Gemini. Попробуй еще раз чуть позже."
        ) from error
    except httpx.RequestError as error:
        logger.exception("Gemini API request failed: %s", error.__class__.__name__)
        raise AIServiceError(
            "Не получилось подключиться к Gemini API. Попробуй еще раз чуть позже."
        ) from error

    explanation = _extract_message_content(response_data)
    if not explanation:
        logger.warning("Gemini API returned an empty explanation")
        raise AIServiceError("Gemini вернул пустой ответ. Попробуй переформулировать запрос.")

    return explanation.strip()


async def _send_gemini_request(
    settings: Settings,
    payload: dict[str, Any],
) -> dict[str, Any]:
    base_url = settings.gemini_base_url.rstrip("/")
    url = f"{base_url}/models/{settings.gemini_model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.gemini_api_key,
    }

    async with httpx.AsyncClient(timeout=settings.gemini_timeout) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


def _extract_message_content(response_data: dict[str, Any]) -> str | None:
    candidates = response_data.get("candidates")
    if not candidates:
        return None

    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        return None

    content = first_candidate.get("content")
    if not isinstance(content, dict):
        return None

    parts = content.get("parts")
    if not parts:
        return None

    text_parts = [
        part.get("text")
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    ]
    return "\n".join(text_parts) if text_parts else None


def _build_instruction(
    mode: ExplanationMode,
    action: ExplanationAction | None,
) -> str:
    if action:
        return ACTION_INSTRUCTIONS.get(action, ACTION_INSTRUCTIONS["simpler"])

    return MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["beginner"])
