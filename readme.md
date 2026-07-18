# LinkNest — 网址分类管理网站

基于 Vue3 + FastAPI 的个人/小团队网址分类管理工具。

## 项目结构

```
linknest/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由 (auth, categories, bookmarks, user_bookmarks, user_history)
│   │   ├── core/            # 数据库配置、JWT 认证
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   └── main.py          # FastAPI 入口
│   ├── seed_data/           # 分类种子数据与导入脚本
│   ├── alembic/             # 数据库迁移配置
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # Axios 封装与 API 端点
│   │   ├── components/      # UI 组件
│   │   ├── router/          # Vue Router 配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── views/           # 页面视图
│   │   └── style.css        # Information Architects 风格样式
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── PLAN.md                  # 项目开发计划
```

---

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python seed_data/import_categories.py   # 导入初始分类数据
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

后端运行在 `http://localhost:8000`，API 文档自动生成在 `http://localhost:8000/docs`。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`。

---

## 功能概览

- **用户系统**：邮箱/手机注册 → JWT 登录 → 自动持久化。
- **多级分类**：17 个全局根分类，3 级最大深度，504 个预置全局分类节点。
- **书签库（全局）**：网址全局共享（唯一性校验），支持关联任意层级的全局分类（多选）。
- **分类筛选**：点击分类树节点，自动递归展示该分类及所有子分类下的书签。
- **搜索**：按标题或 URL 模糊搜索全局书签。
- **个性化收藏夹（User Bookmarks）**：用户可在全局书签的基础上建立个人收藏，并可附加独立的分类。
- **点击流历史（User History）**：自动统计和展示用户个人的网址访问点击记录。
- **分页**：20 条/页，自动分页导航。

---

## API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 无 |
| POST | `/api/auth/login` | 用户登录 | 无 |
| GET | `/api/auth/me` | 当前用户信息 | JWT |
| GET | `/api/categories` | 获取完整分类树 | JWT |
| GET | `/api/categories/{id}` | 单个分类详情 | JWT |
| GET | `/api/categories/{id}/children` | 子分类列表 | JWT |
| POST | `/api/categories` | 创建全局分类 | JWT (仅限 Admin) |
| PUT | `/api/categories/{id}` | 更新全局分类 | JWT (仅限 Admin) |
| DELETE | `/api/categories/{id}` | 删除全局分类 | JWT (仅限 Admin) |
| GET | `/api/bookmarks` | 全局书签列表 (category_id, search, page) | JWT |
| POST | `/api/bookmarks` | 创建全局书签 | JWT (仅限 Admin) |
| GET | `/api/bookmarks/{id}` | 全局书签详情 | JWT |
| PUT | `/api/bookmarks/{id}` | 更新全局书签 | JWT (仅限 Admin) |
| DELETE | `/api/bookmarks/{id}` | 删除全局书签 | JWT (仅限 Admin) |
| GET | `/api/user_bookmarks` | 用户收藏夹列表 | JWT |
| POST | `/api/user_bookmarks` | 添加书签到收藏夹 | JWT |
| DELETE | `/api/user_bookmarks/{bookmark_id}` | 从收藏夹移除 | JWT |
| GET | `/api/user_bookmarks/check/{bookmark_id}` | 检查书签是否已被收藏 | JWT |
| GET | `/api/user_history` | 用户点击历史列表 | JWT |
| POST | `/api/user_history` | 增加一次点击统计 | JWT |
| DELETE | `/api/user_history` | 清空用户点击历史 | JWT |

---

## 设计风格

采用 **03 Information Architects** 哲学：

- 系统字体栈（`-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`）
- 经典蓝色超链接 `#0000EE`
- 零装饰，内容优先层级（无多余渐变、阴影和圆角）
- 66 字符最佳阅读行长
- 双栏布局：左侧 260px 分类树 + 右侧书签列表

---

## 修改指南

### 分类数据
- 分类种子数据：`backend/seed_data/categories.json`
- 修改后需重新运行 `python backend/seed_data/import_categories.py`
- 注意：如果数据库已有分类，导入脚本会自动跳过

### 前端 API 地址
- 默认指向 `http://localhost:8000`
- 修改：`frontend/src/api/index.js` 中的 `baseURL`

### 密码加密
- 使用 bcrypt（passlib），`backend/app/core/auth.py`
- JWT 密钥默认 `linknest-dev-secret-key-change-in-production`，通过环境变量 `SECRET_KEY` 覆盖

### 用户数据隔离
- 全局书签（`bookmarks`）和全局分类（`categories`）在库中全局共享，不隔离。
- 用户通过 `user_bookmarks`（个人收藏夹）和 `user_history`（个人点击历史）实现隔离和个性化数据管理。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + Axios |
| 后端 | FastAPI + SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 认证 | JWT (python-jose) + bcrypt (passlib) |
| 迁移 | Alembic |

---

## 质量覆盖

- 表单校验：邮箱/手机号格式、密码最小 6 位、必填字段
- 错误处理：401 自动跳转登录页、网络错误提示
- 空状态：无书签/无匹配/无分类时显示引导文案
- 加载状态：分类树和书签列表均有 loading 指示器
- 确认删除：删除前弹出确认对话框
- 响应式布局：桌面为主，移动端适配基础布局
