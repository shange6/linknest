import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')
conn.execute('SAVEPOINT migration')

try:
    conn.execute("""
      CREATE TABLE tags_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        parent_id INTEGER REFERENCES tags_new(id),
        sort_order INTEGER DEFAULT 0,
        description VARCHAR(500),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      )
    """)

    conn.execute("INSERT INTO tags_new (id, name, slug, parent_id, sort_order, description, created_at, updated_at) SELECT id, name, slug, parent_id, sort_order, description, created_at, updated_at FROM tags")

    conn.execute("DROP TABLE tags")
    conn.execute("ALTER TABLE tags_new RENAME TO tags")

    conn.execute("CREATE INDEX IF NOT EXISTS ix_tags_slug ON tags(slug)")

    conn.execute('RELEASE migration')
    conn.commit()

    c = conn.cursor()
    print("Schema:")
    for col in c.execute("PRAGMA table_info(tags)").fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}")

    print(f"\nRows: {c.execute('SELECT COUNT(*) FROM tags').fetchone()[0]}")

except Exception as e:
    conn.execute('ROLLBACK')
    print(f"Failed: {e}")
    raise
finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("Done.")
