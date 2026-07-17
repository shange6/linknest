import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')

try:
    conn.execute("""
      CREATE TABLE user_history_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        bookmark_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
      )
    """)
    conn.execute("INSERT INTO user_history_new (id, user_id, bookmark_id, created_at) SELECT id, user_id, bookmark_id, clicked_at FROM user_history")
    conn.execute("DROP TABLE user_history")
    conn.execute("ALTER TABLE user_history_new RENAME TO user_history")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_history_user_time ON user_history(user_id, created_at)")
    conn.commit()

    c = conn.cursor()
    print(f"Rows: {c.execute('SELECT COUNT(*) FROM user_history').fetchone()[0]}")
    for col in c.execute("PRAGMA table_info(user_history)").fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}")

finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("Done.")
