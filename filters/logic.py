from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from data.static import CITIES, PROPERTY_TYPES, ROOM_OPTIONS, YES_NO_SKIP
from db.db import save_filter, load_filter

G_CITY, G_PRICE, G_ROOMS, G_TYPE, G_FURNISHED, G_PETS, G_AREA = range(7)

async def init_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['filter'] = {}
    keyboard = [[InlineKeyboardButton(city, callback_data=city) for city in row] for row in CITIES]
    await update.message.reply_text("Выбери город:", reply_markup=InlineKeyboardMarkup(keyboard))
    return G_CITY

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['filter']['city'] = query.data
    await query.edit_message_text("Укажи цену в формате 2000-3000")
    return G_PRICE

async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        p_from, p_to = map(int, update.message.text.split("-"))
        context.user_data['filter']['price_from'] = p_from
        context.user_data['filter']['price_to'] = p_to
    except:
        await update.message.reply_text("Неверный формат. Введи, например: 2000-3000")
        return G_PRICE
    keyboard = [[InlineKeyboardButton(room, callback_data=room) for room in row] for row in ROOM_OPTIONS]
    await update.message.reply_text("Сколько комнат?", reply_markup=InlineKeyboardMarkup(keyboard))
    return G_ROOMS

async def handle_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['filter']['rooms'] = query.data
    keyboard = [[InlineKeyboardButton(ptype, callback_data=ptype) for ptype in row] for row in PROPERTY_TYPES]
    await query.edit_message_text("Тип недвижимости:", reply_markup=InlineKeyboardMarkup(keyboard))
    return G_TYPE

async def handle_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['filter']['type'] = query.data
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in row] for row in YES_NO_SKIP]
    await query.edit_message_text("Меблировка:", reply_markup=InlineKeyboardMarkup(keyboard))
    return G_FURNISHED

async def handle_furnished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    value = query.data
    context.user_data['filter']['furnished'] = None if value == "Пропустить" else value
    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in row] for row in YES_NO_SKIP]
    await query.edit_message_text("Можно с животными:", reply_markup=InlineKeyboardMarkup(keyboard))
    return G_PETS

async def handle_pets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    value = query.data
    context.user_data['filter']['pets_allowed'] = None if value == "Пропустить" else value
    await query.edit_message_text("Укажи метраж в формате 30-70 или напиши 'Пропустить'")
    return G_AREA

async def handle_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.lower() == "пропустить":
        context.user_data['filter']['area_from'] = None
        context.user_data['filter']['area_to'] = None
    else:
        try:
            a_from, a_to = map(int, text.split("-"))
            context.user_data['filter']['area_from'] = a_from
            context.user_data['filter']['area_to'] = a_to
        except:
            await update.message.reply_text("Неверный формат. Введи, например: 30-70")
            return G_AREA

    result = context.user_data['filter']
    user_id = update.effective_user.id
    filter_data = context.user_data.get("filter", {})

    await save_filter(user_id, filter_data)

    await update.message.reply_text(f"Фильтр сохранён ✅\n{result}", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def show_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    filter_data = await load_filter(user_id)

    if not filter_data:
        await update.message.reply_text("Фильтр не настроен. Используй /filter, чтобы начать.")
        return

    lines = [f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in filter_data.items() if v is not None]
    await update.message.reply_text("Текущий фильтр: \n" + "\n".join(lines))