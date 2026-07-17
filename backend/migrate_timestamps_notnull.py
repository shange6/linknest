import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')
conn.execute('SAVEPOINT migration')

try:
    conn.execute("""
      CREATE TABLE users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile VARCHAR(20),
        email VARCHAR(255),
        username VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CHECK (mobile IS NOT NULL OR email IS NOT NULL),
        UNIQUE (mobile),
        UNIQUE (email)
      )
    """)

    conn.execute("INSERT INTO users_new SELECT * FROM users")
    conn.execute("DROP TABLE users")
    conn.execute("ALTER TABLE users_new RENAME TO users")

    conn.execute("CREATE INDEX IF NOT EXISTS ix_users_mobile ON users(mobile)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)")

    conn.execute('RELEASE migration')
    conn.commit()

    c = conn.cursor()
    for col in c.execute("PRAGMA table_info(users)").fetchall():
        if col[1] in ('created_at','updated_at','is_active'):
            print(f"  {col[1]}  notnull={col[3]}  dflt={col[4]}")

except Exception as e:
    conn.execute('ROLLBACK')
    print(f"Failed: {e}")
    raise
finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("Done.")
