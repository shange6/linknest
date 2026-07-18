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
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int = 1
    sort: int = 0
    status: bool = True
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort: Optional[int] = None
    status: Optional[bool] = None
    description: Optional[str] = None
class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int
    sort: int
    status: bool
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    children: List["CategoryOut"] = []

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    name: str
    slug: str
    level: int

    model_config = {"from_attributes": True}


# --- Bookmark ---
class BookmarkCreate(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    status: bool = True
    category_ids: List[int] = []


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None
    category_ids: Optional[List[int]] = None


class BookmarkOut(BaseModel):
    id: int
    title: str
    url: str
    description: Optional[str] = None
    favicon_url: Optional[str] = None
    status: bool
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
    url: str
    description: Optional[str] = None
    category_ids: List[int] = []


class UserBookmarkOut(BaseModel):
    id: int
    user_id: int
    title: str
    url: str
    favicon_url: Optional[str] = None
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
