# SimpleMind

SimpleMind - Telegram-бот, который объясняет непонятные слова, термины и темы простыми словами.

Бот использует `aiogram 3` для работы с Telegram и Gemini API для генерации объяснений. В проекте есть режимы объяснения, inline-кнопки, Docker-запуск, GitHub Actions и настраиваемое логирование.

## Возможности

* Команда `/start` с кратким описанием бота.
* Команда `/help` с примерами запросов.
* Обработка обычных текстовых сообщений.
* AI-объяснения через Gemini API.
* Режимы объяснения:
  * как новичку
  * коротко
  * подробно
  * с примером
* Inline-кнопки после ответа:
  * объясни проще
  * дай пример
  * сделай короче
  * вопрос для проверки
* Запуск локально, через Docker или на VPS.

## Структура проекта

```text
bot/
  handlers/
    callbacks.py
    commands.py
    messages.py
  keyboards/
    explanation.py
  services/
    explainer.py
    user_context.py
  config.py
  logging_config.py
  main.py

.env.example
.dockerignore
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

## Что нужно для запуска

* Python 3.11 или 3.12
* Telegram bot token от [@BotFather](https://t.me/BotFather)
* Gemini API key из [Google AI Studio](https://aistudio.google.com/)
* Docker и Docker Compose, если нужен запуск в контейнере

## Gemini API Key

1. Открой [Google AI Studio](https://aistudio.google.com/).
2. Войди в Google-аккаунт.
3. Нажми `Get API key` или открой раздел API keys.
4. Создай новый API key.
5. Скопируй ключ в `.env` в переменную `GEMINI_API_KEY`.

По умолчанию проект использует модель:

```env
GEMINI_MODEL=gemini-2.0-flash
```

Для простого бота-объяснялки это хороший быстрый вариант. Если захочешь модель новее, можно попробовать `gemini-2.5-flash`, но у бесплатного тарифа могут быть другие лимиты.

## Переменные окружения

Создай `.env` из примера:

```bash
copy .env.example .env
```

Для Linux или macOS:

```bash
cp .env.example .env
```

Заполни `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
LOG_LEVEL=INFO
```

Что означает каждая переменная:

* `BOT_TOKEN` - токен Telegram-бота от BotFather.
* `GEMINI_API_KEY` - ключ Gemini API из Google AI Studio.
* `GEMINI_MODEL` - модель Gemini, которая будет генерировать объяснения.
* `LOG_LEVEL` - уровень логирования. Обычно достаточно `INFO`.

Файл `.env` нельзя коммитить в git.

## Как создать Telegram-бота

1. Открой [@BotFather](https://t.me/BotFather) в Telegram.
2. Отправь команду `/newbot`.
3. Укажи имя бота.
4. Укажи username, который заканчивается на `bot`.
5. Скопируй токен, который выдаст BotFather.
6. Вставь токен в `.env` в переменную `BOT_TOKEN`.

## Локальный запуск

Создай и активируй виртуальное окружение:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Для Linux или macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установи зависимости:

```bash
pip install -r requirements.txt
```

Запусти бота:

```bash
python -m bot.main
```

После запуска открой бота в Telegram и отправь `/start`.

## Запуск через Docker

Создай `.env` и укажи реальные токены:

```bash
copy .env.example .env
```

Собери и запусти контейнер:

```bash
docker compose up -d --build
```

Посмотреть логи:

```bash
docker compose logs -f bot
```

Перезапустить бота:

```bash
docker compose restart bot
```

Остановить бота:

```bash
docker compose down
```

## Деплой на VPS

1. Установи Docker и Docker Compose на сервер.
2. Склонируй репозиторий:

```bash
git clone https://github.com/convulsiva/SimpleMind.git
cd SimpleMind
```

3. Переключись на стабильную ветку:

```bash
git checkout main
```

4. Создай `.env`:

```bash
cp .env.example .env
nano .env
```

5. Запусти бота:

```bash
docker compose up -d --build
```

6. Проверь логи:

```bash
docker compose logs -f bot
```

Бот работает через long polling, поэтому для него не нужен домен, SSL-сертификат или webhook URL.

## Как пользоваться ботом

Запустить бота:

```text
/start
```

Показать помощь и примеры:

```text
/help
```

Отправить любую тему:

```text
TCP/IP
```

```text
ковариация
```

```text
уравнение Матье
```

```text
что такое API
```

```text
React hooks
```

После ответа можно нажать inline-кнопки, чтобы изменить формат объяснения или получить продолжение.

## Git workflow

Основные ветки:

* `main` - стабильная версия.
* `develop` - ветка разработки.
* `feature/*` - отдельные ветки для новых изменений.

Пример работы над новой задачей:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/example
```

После изменений:

```bash
git status
git add .
git commit -m "feat: describe change"
git push -u origin feature/example
```

Pull Request по фичам нужно открывать из `feature/*` в `develop`.

В `main` нужно мержить только стабильную версию через Pull Request из `develop`.

## Проверки

Базовая проверка Python-файлов:

```bash
python -m compileall bot
```

GitHub Actions запускает эту проверку для Pull Request в `develop` и `main`.

## Если что-то не работает

Если бот не отвечает:

* Проверь, что файл `.env` существует.
* Проверь, что `BOT_TOKEN` указан правильно.
* Проверь, что `GEMINI_API_KEY` указан правильно.
* Посмотри логи через `docker compose logs -f bot` или в терминале при локальном запуске.

Если команда `docker` не найдена:

* Установи Docker Desktop на Windows или Docker Engine на Linux.
* Перезапусти терминал после установки.

Если AI-ответ не приходит:

* Проверь, что Gemini API key активен.
* Проверь, что модель из `GEMINI_MODEL` доступна для аккаунта.
* Если Gemini возвращает `429 Too Many Requests`, подожди несколько минут: бесплатный тариф ограничен по частоте и дневной квоте.
* Если Gemini возвращает `401` или `403`, проверь API key и доступ к модели.
* Если Gemini возвращает `404`, проверь название модели в `GEMINI_MODEL`.
* Попробуй повторить запрос позже, если API временно недоступен.
