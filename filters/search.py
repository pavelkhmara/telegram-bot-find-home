from scrapers.olx import fetch_olx_offers
from telegram import Update
from telegram.ext import ContextTypes

async def search_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from db.db import load_filter
    filter_data = await load_filter(user_id)

    if not filter_data:
        await update.message.reply_text("Сначала нужно настроить фильтр.")
        return

    await update.message.reply_text("Ищу подходящие объявления на OLX...")
    offers = await fetch_olx_offers(filter_data)

    if not offers:
        await update.message.reply_text("Не нашлось подходящих объявлений.")
        return

    for offer in offers:
        text = f"📌 <b>{offer['title']}</b>\n💰 {offer['price']}\n🔗 <a href='{offer['url']}'>Смотреть</a>"
        await update.message.reply_html(text)
