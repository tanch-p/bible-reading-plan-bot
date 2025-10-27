from telegram import Update
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes

POLL_QUESTION, POLL_OPTION, POLL_TIMING, POLL_START_DATE, POLL_END_DATE, POLL_FREQUENCY, CONFIRM = range(7)


async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your poll question:")
    return POLL_QUESTION  # Returns 0, moving to POLL_QUESTION state


async def get_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["poll_question"] = update.message.text
    await update.message.reply_text("Now enter the options (comma-separated):")
    return POLL_OPTION 


async def get_timing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["poll_timing"] = update.message.text
    await update.message.reply_text("Enter time (GMT+8) to send the poll: e.g. 12:00, 10:00am")
    return POLL_START_DATE

async def get_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["poll_start_date"] = update.message.text
    await update.message.reply_text("Enter start date: e.g. 31 August")
    return POLL_START_DATE


async def get_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = context.user_data["poll_question"]
    options = [opt.strip() for opt in update.message.text.split(",")]
    await update.message.reply_text(
        f"✅ Poll created!\n\n*{question}*\nOptions: {', '.join(options)}",
        parse_mode="Markdown",
    )
    return POLL_TIMING


async def confirm_options(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_poll":
        chat_id = query.message.chat.id
        add_group_poll(chat_id)
        await query.edit_message_text("✅ Poll setup complete! It will now run daily.")
    else:
        await query.edit_message_text("❌ Poll setup canceled.")

    context.user_data.clear()
    return ConversationHandler.END


def get_poll_conversation_handler():
    """Return a ConversationHandler for setting up a poll."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("(?i)^setup poll$"), start_poll)],
        states={
            POLL_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)
            ],
            POLL_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_options)],
            POLL_TIMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_options)],
            POLL_START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_options)],
        },
        fallbacks=[],
        name="poll_conversation",
    )
