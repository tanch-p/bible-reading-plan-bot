from dotenv import load_dotenv
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from db import insert_group_invite

async def start_private(update, context):
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add me to a Group",
                url="https://t.me/YourBotUsername?startgroup=true",
            )
        ]
    ]
    text = (
        "Hi! I can send daily polls in your group.\n\n"
        "Step 1️⃣: Add me to your group\n"
        "Step 2️⃣: Promote me as an *admin*\n"
        "Step 3️⃣: Use /start in the group to set up your poll"
    )
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
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


# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# --- SQLite Setup ---
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()


def add_group(chat_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO groups (id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()


def get_all_groups():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT id FROM groups")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    return groups


# --- Handlers ---


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


async def handle_button(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "start_poll":
        chat_id = query.message.chat.id
        add_group(chat_id)
        await query.edit_message_text(
            "✅ Daily polls will now be sent to this group every morning!"
        )

    elif query.data == "settings":
        await query.edit_message_text("⚙️ Settings menu coming soon!")


async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a response to any non-command input!")


async def bot_added_to_group(update, context):
    new_member = update.my_chat_member.new_chat_member.user
    if new_member.is_bot and new_member.username == context.bot.username:
        insert_group_invite(update.my_chat_member)


# --- APScheduler Job ---


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


# --- Command Setup ---


async def set_commands(app):
    commands = [
        BotCommand("start", "Start setup or show menu"),
        BotCommand("help", "Show help message"),
    ]
    await app.bot.set_my_commands(commands)


async def help_command(update, context):
    await update.message.reply_text(
        "/start - Begin setup\n/help - Show this help message"
    )

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


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(
        ChatMemberHandler(bot_added_to_group,
                          chat_member_types="my_chat_member")
    )
    app.add_handler(MessageHandler(
        filters.TEXT & (~filters.COMMAND), catch_all))
    app.post_init = set_commands

    print("✅ Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
