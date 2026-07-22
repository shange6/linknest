from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from math import ceil

from app.core.database import get_db
from app.core.auth import require_admin, get_current_user
from app.models.bookmark import Bookmark, BookmarkTranslation, Keyword
from app.models.category import Category
from app.models.user import User
from app.schemas.schemas import BookmarkCreate, BookmarkUpdate
from app.core.favicon import fetch_favicon, download_and_convert_to_base64

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


def get_all_descendant_ids(db: Session, category_id: int) -> List[int]:
    """Get all descendant category IDs (including the given category_id)."""
    ids = [category_id]
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    for child in children:
        ids.extend(get_all_descendant_ids(db, child.id))
    return ids


def format_bookmark_dict(bookmark: Bookmark, lang: str = "zh") -> Dict[str, Any]:
    """Format bookmark object with translation fields and keywords."""
    trans_map = {t.language_code: t for t in bookmark.translations}
    target_t = trans_map.get(lang) or trans_map.get("zh") or (bookmark.translations[0] if bookmark.translations else None)

    zh_t = trans_map.get("zh")
    en_t = trans_map.get("en")

    cat_list = []
    for c in bookmark.categories:
        c_trans_map = {t.language_code: t for t in c.translations}
        c_t = c_trans_map.get(lang) or c_trans_map.get("zh") or (c.translations[0] if c.translations else None)
        c_zh = c_trans_map.get("zh")
        c_en = c_trans_map.get("en")
        cat_list.append({
            "id": c.id,
            "slug": c.slug,
            "name": c_t.name if c_t else "",
            "name_zh": c_zh.name if c_zh else (c_t.name if c_t else ""),
            "name_en": c_en.name if c_en else None,
        })

    return {
        "id": bookmark.id,
        "href": bookmark.href,
        "icon": bookmark.icon,
        "status": bookmark.status,
        "name": target_t.name if target_t else "",
        "title": target_t.title if target_t else (target_t.name if target_t else ""),
        "description": target_t.description if target_t else None,
        "sort": target_t.sort if target_t else None,
        "title_zh": zh_t.title if zh_t else (target_t.title if target_t else ""),
        "title_en": en_t.title if en_t else None,
        "desc_zh": zh_t.description if zh_t else (target_t.description if target_t else None),
        "desc_en": en_t.description if en_t else None,
        "sort_zh": zh_t.sort if zh_t else (target_t.sort if target_t else None),
        "sort_en": en_t.sort if en_t else None,
        "created_at": bookmark.created_at.isoformat() if bookmark.created_at else None,
        "updated_at": bookmark.updated_at.isoformat() if bookmark.updated_at else None,
        "translations": [
            {
                "language_code": t.language_code,
                "name": t.name,
                "title": t.title,
                "description": t.description,
                "sort": t.sort,
            }
            for t in bookmark.translations
        ],
        "keywords": [k.word for k in bookmark.keywords],
        "categories": cat_list,
    }


def sync_bookmark_translations(db: Session, bookmark: Bookmark, data: BookmarkCreate | BookmarkUpdate):
    """Sync bookmark translations from Pydantic input."""
    existing_trans = {t.language_code: t for t in bookmark.translations}
    trans_to_process: Dict[str, Dict[str, Any]] = {}

    if data.translations is not None and len(data.translations) > 0:
        for t_item in data.translations:
            trans_to_process[t_item.language_code] = {
                "name": t_item.name,
                "title": t_item.title or t_item.name,
                "description": t_item.description,
                "sort": t_item.sort,
            }
    else:
        # Backward compatibility fallback
        if getattr(data, "title_zh", None) is not None:
            title_zh = data.title_zh
            trans_to_process["zh"] = {
                "name": title_zh,
                "title": title_zh,
                "description": getattr(data, "desc_zh", None),
                "sort": getattr(data, "sort_zh", None),
            }
        if getattr(data, "title_en", None) is not None:
            title_en = data.title_en
            trans_to_process["en"] = {
                "name": title_en,
                "title": title_en,
                "description": getattr(data, "desc_en", None),
                "sort": getattr(data, "sort_en", None),
            }

    for lang_code, values in trans_to_process.items():
        if lang_code in existing_trans:
            t_obj = existing_trans[lang_code]
            t_obj.name = values["name"]
            t_obj.title = values["title"]
            if values["description"] is not None:
                t_obj.description = values["description"]
            if values["sort"] is not None:
                t_obj.sort = values["sort"]
        else:
            t_obj = BookmarkTranslation(
                bookmark_id=bookmark.id,
                language_code=lang_code,
                name=values["name"],
                title=values["title"],
                description=values["description"],
                sort=values["sort"],
            )
            bookmark.translations.append(t_obj)


