from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
    ReplyKeyboardRemove,
    BotCommand,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from handlers.start import start_private
from db import insert_group_poll, insert_group_invite


async def set_commands(app):
    commands = [
        BotCommand("start", "Start setup"),
        BotCommand("menu", "Show menu"),
        BotCommand("cancel", "Cancel current workflow or reset"),
    ]
    await app.bot.set_my_commands(commands)


async def bot_added_to_group(update, context):
    new_member = update.my_chat_member.new_chat_member.user
    if new_member.is_bot and new_member.username == context.bot.username:
        insert_group_invite(update.my_chat_member)


async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "create":
        pass
    elif text == "reschedule":
        pass
    else:
        chat_type = update.message.chat.type
        if chat_type == "private":
            await start_private(update, context)
        return
        keyboard = [["Create", "Reschedule"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        text = (
            "Hi! This bot can help you start a reading plan or send daily polls in your group.\n\n"
            "Step 1️⃣: Add me to your group\n"
            "Step 2️⃣: Promote me as an *admin*\n"
            "Step 3️⃣: Press the options below 👇"
        )
        await update.message.reply_text(text, reply_markup=reply_markup)
    return


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "schedule":
        question = "Would you schedule a Reading Plan or Poll? Select option below"
        keyboard = [["Reading Plan", "Poll"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        await query.message.reply_text(text=question, reply_markup=reply_markup)
    elif data == "plan":
        await start_plan(update, context)
    elif data == "poll":
        await start_poll(update, context)
    elif data == "reschedule":
        pass

    return


# --- States for main menu ---
CHOOSE_ACTION = range(1)

# --- States for poll setup ---
POLL_QUESTION, POLL_OPTION = range(2)

# --- States for reading plan setup ---
PLAN_NAME, PLAN_DURATION = range(2)

# --- States ---
ASK_POLL_QUESTION, ASK_POLL_OPTIONS, CONFIRM_POLL = range(3)
ASK_OPTIONS = range(2)


async def start_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    question = "Schedule a Reading Plan or Poll"
    keyboard = [
        [
            InlineKeyboardButton("Reading Plan", callback_data="plan"),
            InlineKeyboardButton("Poll", callback_data="poll"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(question, reply_markup=reply_markup)
    return ASK_OPTIONS


# --- Conversation: Poll Setup ---

# Step 1: Ask poll question


async def start_poll(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 What is your poll question?")
    return ASK_POLL_QUESTION


# Step 2: Receive poll question


async def receive_poll_question(update, context):
    context.user_data["poll_question"] = update.message.text
    await update.message.reply_text(
        "✅ Got it! Now send poll options separated by commas. e.g. Apple,Banana,Orange"
    )
    return ASK_POLL_OPTIONS


# Step 3: Receive poll options


async def receive_poll_options(update, context):
    options = [x.strip() for x in update.message.text.split(",")]
    context.user_data["poll_options"] = options

    question = context.user_data.get("poll_question")
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_poll"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_poll"),
        ]
    ]
    await update.message.reply_text(
        f"Here is your poll:\n\n*{question}*\nOptions: {', '.join(options)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
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

