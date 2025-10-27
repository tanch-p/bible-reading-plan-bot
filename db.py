import sqlite3

DB_PATH = "bot.db"


def init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create jobs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,               -- Telegram group ID
        job_type TEXT NOT NULL,              -- 'chapters' | 'poll'
        schedule_time TEXT NOT NULL,         -- 'HH:MM' format
        day_frequency INTEGER DEFAULT 1,     -- every N days
        last_run DATE,                       -- last time job executed
        active INTEGER DEFAULT 1,            -- 1=active, 0=paused
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    """)

    # Create reading plans table
    c.execute("""
    CREATE TABLE IF NOT EXISTS chapter_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,             -- FK to jobs.id
        books  TEXT NOT NULL,                -- e.g. GEN,EXO,... (comma separated)
        chapters_per_day INTEGER DEFAULT 3,  -- configurable
        current_day INTEGER DEFAULT 1,       -- current day index (for progress)
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Create poll jobs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS poll_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,             -- FK to jobs.id
        question TEXT NOT NULL,              -- e.g. 'How was your week?'
        options TEXT NOT NULL,               -- JSON array of poll options e.g. '["Great","Okay","Tough"]'
        is_anonymous INTEGER DEFAULT 0,      -- Telegram poll setting
        allows_multiple_answers INTEGER DEFAULT 0,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    );
    """)

    # Create job logs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS job_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        chat_id TEXT NOT NULL,
        run_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT,                         -- 'success' or 'failed'
        message TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id)
    );
    """)

    # Create group invites table
    c.execute("""
        CREATE TABLE IF NOT EXISTS group_invites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_chat_id INTEGER NOT NULL,
            group_title TEXT,
            inviter_user_id INTEGER NOT NULL,
            inviter_username TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")


def insert_group_invite(message):
    group_id = message.chat.id
    group_title = message.chat.title
    inviter = message.from_user

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO group_invites (group_chat_id, group_title, inviter_user_id, inviter_username)
        VALUES (?, ?, ?, ?)
    """, (group_id, group_title, inviter.id, inviter.username))
    conn.commit()
    conn.close()

    print(f"✅ Inserted {group_id}, {group_title}, {inviter.id}, {inviter.username} into group_invites_table")

if __name__ == "__main__":
    init()