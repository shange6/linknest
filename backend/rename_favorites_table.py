import sqlite3, os
db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
c = sqlite3.connect(db)
c.execute("ALTER TABLE user_favorites RENAME TO user_bookmarks")
c.commit()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("Tables:", tables)
c.close()
print("OK")
