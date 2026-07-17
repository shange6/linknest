import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')
conn.execute('SAVEPOINT migration')

try:
    # Find and delete duplicate URLs (keep lowest id)
    c = conn.cursor()
    dupes = c.execute('''
        SELECT url, COUNT(*) as cnt, MIN(id) as keep_id
        FROM bookmarks
        GROUP BY url
        HAVING cnt > 1
    ''').fetchall()

    to_delete = []
    for url, cnt, keep_id in dupes:
        ids = c.execute('SELECT id FROM bookmarks WHERE url = ? AND id != ?', (url, keep_id)).fetchall()
        for (did,) in ids:
            to_delete.append(did)

    print(f"Removing {len(to_delete)} duplicate bookmarks: {to_delete}")

    # Delete related bookmark_tags first
    for did in to_delete:
        c.execute('DELETE FROM bookmark_tags WHERE bookmark_id = ?', (did,))
        c.execute('DELETE FROM bookmarks WHERE id = ?', (did,))

    # Create new table with UNIQUE url and swapped column order
    conn.execute("""
      CREATE TABLE bookmarks_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        url VARCHAR(2048) NOT NULL UNIQUE,
        favicon_url VARCHAR(2048),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    """)

    conn.execute("INSERT INTO bookmarks_new (id, title, url, favicon_url, description, created_at, updated_at) SELECT id, title, url, favicon_url, description, created_at, updated_at FROM bookmarks")
    conn.execute("DROP TABLE bookmarks")
    conn.execute("ALTER TABLE bookmarks_new RENAME TO bookmarks")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_bookmarks_url ON bookmarks(url)")

    conn.execute('RELEASE migration')
    conn.commit()

    c = conn.cursor()
    print(f"\nSchema:")
    for col in c.execute("PRAGMA table_info(bookmarks)").fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}")

    print(f"\nRows: {c.execute('SELECT COUNT(*) FROM bookmarks').fetchone()[0]}")
    print(f"Associations: {c.execute('SELECT COUNT(*) FROM bookmark_tags').fetchone()[0]}")

    # Test uniqueness
    try:
        c.execute("INSERT INTO bookmarks (title, url) VALUES ('test','https://chat.openai.com')")
        conn.commit()
        print("ERROR: UNIQUE url constraint did not fire!")
    except sqlite3.IntegrityError as e:
        print(f"UNIQUE url works: {e}")

except Exception as e:
    conn.execute('ROLLBACK')
    print(f"Failed: {e}")
    raise
finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("Done.")
