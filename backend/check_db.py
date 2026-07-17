import sqlite3

db_path = r"C:\Users\shange\.openclaw-autoclaw\workspace\linknest\backend\app\linknest.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Tables
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("Tables:", [t[0] for t in tables])

# Columns
for tbl in ['users', 'tags', 'bookmarks', 'bookmarks_tags']:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({tbl})").fetchall()]
    print(f"\n{tbl} columns: {cols}")

# Tag stats
root_tags = c.execute("SELECT name, slug, level FROM tags WHERE level=1 ORDER BY sort_order").fetchall()
print(f"\nRoot tags ({len(root_tags)}):")
for r in root_tags:
    print(f"  {r[0]} ({r[1]})")

l2_count = c.execute("SELECT COUNT(*) FROM tags WHERE level=2").fetchone()[0]
l3_count = c.execute("SELECT COUNT(*) FROM tags WHERE level=3").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
print(f"\nLevels: L1={len(root_tags)} L2={l2_count} L3={l3_count} Total={total}")

# Check parent_id relationship correctness
orphans = c.execute("SELECT COUNT(*) FROM tags WHERE level > 1 AND parent_id IS NULL").fetchone()[0]
print(f"\nOrphan tags (level>1 without parent): {orphans}")

# Verify unique slugs
dupes = c.execute("SELECT slug, COUNT(*) FROM tags GROUP BY slug HAVING COUNT(*) > 1").fetchall()
print(f"Duplicate slugs: {dupes if dupes else 'None'}")

# User count
user_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"\nUsers: {user_count}")

conn.close()
print("\nDone.")
