"""Import category seed data from JSON into database."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.init_db import init_db
from app.models.category import Category, CategoryTranslation


def import_categories(data: list[dict], parent_id: int | None = None, db=None):
    for item in data:
        children = item.pop("children", [])
        level = item.pop("level", None)
        name = item.pop("name", None)
        description = item.pop("description", None)
        sort = item.pop("sort", None)
        
        category = Category(
            parent_id=parent_id,
            slug=item.get("slug"),
            status=item.get("status", True),
        )
        db.add(category)
        db.flush()

        if name:
            trans = CategoryTranslation(
                category_id=category.id,
                language_code="zh",
                name=name,
                description=description,
                sort=sort,
            )
            db.add(trans)

        import_categories(children, parent_id=category.id, db=db)


def main():
    init_db()
    db = SessionLocal()

    existing = db.query(Category).count()
    if existing > 0:
        print(f"Database already has {existing} categories. Skipping import.")
        db.close()
        return

    json_path = os.path.join(os.path.dirname(__file__), "categories.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    import_categories(data, db=db)
    db.commit()

    count = db.query(Category).count()
    print(f"Imported {count} categories successfully.")
    db.close()


if __name__ == "__main__":
    main()
