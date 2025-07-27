from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text('Hello world!')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.run_polling()

if __name__ == '__main__':
    main()
