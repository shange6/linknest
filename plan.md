# 网址分类管理网站 — 工作计划方案

> **项目代号**: LinkNest  
> **审批状态**: ✅ 已批准（根据数据库实际结构已修正）  
> **设计风格**: 03 Information Architects（零装饰、系统字体、内容优先）

---

## 一、项目概述

构建一个基于 Vue3 + FastAPI 的个人/小团队网址分类管理工具。核心功能：多级分类体系 + 网址 CRUD + 分类树筛选浏览 + 用户注册登录 + 个人收藏夹与访问历史统计。

---

## 二、技术架构

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│   Vue3 前端      │ ◄────────────────► │  FastAPI 后端    │
│   (Vite构建)     │   Axios + JWT      │  (SQLAlchemy)   │
│   Pinia 状态管理  │                    │  SQLite 数据库   │
│   Vue Router     │                    │  Pydantic 校验   │
└─────────────────┘                    └─────────────────┘
```

| 层 | 技术选型 | 理由 |
|---|---|---|
| 前端框架 | Vue 3 + Composition API | 用户指定 |
| 构建工具 | Vite | 标准选型 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| 路由 | Vue Router 4 | SPA 路由 |
| HTTP | Axios | 拦截器、JWT 自动附加 |
| UI 样式 | 手写 CSS（Information Architects 风格） | 零装饰、系统字体栈 |
| 后端框架 | FastAPI | 用户指定 |
| ORM | SQLAlchemy 2.0 | 成熟稳定 |
| 数据库 | SQLite（开发/运行阶段） | 零配置、单文件 |
| 迁移 | Alembic | SQLAlchemy 标准迁移工具 |
| 认证 | JWT（python-jose + passlib） | 无状态、适合 SPA |
| 密码加密 | bcrypt（passlib） | 行业标准 |

---

## 三、分类体系设计（实际数据说明）

基于实际的分类结构，包含 **17 个根分类 + 3 级深度 + 504 个分类节点**。

### 根分类（L1，17 个）

| # | 根分类 | slug | 说明 |
|---|---|---|---|
| 1 | 社交平台 | baa2f715ac | 常用社交应用、网络社区 |
| 2 | 内容平台 | 4592ced768 | 博客、自媒体、文章分发平台 |
| 3 | 科技数码 | f1b6568745 | 科技新闻、数码评测、硬件论坛 |
| 4 | 海外技术 | 76acd6062c | 英文技术论坛、海外博客与新闻 |
| 5 | 通讯工具 | 389900a65c | 即时通讯、协同办公软件 |
| 6 | 技术开发 | tech-dev | 编程、框架、工具、社区 |
| 7 | 新闻资讯 | news-media | 综合/科技/财经/体育新闻 |
| 8 | 社交媒体 | social | 社交网络、论坛、即时通讯 |
| 9 | 学习教育 | education | 在线课程、学术资源、培训 |
| 10 | 购物电商 | shopping | 综合/垂直电商、二手交易 |
| 11 | 金融财经 | finance | 银行、证券、支付、资讯 |
| 12 | 设计创意 | design | UI/UX、平面、插画、摄影 |
| 13 | 影音娱乐 | entertainment | 视频、音乐、游戏、动漫 |
| 14 | 工具效率 | tools | 笔记、任务、文档、AI 工具 |
| 15 | 科学学术 | science | 论文、期刊、科普、研究 |
| 16 | 生活服务 | life | 出行、餐饮、健康、房产 |
| 17 | 政府组织 | gov-org | 政府、国际组织、NGO |

### 层级与分布
- **一级根分类 (L1)**: 17 个
- **二级分类 (L2)**: 358 个
- **三级分类 (L3)**: 129 个
- **最大深度**: 3 级

完整分类树及数据已持久化于 `linknest.db` 中。

---

## 四、数据库设计

数据库总共有 7 张主要的实体与关系表：

### 表结构

**1. users — 用户表**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 用户 ID |
| `mobile` | VARCHAR(20) | UNIQUE, NULLABLE, INDEX | 手机号 |
| `email` | VARCHAR(255) | UNIQUE, NULLABLE, INDEX | 登录邮箱 |
| `username` | VARCHAR(100) | NOT NULL | 显示名称 |
| `password` | VARCHAR(255) | NOT NULL | bcrypt 密码哈希 |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT 'user' | 角色权限（'admin', 'user'） |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否激活 |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 注册时间 |
| `updated_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 更新时间 |

