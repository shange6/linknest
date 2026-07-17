import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')

try:
    conn.execute("""
      CREATE TABLE user_bookmarks_new (
        user_id INTEGER NOT NULL,
        bookmark_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, bookmark_id, tag_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
      )
    """)

    conn.execute("INSERT INTO user_bookmarks_new (user_id, bookmark_id, created_at) SELECT user_id, bookmark_id, created_at FROM user_bookmarks")
    conn.execute("DROP TABLE user_bookmarks")
    conn.execute("ALTER TABLE user_bookmarks_new RENAME TO user_bookmarks")

    # tag_id can't be null, and old data had no tag_id — set to 1 (root tag) for existing
    conn.execute("UPDATE user_bookmarks SET tag_id = (SELECT MIN(id) FROM tags) WHERE tag_id IS NULL")

    conn.commit()

    c = conn.cursor()
    rows = c.execute("SELECT COUNT(*) FROM user_bookmarks").fetchone()[0]
    print(f"Rows: {rows}")
    for col in c.execute("PRAGMA table_info(user_bookmarks)").fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}  pk={col[5]}")

finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("Done.")
