from dotenv import load_dotenv
import os
from handlers.workflows import (
    handle_buttons,
    set_commands,
    catch_all,
    bot_added_to_group,
)
from handlers.start import start
from handlers.menu import get_menu_conversation_handler
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    CommandHandler
)



# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(
        ChatMemberHandler(bot_added_to_group, chat_member_types="my_chat_member")
    )
    app.add_handler(get_menu_conversation_handler())
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), catch_all))
    app.post_init = set_commands
    print("✅ Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
