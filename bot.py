from dotenv import load_dotenv
import os
import asyncio
import logging

from db.db import init_db
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from filters.conversation import get_filter_conversation_handler
from data.static import MAIN_MENU
from filters.logic import init_filter
from filters.search import search_and_send

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу тебе найти подходящую квартиру. Что хочешь сделать?",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⚙️ Настроить фильтр":
        return await init_filter(update, context)
    elif text == "❓ Помощь":
        await update.message.reply_text("Напиши /filter чтобы начать настройку фильтра вручную.")
    else:
        await update.message.reply_text("Выбери один из вариантов меню.")


async def show_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    f = context.user_data.get("filter")
    if not f:
        await update.message.reply_text("Фильтр не настроен. Используй /filter, чтобы начать.")
        return
    lines = [f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in f.items() if value is not None]
    await update.message.reply_text("Текущий фильтр: \n" + "\n".join(lines))


def main():
    init_db_sync = asyncio.get_event_loop().run_until_complete(init_db())

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('showfilter', show_filter))
    app.add_handler(CommandHandler('search', search_and_send))
    app.add_handler(get_filter_conversation_handler())
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection))

    print("✅ Бот запущен")
    app.run_polling()



if __name__ == '__main__':
    main()
