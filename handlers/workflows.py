from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BotCommand, Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

from db import add_group_poll

# --- States ---
ASK_POLL_QUESTION, ASK_POLL_OPTIONS, CONFIRM_POLL = range(3)
ASK_OPTIONS = range(2)


async def start_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    question = "Schedule a Reading Plan or Poll"
    keyboard = [
        [
            InlineKeyboardButton("Reading Plan", callback_data="plan"),
            InlineKeyboardButton("Poll", callback_data="poll")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)
    return ASK_OPTIONS


async def schedule_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the press of 'Option 1' button."""
    query = update.callback_query
    await query.answer()  # Always answer the callback query

    # Logic for Option 1... maybe ask another question
    await query.edit_message_text("You chose Option 1. Now select another action.")

    # You could return a new state here, or the same state with a new keyboard.
    return CHOOSE_OPTION  # Assume a new state where they can choose again


async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the press of 'Option 1' button."""
    query = update.callback_query
    await query.answer()  # Always answer the callback query

    # Logic for Option 1... maybe ask another question
    await query.edit_message_text("You chose Option 1. Now select another action.")

    # You could return a new state here, or the same state with a new keyboard.
    return CHOOSE_OPTION  # Assume a new state where they can choose again

# --- Conversation: Poll Setup ---

# Step 1: Ask poll question


async def ask_poll_question(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 What is your poll question?")
    return ASK_POLL_QUESTION

# Step 2: Receive poll question


async def receive_poll_question(update, context):
    context.user_data["poll_question"] = update.message.text
    await update.message.reply_text("✅ Got it! Now send poll options separated by commas. e.g. Apple,Banana,Orange")
    return ASK_POLL_OPTIONS

# Step 3: Receive poll options


async def receive_poll_options(update, context):
    options = [x.strip() for x in update.message.text.split(",")]
    context.user_data["poll_options"] = options

    question = context.user_data.get("poll_question")
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_poll"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_poll")
        ]
    ]
    await update.message.reply_text(
        f"Here is your poll:\n\n*{question}*\nOptions: {', '.join(options)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CONFIRM_POLL

# Step 4: Confirm or cancel


async def confirm_poll(update, context):
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

# Optional fallback


async def cancel(update, context):
    await update.message.reply_text("Poll setup canceled.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

new_plan_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("schedule", start_schedule)],
    states={
        ASK_OPTIONS: [
            # Use CallbackQueryHandler for inline button presses
            CallbackQueryHandler(
                schedule_plan, pattern="^" + str(ONE) + "$"),
            # You can add more handlers for other buttons here
            CallbackQueryHandler(
                option_finish, pattern="^" + str(THREE) + "$"),
        ],
        CHOOSE_OPTION: [
            # Handlers for the next state's buttons
            # ...
        ]
    },
    # Fallback to restart the convo
    fallbacks=[CommandHandler("start", start)],
)

new_poll_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        ask_poll_question, pattern="start_poll")],
    states={
        ASK_POLL_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_poll_question)],
        ASK_POLL_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_poll_options)],
        CONFIRM_POLL: [CallbackQueryHandler(
            confirm_poll, pattern="^(confirm_poll|cancel_poll)$")]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
