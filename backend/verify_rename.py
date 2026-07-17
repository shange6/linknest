import sqlite3, os
db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
c = sqlite3.connect(db)
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("Tables:", tables)
print(f"bookmarks_tags rows: {c.execute('SELECT COUNT(*) FROM bookmarks_tags').fetchone()[0]}")
c.close()
