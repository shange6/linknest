import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)

conn.execute("""
  CREATE TABLE IF NOT EXISTS user_favorites (
    user_id INTEGER NOT NULL,
    bookmark_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, bookmark_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
  )
""")

conn.execute("""
  CREATE TABLE IF NOT EXISTS user_click_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bookmark_id INTEGER NOT NULL,
    clicked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
  )
""")

conn.execute("CREATE INDEX IF NOT EXISTS ix_click_history_user_time ON user_click_history(user_id, clicked_at)")

conn.commit()

c = conn.cursor()
for t in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
    print(f"  {t[0]}")

# Verify
for table in ['user_favorites', 'user_click_history']:
    c.execute(f"PRAGMA table_info('{table}')")
    print(f"\n{table}:")
    for col in c.fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}")

conn.close()
print("\nDone.")
