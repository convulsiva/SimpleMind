# SimpleMind

SimpleMind is a Telegram bot that explains unfamiliar words, terms, and topics in simple language.

The bot runs on `aiogram 3` and uses the OpenAI API to generate beginner-friendly explanations. Explanation modes, inline buttons, Docker deployment, and advanced logging will be added in later stages.

## Features

* `/start` command with a short bot introduction
* `/help` command with example requests
* Plain text message handling
* AI-generated explanations through OpenAI API
* Environment-based configuration through `.env`

## Project Structure

```text
bot/
  handlers/
    commands.py
    messages.py
  keyboards/
  services/
    explainer.py
  config.py
  main.py
```

## Requirements

* Python 3.11+
* Telegram bot token from [@BotFather](https://t.me/BotFather)

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the example file:

```bash
copy .env.example .env
```

Set your Telegram token in `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Run the bot:

```bash
python -m bot.main
```

## Example Requests

* `TCP/IP`
* `ковариация`
* `уравнение Матье`
* `Docker`
* `что такое API`
* `React hooks`

## Roadmap

* Add AI explanation service
* Add explanation modes
* Add inline action buttons
* Add Docker deployment
* Add structured logging
* Add GitHub workflow
