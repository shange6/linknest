# LinkNest 数据库设计文档

## ER 图

```
┌──────────────┐       ┌─────────────────┐       ┌─────────────────────┐
│    users     │       │    bookmarks     │       │    bookmark_tags    │
├──────────────┤       ├─────────────────┤       ├─────────────────────┤
│ id (PK)      │       │ id (PK)         │──1:N──│ bookmark_id (PK,FK) │
│ mobile       │       │ title           │       │ tag_id (PK,FK)      │
│ email (UQ)   │       │ url             │       └──────────┬──────────┘
│ username     │       │ description     │                  │
│ password     │       │ favicon_url     │            N:1   │
│ is_active    │       │ created_at      │                  │
│ created_at   │       │ updated_at      │       ┌──────────┴──────────┐
│ updated_at   │       └─────────────────┘       │        tags         │
└──────────────┘                                 ├─────────────────────┤
                                                 │ id (PK)             │◄── self-ref
                                                 │ name                │    parent_id
                                                 │ slug (UQ)           │──┐
                                                 │ parent_id (FK, NULL)│◄─┘
                                                 │ level               │
                                                 │ sort_order          │
                                                 │ description         │
                                                 │ created_at          │
                                                 │ updated_at          │
                                                 └─────────────────────┘
```

> 书签表不再关联 users 表——书签为全局共享，所有用户可见和操作。

## 表结构详述

### users — 用户表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | INTEGER | PK, AUTOINCREMENT | 用户唯一 ID |
| `mobile` | VARCHAR(20) | NULLABLE, INDEX | 手机号（可选） |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | 登录邮箱 |
| `username` | VARCHAR(100) | NOT NULL | 显示名称 |
| `password` | VARCHAR(255) | NOT NULL | bcrypt 哈希（$2b$...格式） |
| `is_active` | BOOLEAN | DEFAULT TRUE | 账户激活状态 |
| `created_at` | DATETIME | DEFAULT UTC NOW | 注册时间 |
| `updated_at` | DATETIME | ON UPDATE UTC NOW | 最后更新时间 |

### tags — 标签表（自引用树形结构）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | INTEGER | PK, AUTOINCREMENT | 标签唯一 ID |
| `name` | VARCHAR(100) | NOT NULL | 标签显示名称（中文） |
| `slug` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | URL 友好标识（英文） |
| `parent_id` | INTEGER | FK → tags.id, NULLABLE | 父标签 ID，NULL 表示根节点 |
| `level` | INTEGER | NOT NULL, [1-5] | 层级深度（1=根,2=二级...） |
| `sort_order` | INTEGER | DEFAULT 0 | 同级排序权重，升序 |
| `description` | VARCHAR(500) | NULLABLE | 标签说明文本 |
| `created_at` | DATETIME | DEFAULT UTC NOW | 创建时间 |
| `updated_at` | DATETIME | ON UPDATE UTC NOW | 最后修改时间 |

**索引**：
- PRIMARY KEY (`id`)
- UNIQUE INDEX (`slug`)
- INDEX (`parent_id`)
- INDEX (`level`)

### bookmarks — 网址/书签表（全局共享，无用户隔离）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | INTEGER | PK, AUTOINCREMENT | 书签唯一 ID |
| `title` | VARCHAR(500) | NOT NULL | 网页标题 |
| `url` | VARCHAR(2048) | NOT NULL | 完整 URL |
| `description` | TEXT | NULLABLE | 用户备注 |
| `favicon_url` | VARCHAR(2048) | NULLABLE | 网站 favicon 地址（预留） |
| `created_at` | DATETIME | DEFAULT UTC NOW | 创建时间 |
| `updated_at` | DATETIME | ON UPDATE UTC NOW | 最后修改时间 |

**索引**：
- PRIMARY KEY (`id`)
- INDEX (`created_at` DESC)

### bookmark_tags — 书签-标签关联表（多对多）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `bookmark_id` | INTEGER | FK → bookmarks.id, CASCADE DELETE | 书签 ID |
| `tag_id` | INTEGER | FK → tags.id, CASCADE DELETE | 标签 ID |

**约束**：
- PRIMARY KEY (`bookmark_id`, `tag_id`) — 联合主键，防止重复关联
- FOREIGN KEY (`bookmark_id`) REFERENCES `bookmarks`(`id`) ON DELETE CASCADE
- FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE

## 标签层级逻辑

标签筛选时使用递归查询：选中标签 `tag_id=X` 时，查询所有 `parent_id` 路径可达 `X` 的标签 ID 集合，然后从 `bookmark_tags` 中找出关联了这些标签中任一一个的书签。

```python
def get_all_descendant_ids(db, tag_id):
    ids = [tag_id]
    children = db.query(Tag).filter(Tag.parent_id == tag_id).all()
    for child in children:
        ids.extend(get_all_descendant_ids(db, child.id))
    return ids
```

## 数据统计

| 指标 | 值 |
|------|-----|
| 总表数 | 4 |
| 根分类标签 | 12 |
| 二级标签 | 48 |
| 三级标签 | 114 |
| 总标签节点 | 174 |
| 标签最大深度 | 3 |
