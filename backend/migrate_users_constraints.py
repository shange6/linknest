import sqlite3, os

db = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db')

# Check if backup exists from last migration, delete if stale
backup = os.path.join(os.path.dirname(__file__), 'app', 'linknest.db.bak')
if os.path.exists(backup):
    os.remove(backup)

conn = sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys = OFF')
conn.execute('SAVEPOINT migration')

try:
    # 1. Create new users table with all constraints
    conn.execute("""
      CREATE TABLE users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile VARCHAR(20),
        email VARCHAR(255),
        username VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        CHECK (mobile IS NOT NULL OR email IS NOT NULL),
        UNIQUE (mobile),
        UNIQUE (email)
      )
    """)

    # 2. Copy data (NULL → NULL is fine since constraint allows at least one non-null)
    conn.execute("INSERT INTO users_new SELECT * FROM users")

    # 3. Drop old table
    conn.execute("DROP TABLE users")

    # 4. Rename
    conn.execute("ALTER TABLE users_new RENAME TO users")

    # 5. Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS ix_users_mobile ON users(mobile)")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)")

    conn.execute('RELEASE migration')
    conn.commit()

    # Verify data
    c = conn.cursor()
    rows = c.execute("SELECT id, username, mobile, email, role FROM users").fetchall()
    print("Users after migration:")
    for r in rows:
        print(f"  id={r[0]} username={r[1]} mobile={r[2]!r} email={r[3]!r} role={r[4]}")

    # Verify schema
    c.execute("PRAGMA table_info(users)")
    print("\nSchema:")
    for col in c.fetchall():
        print(f"  {col[1]}  {col[2]}  notnull={col[3]}  dflt={col[4]}  pk={col[5]}")

    # Verify indexes
    c.execute("PRAGMA index_list('users')")
    print("\nIndexes:")
    for idx in c.fetchall():
        c2 = conn.cursor()
        c2.execute(f"PRAGMA index_info('{idx[1]}')")
        cols = [ic[2] for ic in c2.fetchall()]
        print(f"  {idx[1]}  unique={idx[2]}  columns={cols}")

    # Test: both null should fail
    try:
        conn.execute("INSERT INTO users (username, password, role) VALUES ('bad', 'x', 'user')")
        conn.commit()
        print("\nERROR: Both-null constraint did not fire!")
    except sqlite3.IntegrityError as e:
        print(f"\nCHECK (at least one not null) works: {e}")

    # Test: duplicate mobile should fail
    try:
        conn.execute("INSERT INTO users (username, password, mobile) VALUES ('dup', 'x', NULL)")
        conn.commit()
        print("ERROR: Duplicate NULL mobile constraint did not fire!")
    except sqlite3.IntegrityError as e:
        print(f"UNIQUE (multiple NULLs allowed): {e}")

    # Test: valid insert with mobile only
    conn.execute("INSERT INTO users (username, password, mobile) VALUES ('mobileonly', 'x', '13800000001')")
    conn.commit()
    print("Insert with mobile only: OK")

    # Test: valid insert with email only
    conn.execute("INSERT INTO users (username, password, email) VALUES ('emailonly', 'x', 'only@test.com')")
    conn.commit()
    print("Insert with email only: OK")

    # Test: duplicate email should fail
    try:
        conn.execute("INSERT INTO users (username, password, email) VALUES ('dup','x','only@test.com')")
        conn.commit()
        print("ERROR: Duplicate email constraint did not fire!")
    except sqlite3.IntegrityError as e:
        print(f"UNIQUE email works: {e}")

except Exception as e:
    conn.execute('ROLLBACK')
    print(f"Migration failed: {e}")
    raise

finally:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.close()

print("\nDone.")
