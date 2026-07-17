import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')

try:
    conn.execute("""
      CREATE TABLE user_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) NOT NULL,
        parent_id INTEGER REFERENCES user_tags(id),
        sort_order INTEGER DEFAULT 0,
        description VARCHAR(500),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user_id, slug)
      )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS ix_user_tags_user ON user_tags(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_user_tags_parent ON user_tags(parent_id)")

    conn.commit()

    c = conn.cursor()
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print("Tables:", tables)
    print(f"\nuser_tags schema:")
    for col in c.execute("PRAGMA table_info(user_tags)").fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}  pk={col[5]}")

finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("\nDone.")