def sync_bookmark_keywords(db: Session, bookmark: Bookmark, keywords_list: Optional[List[str]]):
    """Sync keywords for a bookmark."""
    if keywords_list is None:
        return
    keyword_objs = []
    for w in keywords_list:
        w_clean = w.strip()
        if not w_clean:
            continue
        kw = db.query(Keyword).filter(Keyword.word == w_clean).first()
        if not kw:
            kw = Keyword(word=w_clean)
            db.add(kw)
            db.flush()
        keyword_objs.append(kw)
    bookmark.keywords = keyword_objs


@router.get("", response_model=Dict[str, Any])
def get_bookmarks(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    lang: str = Query("zh"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Bookmark)

    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        descendant_ids = get_all_descendant_ids(db, category_id)
        query = query.filter(Bookmark.categories.any(Category.id.in_(descendant_ids)))

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Bookmark.href.ilike(like))
            | (Bookmark.translations.any((BookmarkTranslation.name.ilike(like)) | (BookmarkTranslation.title.ilike(like)) | (BookmarkTranslation.description.ilike(like))))
            | (Bookmark.keywords.any(Keyword.word.ilike(like)))
        )

    total = query.count()
    total_pages = max(1, ceil(total / page_size))
    if page > total_pages:
        page = total_pages

    items = (
        query.order_by(Bookmark.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [format_bookmark_dict(item, lang=lang) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=Dict[str, Any], status_code=201)
def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    resolved_icon = data.icon
    if resolved_icon and (resolved_icon.startswith("http://") or resolved_icon.startswith("https://")):
        resolved_icon = download_and_convert_to_base64(resolved_icon)
    if not resolved_icon:
        resolved_icon = fetch_favicon(data.href)

    bookmark = Bookmark(
        href=data.href,
        icon=resolved_icon,
        status=data.status,
    )
    if data.category_ids:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        bookmark.categories = categories

    db.add(bookmark)
    db.flush()

    sync_bookmark_translations(db, bookmark, data)
    sync_bookmark_keywords(db, bookmark, data.keywords)

    db.commit()
    db.refresh(bookmark)
    return format_bookmark_dict(bookmark)


@router.get("/{bookmark_id}", response_model=Dict[str, Any])
def get_bookmark(
    bookmark_id: int,
    lang: str = Query("zh"),
    db: Session = Depends(get_db),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return format_bookmark_dict(bookmark, lang=lang)


@router.put("/{bookmark_id}", response_model=Dict[str, Any])
def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if data.href is not None:
        bookmark.href = data.href
    if data.icon is not None:
        resolved_icon = data.icon
        if resolved_icon and (resolved_icon.startswith("http://") or resolved_icon.startswith("https://")):
            resolved_icon = download_and_convert_to_base64(resolved_icon)
        bookmark.icon = resolved_icon
    if data.status is not None:
        bookmark.status = data.status
    if data.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(data.category_ids)).all()
        bookmark.categories = categories

    sync_bookmark_translations(db, bookmark, data)
    if data.keywords is not None:
        sync_bookmark_keywords(db, bookmark, data.keywords)

    db.commit()
    db.refresh(bookmark)
    return format_bookmark_dict(bookmark)


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return None

