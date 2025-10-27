from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.chat.type

    if chat_type == "private":
        await start_private(update, context)
    elif chat_type in ["group", "supergroup"]:
        await start_group(update, context)
    elif chat_type == "channel":
        pass
    else:
        pass


async def start_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Hi! This bot can help you start a reading plan (only Genesis to Exodus) or send daily polls in your group.\n\n"
        "Step 1️⃣: Add me to your group\n"
        "Step 2️⃣: Promote me as an *admin*\n"
        "Step 3️⃣: Use /start in the group to get started"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown"
    )


async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗳 Schedule a plan/poll",
                              callback_data="schedule")],
        [InlineKeyboardButton("⚙️ Reschedule", callback_data="reschedule")],
    ]
    await update.message.reply_text(
        "Please select an action below:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
