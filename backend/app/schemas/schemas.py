from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# --- Auth ---
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    mobile: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    mobile: Optional[str] = None
    email: str
    username: str
    role: str
    status: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Category ---
class CategoryCreate(BaseModel):
    id: Optional[int] = None
    name_zh: str
    name_en: Optional[str] = None
    slug: str
    parent_id: Optional[int] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    status: bool = True
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    manager_ids: List[int] = []


class CategoryUpdate(BaseModel):
    id: Optional[int] = None
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    status: Optional[bool] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    manager_ids: Optional[List[int]] = None


class CategoryOut(BaseModel):
    id: int
    name_zh: str
    name_en: Optional[str] = None
    slug: str
    parent_id: Optional[int] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    status: bool
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    updated_at: Optional[datetime] = None
    managers: List[UserOut] = []
    children: List["CategoryOut"] = []

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    name_zh: str
    name_en: Optional[str] = None
    slug: str

    model_config = {"from_attributes": True}


# --- Bookmark ---
class BookmarkCreate(BaseModel):
    title_zh: str
    title_en: Optional[str] = None
    href: str
    icon: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    status: bool = True
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    category_ids: List[int] = []


class BookmarkUpdate(BaseModel):
    title_zh: Optional[str] = None
    title_en: Optional[str] = None
    href: Optional[str] = None
    icon: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    status: Optional[bool] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    category_ids: Optional[List[int]] = None


class BookmarkOut(BaseModel):
    id: int
    title_zh: str
    title_en: Optional[str] = None
    href: str
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    icon: Optional[str] = None
    status: bool
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryBrief] = []

    model_config = {"from_attributes": True}


class BookmarkListOut(BaseModel):
    items: List[BookmarkOut]
    total: int
    page: int
    page_size: int


# --- User Categories & Bookmarks ---
class UserCategoryBrief(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class UserBookmarkCreate(BaseModel):
    title: str
    href: str
    icon: Optional[str] = None
    description: Optional[str] = None
    category_ids: List[int] = []


class UserBookmarkOut(BaseModel):
    id: int
    user_id: int
    title: str
    href: str
    icon: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    categories: List[UserCategoryBrief] = []

    model_config = {"from_attributes": True}


# --- Click History ---
class ClickHistoryCreate(BaseModel):
    bookmark_id: int


class ClickHistoryOut(BaseModel):
    id: int
    user_id: int
    bookmark_id: int
    bookmark: BookmarkOut
    click_count: int
    first_clicked_at: datetime
    last_clicked_at: datetime

    model_config = {"from_attributes": True}
