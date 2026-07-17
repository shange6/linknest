import sqlite3

db = r"C:\Users\shange\.openclaw-autoclaw\workspace\linknest\backend\app\linknest.db"
c = sqlite3.connect(db)

bm_total = c.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]
tag_total = c.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

# Root tags with recursive bookmark counts
counts = c.execute("""
    WITH RECURSIVE tag_ancestors AS (
        SELECT id, id as root_id FROM tags WHERE level = 1
        UNION ALL
        SELECT t.id, ta.root_id FROM tags t JOIN tag_ancestors ta ON t.parent_id = ta.id
    )
    SELECT t.name, COUNT(DISTINCT bt.bookmark_id) as cnt
    FROM tag_ancestors ta
    JOIN tags t ON t.id = ta.root_id
    LEFT JOIN bookmarks_tags bt ON bt.tag_id = ta.id
    GROUP BY ta.root_id
    ORDER BY cnt DESC
""").fetchall()

print(f"书签总数: {bm_total}")
print(f"标签总数: {tag_total}")
print()
print("各根分类书签数（含子标签递归）:")
for r in counts:
    print(f"  {r[0]:14s}  {r[1]:4d}")

# Level distribution
print()
print("标签层级分布:")
for row in c.execute("SELECT level, COUNT(*) FROM tags GROUP BY level ORDER BY level"):
    print(f"  L{row[0]}: {row[1]} 个")

# New roots (those not in original 12)
orig = {"tech-dev","news-media","social","education","shopping","finance","design","entertainment","tools","science","life","gov-org"}
new_roots = c.execute("SELECT name, slug FROM tags WHERE level=1 AND slug NOT IN ({})".format(",".join("?"*len(orig))), list(orig)).fetchall()
if new_roots:
    print(f"\n采集过程中新增的根分类 ({len(new_roots)}):")
    for r in new_roots:
        print(f"  {r[0]} ({r[1]})")

c.close()
