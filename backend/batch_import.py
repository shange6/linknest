"""
Batch bookmark importer with auto tag matching.
Reads JSON lines: {"title":"...","url":"...","description":"...","tags":[["根","子"],...]}
Auto-finds or creates tags by path, upserts slugs.
"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.tag import Tag
from app.models.bookmark import Bookmark
from sqlalchemy import func


def slugify(name: str) -> str:
    """Generate a slug from a name, preserving CJK via hash fallback."""
    import re, hashlib
    # Try ASCII-friendly first
    s = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', name).strip('-').lower()
    if not s or len(re.sub(r'[^a-zA-Z0-9]', '', s)) < 2:
        # Heavily CJK — use hash-based slug
        s = hashlib.md5(name.encode()).hexdigest()[:10]
    return s[:80]


def get_or_create_tag(db, path: list[str], parent_id: int | None = None, level: int = 1) -> int:
    """Walk or create tag hierarchy and return leaf tag ID."""
    if not path:
        return parent_id or 0

    name = path[0].strip()
    slug = slugify(name)

    # Try to find existing
    tag = db.query(Tag).filter(Tag.slug == slug).first()
    if not tag:
        # Check existing names under same parent
        existing = db.query(Tag).filter(
            Tag.name == name,
            Tag.parent_id == parent_id
        ).first()
        if existing:
            tag = existing
        else:
            tag = Tag(
                name=name,
                slug=slug,
                parent_id=parent_id,
                level=level,
                sort_order=0,
            )
            db.add(tag)
            db.flush()
    elif parent_id is not None and tag.parent_id != parent_id:
        # Slug collision — create a new one with unique suffix
        tag = Tag(
            name=name,
            slug=f"{slug}-{parent_id}",
            parent_id=parent_id,
            level=level,
            sort_order=0,
        )
        db.add(tag)
        db.flush()

    if len(path) == 1:
        return tag.id
    return get_or_create_tag(db, path[1:], parent_id=tag.id, level=level + 1)


def import_batch(jsonl_path: str):
    db = SessionLocal()

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]

    total = len(lines)
    imported = 0
    skipped = 0
    errors = 0

    for i, line in enumerate(lines):
        try:
            item = json.loads(line)
            url = item.get('url', '').strip()
            title = item.get('title', '').strip()[:500]
            if not url or not title:
                skipped += 1
                continue

            # Deduplicate by URL
            existing = db.query(Bookmark).filter(Bookmark.url == url).first()
            if existing:
                skipped += 1
                continue

            bm = Bookmark(
                title=title,
                url=url,
                description=item.get('description', '')[:2000],
            )

            tag_ids = set()
            for tag_path in item.get('tags', []):
                if not tag_path:
                    continue
                tid = get_or_create_tag(db, tag_path)
                if tid:
                    tag_ids.add(tid)

            if tag_ids:
                tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                bm.tags = tags

            db.add(bm)
            imported += 1

            # Commit in batches of 200
            if imported % 200 == 0:
                db.commit()
                print(f"  [{imported + skipped}/{total}] imported={imported} skipped={skipped} errors={errors} tags={db.query(Tag).count()}")

        except Exception as e:
            errors += 1
            db.rollback()
            if errors <= 5:
                print(f"  Error line {i}: {e}")

    db.commit()

    tag_count = db.query(Tag).count()
    bm_count = db.query(Bookmark).count()
    db.close()

    print(f"\nDONE: {imported} imported, {skipped} skipped (duplicates), {errors} errors")
    print(f"Total: {bm_count} bookmarks, {tag_count} tags")
    return imported


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'batch_import.jsonl'
    import_batch(path)
