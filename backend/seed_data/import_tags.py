"""Import tag seed data from JSON into database."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.init_db import init_db
from app.models.tag import Tag


def import_tags(data: list[dict], parent_id: int | None = None, db=None):
    for item in data:
        children = item.pop("children", [])
        tag = Tag(parent_id=parent_id, **item)
        db.add(tag)
        db.flush()
        import_tags(children, parent_id=tag.id, db=db)


def main():
    init_db()
    db = SessionLocal()

    existing = db.query(Tag).count()
    if existing > 0:
        print(f"Database already has {existing} tags. Skipping import.")
        db.close()
        return

    json_path = os.path.join(os.path.dirname(__file__), "tags.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    import_tags(data, db=db)
    db.commit()

    count = db.query(Tag).count()
    print(f"Imported {count} tags successfully.")
    db.close()


if __name__ == "__main__":
    main()
