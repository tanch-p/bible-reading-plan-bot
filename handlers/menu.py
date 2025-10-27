from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, ContextTypes
from .poll import get_poll_conversation_handler
from .reading_plan import get_reading_plan_conversation_handler
from .reschedule import get_reschedule_conversation_handler

CHOOSE_ACTION = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Setup Poll", "Setup Reading Plan"], ["Reschedule an item"]]
    await update.message.reply_text(
        "What would you want to do?\n Pick an option below",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CHOOSE_ACTION


def get_menu_conversation_handler():
    """Main menu conversation that includes sub-conversations."""
    return ConversationHandler(
        entry_points=[CommandHandler("menu", start)],
        states={
            CHOOSE_ACTION: [
                get_poll_conversation_handler(),
                get_reading_plan_conversation_handler(),
                get_reschedule_conversation_handler(),
            ],
        },
        fallbacks=[],
        name="menu_conversation",
    )
