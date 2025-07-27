from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text('Hello world!')

def main():
    app = Application.builder().token('TOKEN').build()
    app.add_handler(CommandHandler('start', start))
    app.run_polling()

if __name__ == '__main__':
    main()
