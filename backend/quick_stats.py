import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 各层级的标签数
for level in [1, 2, 3]:
    c = db.execute(text("SELECT COUNT(*) FROM tags WHERE level = :l"), {"l": level}).scalar()
    print(f"Level {level} 标签: {c}")

# 带书签最多的叶子标签 Top 15
print("\n叶子标签 / 书签数 (Top 15):")
rows = db.execute(text("""
    SELECT t.name, t.level, COUNT(bt.bookmark_id) as cnt
    FROM tags t
    JOIN bookmark_tags bt ON t.id = bt.tag_id
    GROUP BY t.id
    ORDER BY cnt DESC
    LIMIT 15
""")).fetchall()
for r in rows:
    print(f"  {r[0]} (L{r[1]}): {r[2]}")

# 书签数 / 有 0/1/2/3+ 标签的书签数
print("\n书签标签数量分布:")
rows = db.execute(text("""
    SELECT tag_count, COUNT(*) as bm_count FROM (
        SELECT b.id, COUNT(bt.tag_id) as tag_count
        FROM bookmarks b
        LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
        GROUP BY b.id
    ) GROUP BY tag_count ORDER BY tag_count
""")).fetchall()
for r in rows:
    print(f"  {r[0]} 个标签: {r[1]} 条书签")

db.close()
