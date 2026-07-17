import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)

conn.execute("ALTER TABLE bookmark_tags RENAME TO bookmarks_tags")
conn.commit()

c = conn.cursor()
tables = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("Tables:", tables)

count = c.execute("SELECT COUNT(*) FROM bookmarks_tags").fetchone()[0]
print(f"Rows: {count}")

conn.close()
print("Done.")
