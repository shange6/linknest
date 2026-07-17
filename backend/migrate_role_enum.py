import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')
conn = sqlite3.connect(db)

# 1. Create new table with CHECK constraint
conn.execute("""
  CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mobile VARCHAR(20),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
""")

# 2. Copy data
conn.execute("INSERT INTO users_new SELECT * FROM users")

# 3. Drop old table
conn.execute("DROP TABLE users")

# 4. Rename
conn.execute("ALTER TABLE users_new RENAME TO users")

# 5. Recreate indexes
conn.execute("CREATE INDEX IF NOT EXISTS ix_users_mobile ON users(mobile)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)")

conn.commit()

# Verify existing data
c = conn.cursor()
c.execute("SELECT id, username, role FROM users")
print("Users after migration:")
for r in c.fetchall():
    print(f"  id={r[0]} username={r[1]} role={r[2]}")

# Test CHECK constraint — should fail
try:
    conn.execute("INSERT INTO users (email, username, password, role) VALUES ('x@t.com','test','hash','superadmin')")
    conn.commit()
    print("ERROR: CHECK constraint did not fire!")
except sqlite3.IntegrityError as e:
    print(f"CHECK constraint works: {e}")

# Verify schema
c.execute("PRAGMA table_info(users)")
print("\nNew users schema:")
for col in c.fetchall():
    print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}  pk={col[5]}")

conn.close()
print("\nDone.")
