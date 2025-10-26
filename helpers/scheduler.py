from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def send_daily_poll(context):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    for (chat_id,) in c.execute("SELECT id FROM groups"):
        await context.bot.send_poll(chat_id, "Daily Question", ["Yes", "No", "Maybe"])
    conn.close()

# Schedule at 9 AM daily
scheduler.add_job(send_daily_poll, "cron", hour=9, minute=0, args=[app.bot])
scheduler.start()
