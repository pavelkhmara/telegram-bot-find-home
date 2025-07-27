from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from filters.logic import (
    init_filter,
    handle_city,
    handle_price,
    handle_rooms,
    handle_type,
    handle_furnished,
    handle_pets,
    handle_area,
    cancel
)

G_CITY, G_PRICE, G_ROOMS, G_TYPE, G_FURNISHED, G_PETS, G_AREA = range(7)

def get_filter_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("filter", init_filter)],
        states={
            G_CITY: [CallbackQueryHandler(handle_city)],
            G_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price)],
            G_ROOMS: [CallbackQueryHandler(handle_rooms)],
            G_TYPE: [CallbackQueryHandler(handle_type)],
            G_FURNISHED: [CallbackQueryHandler(handle_furnished)],
            G_PETS: [CallbackQueryHandler(handle_pets)],
            G_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_area)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