- **表级约束**：`CHECK(role IN ('admin','user'))`，`CHECK(mobile IS NOT NULL OR email IS NOT NULL)`

**2. categories — 全局共享分类表（自引用树形结构）**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 分类 ID |
| `name` | VARCHAR(100) | NOT NULL | 分类名称 |
| `slug` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | URL 友好标识 |
| `parent_id` | INTEGER | FK → categories.id, NULLABLE, INDEX | 父分类 ID |
| `sort_order` | INTEGER | DEFAULT 0 | 同级排序 |
| `description` | VARCHAR(500) | NULLABLE | 分类说明 |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 创建时间 |
| `updated_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 更新时间 |

- **说明**：此表不存储 `level` 列，层级深度由应用层在运行时动态计算。

**3. bookmarks — 全局共享网址表**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 书签 ID |
| `title` | VARCHAR(500) | NOT NULL | 网页标题 |
| `url` | VARCHAR(2048) | UNIQUE, NOT NULL | 唯一完整 URL |
| `description` | TEXT | NULLABLE | 描述/备注 |
| `favicon_url` | VARCHAR(2048) | NULLABLE | 网站图标 |
| `created_at` | DATETIME | DEFAULT UTC NOW | 创建时间 |
| `updated_at` | DATETIME | DEFAULT UTC NOW | 更新时间 |

**4. bookmarks_categories — 书签-分类全局关联表（多对多）**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `bookmark_id` | INTEGER | PK, FK → bookmarks.id, ON DELETE CASCADE | 书签 ID |
| `category_id` | INTEGER | PK, FK → categories.id, ON DELETE CASCADE | 分类 ID |

**5. user_bookmarks — 用户收藏表（多对多，带分类）**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `user_id` | INTEGER | PK, FK → users.id, ON DELETE CASCADE | 用户 ID |
| `bookmark_id` | INTEGER | PK, FK → bookmarks.id, ON DELETE CASCADE | 书签 ID |
| `category_id` | INTEGER | PK, FK → categories.id, ON DELETE CASCADE | 收藏夹关联分类 |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 收藏时间 |

**6. user_categories — 用户私有分类表**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 私有分类 ID |
| `user_id` | INTEGER | FK → users.id, ON DELETE CASCADE, INDEX | 所属用户 |
| `name` | VARCHAR(100) | NOT NULL | 分类名称 |
| `slug` | VARCHAR(100) | NOT NULL | 标识符 |
| `parent_id` | INTEGER | FK → user_categories.id, NULLABLE | 父级 ID |
| `sort_order` | INTEGER | DEFAULT 0 | 排序权重 |
| `description` | VARCHAR(500) | NULLABLE | 描述 |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 创建时间 |
| `updated_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 更新时间 |

- **唯一约束**：`UNIQUE(user_id, slug)`

**7. user_history — 用户点击流历史表**

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `user_id` | INTEGER | PK, FK → users.id, ON DELETE CASCADE | 用户 ID |
| `bookmark_id` | INTEGER | PK, FK → bookmarks.id, ON DELETE CASCADE | 书签 ID |
| `click_count` | INTEGER | NOT NULL, DEFAULT 1 | 点击次数 |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 首次访问时间 |
| `updated_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | 最后访问时间 |

- **索引**：`ix_history_user_count` (`user_id`, `click_count`)

---

## 五、API 接口设计

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/auth/register` | 注册 | 无 |
| POST | `/api/auth/login` | 登录，返回 JWT | 无 |
| GET | `/api/auth/me` | 获取当前用户信息 | JWT |

### 分类模块 `/api/categories`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/categories` | 获取完整分类树 | JWT |
| GET | `/api/categories/{id}` | 获取单个分类详情 | JWT |
| GET | `/api/categories/{id}/children` | 获取子分类 | JWT |
| POST | `/api/categories` | 创建分类（仅管理员） | JWT |
| PUT | `/api/categories/{id}` | 更新分类（仅管理员） | JWT |
| DELETE | `/api/categories/{id}` | 删除分类（仅管理员） | JWT |

### 书签模块 `/api/bookmarks`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/bookmarks` | 获取书签列表（支持筛选） | JWT |
| POST | `/api/bookmarks` | 创建书签（仅管理员） | JWT |
| GET | `/api/bookmarks/{id}` | 获取书签详情 | JWT |
| PUT | `/api/bookmarks/{id}` | 更新书签（仅管理员） | JWT |
| DELETE | `/api/bookmarks/{id}` | 删除书签（仅管理员） | JWT |

