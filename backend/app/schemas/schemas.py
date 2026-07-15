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
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Tag ---
class TagCreate(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int = 1
    sort_order: int = 0
    description: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort_order: Optional[int] = None
    description: Optional[str] = None
class TagOut(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int
    sort_order: int
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
    children: List["TagOut"] = []

    model_config = {"from_attributes": True}


class TagBrief(BaseModel):
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
    tag_ids: List[int] = []


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class BookmarkOut(BaseModel):
    id: int
    title: str
    url: str
    description: Optional[str] = None
    favicon_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagBrief] = []

    model_config = {"from_attributes": True}


class BookmarkListOut(BaseModel):
    items: List[BookmarkOut]
    total: int
    page: int
    page_size: int
