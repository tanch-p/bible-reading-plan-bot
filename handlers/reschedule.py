from telegram import Update
from telegram.ext import (
    ConversationHandler, MessageHandler, filters, ContextTypes
)

PLAN_NAME, PLAN_DURATION = range(2)

async def start_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter reading plan name:")
    return PLAN_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plan_name"] = update.message.text
    await update.message.reply_text("How many days will it last?")
    return PLAN_DURATION

async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["plan_name"]
    duration = update.message.text
    await update.message.reply_text(f"📖 Reading plan '{name}' set for {duration} days.")
    return ConversationHandler.END


def get_reschedule_conversation_handler():
    """Return a ConversationHandler for rescheduling plans."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("(?i)^reschedule an item$"), start_plan)],
        states={
            PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PLAN_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_duration)],
        },
        fallbacks=[],
        name="reading_plan_conversation",
    )
