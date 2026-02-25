# Telegram ChatGPT Bot

Простой Telegram-бот с нуля: отправляете сообщение в Telegram — получаете ответ от OpenAI (как ChatGPT).

## Возможности

- Ответы в Telegram через OpenAI API
- Память контекста для каждого чата
- Команда `/new` для очистки истории
- Команда `/model` для просмотра текущей модели

## 1) Что нужно

- Python 3.10+
- Токен Telegram-бота от [@BotFather](https://t.me/BotFather)
- OpenAI API key

## 2) Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Настройка

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполните значения:

- `TELEGRAM_BOT_TOKEN` — токен от BotFather
- `OPENAI_API_KEY` — ваш ключ OpenAI
- `OPENAI_MODEL` — модель (например, `gpt-4o-mini`)
- `SYSTEM_PROMPT` — системная инструкция бота
- `MAX_HISTORY_MESSAGES` — сколько последних сообщений хранить в контексте

## 4) Запуск

```bash
python bot.py
```

Если всё ок, в логах увидите имя бота, после чего можно писать ему в Telegram.

## Команды

- `/start` — приветствие и подсказка
- `/new` — начать новый диалог
- `/model` — показать используемую модель

## Частые проблемы

1. **`Unauthorized` от Telegram** — неверный `TELEGRAM_BOT_TOKEN`.
2. **Ошибка OpenAI** — проверьте `OPENAI_API_KEY` и название модели.
3. **Бот молчит** — убедитесь, что процесс запущен и вы пишете именно вашему боту.

---

Если нужно — могу следующим шагом добавить:

- поддержку голосовых сообщений,
- markdown-форматирование,
- ограничения по пользователям,
- запуск через Docker/systemd,
- webhook-режим для VPS.
