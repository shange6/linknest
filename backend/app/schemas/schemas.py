from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, List


# --- Auth ---
class UserRegister(BaseModel):
    email: Optional[str] = None
    mobile: Optional[str] = None
    username: str
    password: str

    @model_validator(mode="after")
    def check_contact(self):
        e_valid = self.email and self.email.strip()
        m_valid = self.mobile and self.mobile.strip()
        if not e_valid and not m_valid:
            raise ValueError("Mobile or email must be provided")
        return self


class UserLogin(BaseModel):
    email: Optional[str] = None
    mobile: Optional[str] = None
    username: Optional[str] = None
    password: str


class UserOut(BaseModel):
    id: int
    mobile: Optional[str] = None
    email: Optional[str] = None
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
class CategoryTranslationSchema(BaseModel):
    language_code: str
    name: str
    description: Optional[str] = None
    sort: Optional[int] = None

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    id: Optional[int] = None
    slug: str
    parent_id: Optional[int] = None
    status: bool = True
    translations: List[CategoryTranslationSchema] = []
    manager_ids: List[int] = []
    # Backward compatibility fields
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None


class CategoryUpdate(BaseModel):
    id: Optional[int] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    status: Optional[bool] = None
    translations: Optional[List[CategoryTranslationSchema]] = None
    manager_ids: Optional[List[int]] = None
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None


class CategoryOut(BaseModel):
    id: int
    slug: str
    parent_id: Optional[int] = None
    status: bool
    name: str = ""
    description: Optional[str] = None
    sort: Optional[int] = None
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    translations: List[CategoryTranslationSchema] = []
    managers: List[UserOut] = []
    children: List["CategoryOut"] = []
    bookmarks_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    slug: str
    name: str = ""
    name_zh: Optional[str] = None
    name_en: Optional[str] = None

    model_config = {"from_attributes": True}


# --- Bookmark ---
class BookmarkTranslationSchema(BaseModel):
    language_code: str
    name: str
    title: str
    description: Optional[str] = None
    sort: Optional[int] = None

    model_config = {"from_attributes": True}


class BookmarkCreate(BaseModel):
    href: str
    icon: Optional[str] = None
    status: bool = True
    translations: List[BookmarkTranslationSchema] = []
    keywords: List[str] = []
    category_ids: List[int] = []
    # Backward compatibility fields
    title_zh: Optional[str] = None
    title_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None


class BookmarkUpdate(BaseModel):
    href: Optional[str] = None
    icon: Optional[str] = None
    status: Optional[bool] = None
    translations: Optional[List[BookmarkTranslationSchema]] = None
    keywords: Optional[List[str]] = None
    category_ids: Optional[List[int]] = None
    title_zh: Optional[str] = None
    title_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None


class BookmarkOut(BaseModel):
    id: int
    href: str
    icon: Optional[str] = None
    status: bool
    name: str = ""
    title: str = ""
    description: Optional[str] = None
    sort: Optional[int] = None
    title_zh: Optional[str] = None
    title_en: Optional[str] = None
    desc_zh: Optional[str] = None
    desc_en: Optional[str] = None
    sort_zh: Optional[int] = None
    sort_en: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    translations: List[BookmarkTranslationSchema] = []
    keywords: List[str] = []
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
    name: Optional[str] = None
    title: Optional[str] = None
    href: str
    icon: Optional[str] = None
    description: Optional[str] = None
    category_ids: List[int] = []

    @model_validator(mode="after")
    def check_name_or_title(self):
        if not self.name and not self.title:
            raise ValueError("Either name or title must be provided")
        if not self.name and self.title:
            self.name = self.title
        return self


class UserBookmarkOut(BaseModel):
    id: int
    user_id: int
    name: str
    title: str = ""  # alias for frontend compatibility
    href: str
    icon: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    categories: List[UserCategoryBrief] = []

    model_config = {"from_attributes": True}


# --- Click History ---
class ClickHistoryCreate(BaseModel):
    bookmark_id: Optional[int] = None
    user_bookmark_id: Optional[int] = None
    is_global: bool = True


class ClickHistoryOut(BaseModel):
    user_id: int
    bookmark_id: Optional[int] = None
    user_bookmark_id: Optional[int] = None
    bookmark: Optional[BookmarkOut] = None
    user_bookmark: Optional[UserBookmarkOut] = None
    click_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