### 用户收藏夹模块 `/api/user_bookmarks`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/user_bookmarks` | 获取当前用户收藏的所有书签 | JWT |
| POST | `/api/user_bookmarks` | 添加书签到收藏夹 | JWT |
| DELETE | `/api/user_bookmarks/{bookmark_id}` | 从收藏夹移除 | JWT |
| GET | `/api/user_bookmarks/check/{bookmark_id}` | 校验某书签是否已被收藏 | JWT |

### 用户历史记录模块 `/api/user_history`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/user_history` | 分页/Limit 获取当前用户浏览历史 | JWT |
| POST | `/api/user_history` | 记录一次书签点击（计数+1） | JWT |
| DELETE | `/api/user_history` | 清空当前用户的所有点击历史 | JWT |

---

## 六、前端设计

### 路由结构

| 路径 | 组件 | 说明 |
|---|---|---|
| `/login` | LoginView | 登录页 |
| `/register` | RegisterView | 注册页 |
| `/` | HomeView | 主界面（需登录） |

### 组件树

```
App.vue
├── LoginView.vue
├── RegisterView.vue
└── HomeView.vue                    [认证后]
    ├── AppHeader.vue               [用户信息 + 登出]
    ├── CategoryTree.vue            [左侧分类树面板]
    │   └── CategoryNode.vue        [递归树节点]
    ├── BookmarkList.vue            [右侧书签列表]
    │   └── BookmarkCard.vue        [单个书签卡片]
    └── BookmarkEditor.vue          [新增/编辑弹窗]
        └── CategorySelector.vue    [多级分类选择器]
```

### 状态管理 (Pinia)

| Store | 职责 |
|---|---|
| `useAuthStore` | 用户登录状态、JWT 管理、自动登录 |
| `useCategoryStore` | 分类树数据、选中节点、展开状态 |
| `useBookmarkStore` | 书签列表、增删改查、筛选条件 |

### 设计风格落地（Information Architects）

- 系统字体栈：`-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`
- 传统蓝色链接 `#0000EE`，已访问 `#551A8B`
- 66 字符最佳行长，16px 基准字号
- 零装饰：无渐变、无阴影、无圆角（或最小 2px）
- 黑白灰 + 经典链接蓝 作为唯一强调色
- 布局：左侧分类树 260px + 右侧内容区，类双栏文档风格

---

## 七、开发阶段与预估

| 阶段 | 内容 | 产出 |
|---|---|---|
| **1. 项目初始化** | 创建前端 Vite + Vue3 项目、后端 FastAPI 项目骨架 | 项目目录、依赖配置 |
| **2. 数据库与分类** | 导入现存的 504 个分类、2292 个书签及映射数据 | SQLite 数据库文件 (`linknest.db`) |
| **3. 后端 API** | 认证接口 → 分类树接口 → 书签 CRUD → 收藏夹和历史记录 API | 全部 REST API 可用 |
| **4. 前端核心** | 登录/注册 → 分类树 → 书签管理 → 筛选浏览 | 完整可交互界面 |
| **5. 联调验证** | 前后端联调、冒烟测试、交互验证 | 端到端工作流通过 |
| **6. 文档交付** | README、启动说明、验证清单 | 可交付文档 |

---

## 八、交付物清单

| # | 交付物 | 格式 |
|---|---|---|
| 1 | 项目开发计划（本文档） | Markdown |
| 2 | FastAPI 后端项目源码 | Python 项目目录 |
| 3 | Vue3 前端项目源码 | Vite + Vue3 项目目录 |
| 4 | 数据库备份与持久化文件 | SQLite 数据库文件 |
| 5 | 前后端启动与部署说明 | README.md |
| 6 | 数据库设计文档（含 ER 图说明） | Markdown |

---

## 九、需要确认的事项

1. **数据库**：开发阶段与实际存储统一使用 SQLite (`backend/app/linknest.db`) → ✅ 确认
2. **全局数据**：书签和分类结构是全局的，所有用户都可以查阅，但管理员有权编辑全局分类和全局书签 → ✅ 确认
3. **个人数据**：用户在全局书签的基础上，通过 `/api/user_bookmarks` 和 `/api/user_history` 实现个性化的收藏和点击统计隔离 → ✅ 确认
4. **邮箱验证**：无需邮箱验证，注册即可登录 → ✅ 确认
