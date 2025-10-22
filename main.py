from dotenv import load_dotenv
import os
from telegram import Bot
from telegram.ext import Application
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()



TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = -1001234567890  # Replace with your group chat ID

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')



bot = Bot(token=TOKEN)

async def send_poll():
    question = "What should we have for lunch today?"
    options = ["Chicken Rice", "Noodles", "Salad", "Fast Food"]
    await bot.send_poll(chat_id=CHAT_ID, question=question, options=options, is_anonymous=False)

async def send_text():
    message = "Good afternoon everyone! Don’t forget to take a break 😊"
    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    print("Bot is running... Press Ctrl+C to stop.")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    app.run_polling()
