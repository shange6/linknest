# LinkNest — 网址分类管理网站

基于 Vue3 + FastAPI 的个人/小团队网址分类管理工具。

## 项目结构

```
linknest/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由 (auth, tags, bookmarks)
│   │   ├── core/            # 数据库配置、JWT 认证
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   └── main.py          # FastAPI 入口
│   ├── seed_data/           # 标签种子数据与导入脚本
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

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python seed_data/import_tags.py   # 导入 174 个初始标签
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

## 功能概览

- **用户系统**：邮箱注册 → JWT 登录 → 自动持久化
- **多级标签**：12 个根分类，3 级深度，174 个预置标签节点
- **书签管理**：添加/编辑/删除书签，关联任意层级标签（多选）
- **标签筛选**：点击标签树节点，自动递归展示该标签及所有子标签下的书签
- **搜索**：按标题或 URL 模糊搜索
- **分页**：20 条/页，自动分页导航

## API 接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 注册 | 无 |
| POST | `/api/auth/login` | 登录 | 无 |
| GET | `/api/auth/me` | 当前用户信息 | JWT |
| GET | `/api/tags` | 完整标签树 | JWT |
| GET | `/api/tags/{id}` | 单个标签详情 | JWT |
| GET | `/api/tags/{id}/children` | 子标签列表 | JWT |
| GET | `/api/bookmarks` | 书签列表 (tag_id, search, page) | JWT |
| POST | `/api/bookmarks` | 创建书签 | JWT |
| GET | `/api/bookmarks/{id}` | 书签详情 | JWT |
| PUT | `/api/bookmarks/{id}` | 更新书签 | JWT |
| DELETE | `/api/bookmarks/{id}` | 删除书签 | JWT |

## 设计风格

采用 **03 Information Architects** 哲学：

- 系统字体栈（PingFang SC / Microsoft YaHei / Segoe UI）
- 经典蓝色超链接 `#0000EE`
- 零装饰，内容优先层级
- 66 字符最佳阅读行长
- 双栏布局：左侧 260px 标签树 + 右侧书签列表

## 修改指南

### 标签数据
- 标签种子数据：`backend/seed_data/tags.json`
- 修改后需重新运行 `python backend/seed_data/import_tags.py`
- 注意：如果数据库已有标签，导入脚本会自动跳过

### 前端 API 地址
- 默认指向 `http://localhost:8000`
- 修改：`frontend/src/api/index.js` 中的 `baseURL`

### 密码加密
- 使用 bcrypt（passlib），`backend/app/core/auth.py`
- JWT 密钥默认 `linknest-dev-secret-key-change-in-production`，通过环境变量 `SECRET_KEY` 覆盖

### 用户数据隔离
- 每个用户只能看到自己的书签（按 `user_id` 过滤）
- 标签为全局共享

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + Axios |
| 后端 | FastAPI + SQLAlchemy 2.0 |
| 数据库 | SQLite（开发） |
| 认证 | JWT (python-jose) + bcrypt (passlib) |
| 迁移 | Alembic |

## 质量覆盖

- 表单校验：邮箱格式、密码最小 6 位、必填字段
- 错误处理：401 自动跳转登录页、网络错误提示
- 空状态：无书签/无匹配/无标签时显示引导文案
- 加载状态：标签树和书签列表均有 loading 指示器
- 确认删除：删除前弹出确认对话框
- 响应式布局：桌面为主，移动端适配基础布局
