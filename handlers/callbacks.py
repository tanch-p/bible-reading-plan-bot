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
from db import insert_group_invite

# --- Command Setup ---


async def set_commands(app):
    commands = [
        BotCommand("start", "Start setup or show menu"),
        BotCommand("cancel", "Cancel current workflow or reset"),
    ]
    await app.bot.set_my_commands(commands)


async def start_private(update: Update, context):

    text = (
        "Hi! This bot can help you start a reading plan (only Genesis to Exodus) or send daily polls in your group.\n\n"
        "Step 1️⃣: Add me to your group\n"
        "Step 2️⃣: Promote me as an *admin*\n"
        "Step 3️⃣: Use /start in the group to starting scheduling"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown"
    )


async def start_group(update, context):
    keyboard = [
        [InlineKeyboardButton("🗳 Start Daily Poll",
                              callback_data="start_poll")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ]
    await update.message.reply_text(
        "Setup Menu:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.chat_data.get("state", "idle")
    if text == "create":
        pass
    elif text == "reschedule":
        pass
    else:
        keyboard = [["Create", "Reschedule"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True)
        text = (
            "Hi! This bot can help you start a reading plan or send daily polls in your group.\n\n"
            "Step 1️⃣: Add me to your group\n"
            "Step 2️⃣: Promote me as an *admin*\n"
            "Step 3️⃣: Press the options below 👇"
        )
        await update.message.reply_text(text, reply_markup=reply_markup)
    return
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add me to a Group",
                url="https://t.me/YourBotUsername?startgroup=true",
            )
        ]
    ]

    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )
    await update.message.reply_text("This is a response to any non-command input!\n")


async def bot_added_to_group(update, context):
    new_member = update.my_chat_member.new_chat_member.user
    if new_member.is_bot and new_member.username == context.bot.username:
        insert_group_invite(update.my_chat_member)


async def start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT group_chat_id, group_title
        FROM group_invites
        WHERE inviter_user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    record = c.fetchone()
    conn.close()

    if record:
        group_chat_id, group_title = record
        await update.message.reply_text(
            f"✅ I found your recent group:\n"
            f"Group: {group_title}\n"
            f"Chat ID: {group_chat_id}"
        )
    else:
        await update.message.reply_text("I couldn’t find any recent group you added me to.")


async def send_daily_poll(bot):
    groups = get_all_groups()
    for chat_id in groups:
        try:
            await bot.send_poll(
                chat_id=chat_id,
                question="How are you feeling today?",
                options=["😊 Good", "😐 Okay", "😞 Not great"],
                is_anonymous=False,
            )
        except Exception as e:
            print(f"Error sending poll to {chat_id}: {e}")


async def start(update, context):
    chat_type = update.message.chat.type
    if chat_type == "private":
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Add me to a Group",
                    url="https://t.me/YOUR_BOT_USERNAME?startgroup=true",
                )
            ]
        ]
        text = (
            "👋 Hi! I can send recurring polls in your group.\n\n"
            "🪜 Steps:\n"
            "1️⃣ Add me to your group\n"
            "2️⃣ Promote me as *admin*\n"
            "3️⃣ Use /start in the group to set up your poll"
        )
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

    elif chat_type in ("group", "supergroup"):
        keyboard = [
            [InlineKeyboardButton("🗳 Start Daily Poll",
                                  callback_data="start_poll")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        ]
        await update.message.reply_text(
            "Setup Menu:", reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "schedule":
        pass
    elif data == "reschedule":
        pass

    return await start_poll(update, context)  # hand off to ConversationHandler

    if query.data == "start_poll":
        chat_id = query.message.chat.id
        add_group(chat_id)
        await query.edit_message_text(
            "✅ Daily polls will now be sent to this group every morning!"
        )

    elif query.data == "settings":
        await query.edit_message_text("⚙️ Settings menu coming soon!")

ASK_OPTIONS = range(2)

# Entry point


async def start_schedule(update, context):
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


async def start_poll(update, context):
    await update.message.reply_text(
        "Welcome! Let's set up your poll.\n\nWhat is the poll question?"
    )
    return ASK_QUESTION

# Step 1: User sends poll question


async def get_question(update, context):
    context.user_data["poll_question"] = update.message.text
    await update.message.reply_text(
        "Great! Now send me the poll options separated by commas."
    )
    return ASK_OPTIONS

# Step 2: User sends poll options


async def get_options(update, context):
    question = context.user_data.get("poll_question")
    options = [x.strip() for x in update.message.text.split(",")]
    await update.message.reply_text(
        f"✅ Poll ready!\nQuestion: {question}\nOptions: {options}",
        reply_markup=ReplyKeyboardRemove()
    )
    # Schedule poll here if needed
    context.user_data.clear()
    return ConversationHandler.END

# Optional fallback


async def cancel(update, context):
    await update.message.reply_text(
        "Poll setup canceled.", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def handle_confirmation(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_yes":
        await query.edit_message_text("✅ Poll started! It will now run daily.")
        # Schedule poll here
    else:
        await query.edit_message_text("❌ Poll setup canceled.")

    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("schedule", start_schedule)],
    states={
        ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_question)],
        ASK_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_options)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

