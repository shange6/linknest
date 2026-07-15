# 网址分类管理网站 — 工作计划方案

> **项目代号**: LinkNest  
> **审批状态**: ⏳ 待审批  
> **设计风格**: 03 Information Architects（零装饰、系统字体、内容优先）

---

## 一、项目概述

构建一个基于 Vue3 + FastAPI 的个人/小团队网址分类管理工具。核心功能：多级标签体系 + 网址 CRUD + 标签树筛选浏览 + 用户注册登录。

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
| 数据库 | SQLite（开发阶段） | 零配置、单文件 |
| 迁移 | Alembic | SQLAlchemy 标准迁移工具 |
| 认证 | JWT（python-jose + passlib） | 无状态、适合 SPA |
| 密码加密 | bcrypt（passlib） | 行业标准 |

---

## 三、标签体系设计（AI 总结）

基于互联网网站通用分类知识，设计 **12 个根分类 + 3 级深度 + 约 120 个标签节点**。

### 根分类（L1，12 个）

| # | 根分类 | slug | 说明 |
|---|---|---|---|
| 1 | 技术开发 | tech-dev | 编程、框架、工具、社区 |
| 2 | 新闻资讯 | news-media | 综合/科技/财经/体育新闻 |
| 3 | 社交媒体 | social | 社交网络、论坛、即时通讯 |
| 4 | 学习教育 | education | 在线课程、学术资源、培训 |
| 5 | 购物电商 | shopping | 综合/垂直电商、二手交易 |
| 6 | 金融财经 | finance | 银行、证券、支付、资讯 |
| 7 | 设计创意 | design | UI/UX、平面、插画、摄影 |
| 8 | 影音娱乐 | entertainment | 视频、音乐、游戏、动漫 |
| 9 | 工具效率 | tools | 笔记、任务、文档、AI 工具 |
| 10 | 科学学术 | science | 论文、期刊、科普、研究 |
| 11 | 生活服务 | life | 出行、餐饮、健康、房产 |
| 12 | 政府组织 | gov-org | 政府、国际组织、NGO |

### 二级标签示例（每个根分类 3-6 个）

以「技术开发」为例：

```
技术开发 (tech-dev)
├── 编程语言 (programming-languages)
│   ├── Python
│   ├── JavaScript / TypeScript
│   ├── Java / Kotlin
│   ├── Go
│   ├── Rust
│   └── C / C++
├── 前端开发 (frontend)
│   ├── Vue / Nuxt
│   ├── React / Next.js
│   ├── CSS / 样式
│   └── 构建工具
├── 后端开发 (backend)
│   ├── 框架
│   ├── 数据库
│   ├── API 设计
│   └── 消息队列
├── 开发工具 (dev-tools)
│   ├── Git / 版本控制
│   ├── IDE / 编辑器
│   └── CI/CD
├── 云计算 (cloud)
│   ├── AWS
│   ├── 阿里云 / 腾讯云
│   └── Vercel / Netlify
└── 技术社区 (tech-community)
    ├── GitHub
    ├── Stack Overflow
    └── 掘金 / 知乎
```

完整标签树（12 根 × 4~6 二级 × 2~4 三级）约 120~150 个节点，以 JSON 文件交付，可直接导入。

---

## 四、数据库设计

### 表结构

**users** — 用户表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 用户 ID |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | 登录邮箱 |
| username | VARCHAR(100) | NOT NULL | 显示名称 |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | DATETIME | DEFAULT NOW | 注册时间 |
| updated_at | DATETIME | ON UPDATE | 更新时间 |

**tags** — 标签表（自引用树形结构）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 标签 ID |
| name | VARCHAR(100) | NOT NULL | 标签名称 |
| slug | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | URL 友好标识 |
| parent_id | INTEGER | FK → tags.id, NULLABLE | 父标签 ID |
| level | INTEGER | NOT NULL, 1-5 | 层级深度 |
| sort_order | INTEGER | DEFAULT 0 | 同级排序 |
| description | VARCHAR(500) | NULLABLE | 标签说明 |
| created_at | DATETIME | DEFAULT NOW | — |

索引：`(parent_id)`, `(level)`, `(slug UNIQUE)`

**bookmarks** — 网址表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | 书签 ID |
| user_id | INTEGER | FK → users.id, NOT NULL, INDEX | 所属用户 |
| title | VARCHAR(500) | NOT NULL | 网页标题 |
| url | VARCHAR(2048) | NOT NULL | 完整 URL |
| description | TEXT | NULLABLE | 备注/描述 |
| favicon_url | VARCHAR(2048) | NULLABLE | 网站图标 |
| created_at | DATETIME | DEFAULT NOW | — |
| updated_at | DATETIME | ON UPDATE | — |

索引：`(user_id)`, `(user_id, created_at DESC)`

