import logging
import os
from collections import defaultdict

from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Ты полезный ассистент. Отвечай кратко и по делу, если не попросили иначе.",
)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "12"))

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY:
    raise RuntimeError("Не задан OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

chat_histories: dict[int, list[dict[str, str]]] = defaultdict(list)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветствие."""
    del context
    await update.message.reply_text(
        "Привет! Я подключен к OpenAI и могу работать как твой ChatGPT в Telegram.\n"
        "Просто отправь сообщение.\n\n"
        "Команды:\n"
        "/new — очистить историю диалога\n"
        "/model — показать текущую модель"
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сбрасывает историю конкретного чата."""
    del context
    chat_id = update.effective_chat.id
    chat_histories[chat_id].clear()
    await update.message.reply_text("История очищена. Начинаем новый диалог ✨")


async def show_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    await update.message.reply_text(f"Текущая модель: {OPENAI_MODEL}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text.strip()

    if not user_text:
        return

    history = chat_histories[chat_id]
    history.append({"role": "user", "content": user_text})

    if len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history]

    try:
        await update.message.chat.send_action(action=ChatAction.TYPING)

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
        )

        answer = response.choices[0].message.content or "Не удалось сгенерировать ответ."
        history.append({"role": "assistant", "content": answer})

        if len(history) > MAX_HISTORY_MESSAGES:
            del history[:-MAX_HISTORY_MESSAGES]

        await update.message.reply_text(answer)

    except Exception as exc:
        logger.exception("Ошибка во время запроса к OpenAI")
        await update.message.reply_text(
            "Упс, произошла ошибка при обращении к OpenAI. "
            "Проверь токены/модель и попробуй снова."
        )
        history.pop() if history and history[-1]["content"] == user_text else None
        logger.debug("Детали ошибки: %s", exc)


async def post_init(application: Application) -> None:
    bot_info = await application.bot.get_me()
    logger.info("Бот запущен: @%s", bot_info.username)


def build_app() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(CommandHandler("model", show_model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


def main() -> None:
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