**bookmark_tags** — 书签-标签关联表（多对多）

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| bookmark_id | INTEGER | FK → bookmarks.id, ON DELETE CASCADE | — |
| tag_id | INTEGER | FK → tags.id, ON DELETE CASCADE | — |
| PK | — | (bookmark_id, tag_id) 联合主键 | — |

索引：`(tag_id)`, (bookmark_id, tag_id) 联合唯一

### ER 关系

```
users 1 ──── N bookmarks N ──── M bookmark_tags M ──── 1 tags
                                              │
                                        tags.parent_id ──► tags (self-ref tree)
```

---

## 五、API 接口设计

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | `/api/auth/register` | 注册 | 无 |
| POST | `/api/auth/login` | 登录，返回 JWT | 无 |
| GET | `/api/auth/me` | 获取当前用户信息 | JWT |

### 标签模块 `/api/tags`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/tags` | 获取完整标签树 | JWT |
| GET | `/api/tags/{id}` | 获取单个标签详情 | JWT |
| GET | `/api/tags/{id}/children` | 获取子标签 | JWT |

### 书签模块 `/api/bookmarks`

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | `/api/bookmarks` | 获取书签列表（支持筛选） | JWT |
| POST | `/api/bookmarks` | 创建书签 | JWT |
| GET | `/api/bookmarks/{id}` | 获取书签详情 | JWT |
| PUT | `/api/bookmarks/{id}` | 更新书签 | JWT |
| DELETE | `/api/bookmarks/{id}` | 删除书签 | JWT |

查询参数 `GET /api/bookmarks`：
- `tag_id` — 按标签筛选（含子标签递归）
- `search` — 标题/URL 模糊搜索
- `page` / `page_size` — 分页

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
    ├── TagTree.vue                 [左侧标签树面板]
    │   └── TagNode.vue             [递归树节点]
    ├── BookmarkList.vue            [右侧书签列表]
    │   └── BookmarkCard.vue        [单个书签卡片]
    └── BookmarkEditor.vue          [新增/编辑弹窗]
        └── TagSelector.vue         [多级标签选择器]
```

### 状态管理 (Pinia)

| Store | 职责 |
|---|---|
| `useAuthStore` | 用户登录状态、JWT 管理、自动登录 |
| `useTagStore` | 标签树数据、选中节点、展开状态 |
| `useBookmarkStore` | 书签列表、增删改查、筛选条件 |

### 设计风格落地（Information Architects）

- 系统字体栈：`-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`
- 传统蓝色链接 `#0000EE`，已访问 `#551A8B`
- 66 字符最佳行长，16px 基准字号
- 零装饰：无渐变、无阴影、无圆角（或最小 2px）
- 黑白灰 + 经典链接蓝 作为唯一强调色
- 布局：左侧标签树 260px + 右侧内容区，类双栏文档风格

---

## 七、开发阶段与预估

| 阶段 | 内容 | 产出 |
|---|---|---|
| **1. 项目初始化** | 创建前端 Vite + Vue3 项目、后端 FastAPI 项目骨架 | 项目目录、依赖配置 |
| **2. 数据库与标签** | 设计模型、Alembic 迁移、标签种子数据 JSON/SQL | 可迁移的数据库、完整标签树 |
| **3. 后端 API** | 认证接口 → 标签接口 → 书签 CRUD | 全部 REST API 可用 |
| **4. 前端核心** | 登录/注册 → 标签树 → 书签管理 → 筛选浏览 | 完整可交互界面 |
| **5. 联调验证** | 前后端联调、冒烟测试、交互验证 | 端到端工作流通过 |
| **6. 文档交付** | README、启动说明、验证清单 | 可交付文档 |

---

## 八、交付物清单

| # | 交付物 | 格式 |
|---|---|---|
| 1 | 项目开发计划（本文档，审批通过版） | Markdown |
| 2 | FastAPI 后端项目源码 | Python 项目目录 |
| 3 | Vue3 前端项目源码 | Vite + Vue3 项目目录 |
| 4 | 数据库迁移脚本（Alembic） | Python 迁移文件 |
| 5 | 初始标签种子数据（3+ 层级，约 120 节点） | JSON |
| 6 | 前后端启动与部署说明 | README.md |
| 7 | 数据库设计文档（含 ER 图说明） | Markdown |

---

## 九、需要确认的事项

请在审批时确认以下几点（均可按默认假设推进，有异议再调整）：

1. **数据库**：开发阶段用 SQLite，后续可平滑切换 PostgreSQL → ✅ 默认
2. **标签管理**：初始种子数据由 AI 生成后直接导入，前端不提供标签新增/编辑 → ✅ 默认（如需标签管理功能可后续加）
3. **书签权限**：每个用户只看自己的书签（按 user_id 隔离） → ✅ 默认
4. **标签筛选逻辑**：选中某标签后，展示该标签 + 所有子标签下的书签 → ✅ 默认
5. **邮箱验证**：无需邮箱验证，注册即可登录 → ✅ 默认（用户假设已明确）

---

> **请回复"批准"或"同意"以开始执行。如有调整意见请直接说明。**
