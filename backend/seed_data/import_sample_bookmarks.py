"""Script to generate and seed 10 sample bookmarks into database."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.init_db import init_db
from app.models.bookmark import Bookmark, BookmarkTranslation, Keyword
from app.models.category import Category

SAMPLE_BOOKMARKS = [
    {
        "href": "https://vuejs.org",
        "icon": "https://vuejs.org/logo.svg",
        "category_slugs": ["vue-nuxt", "frontend"],
        "keywords": ["Vue", "JavaScript", "前端框架", "UI"],
        "translations": [
            {
                "language_code": "zh",
                "name": "Vue.js 官网",
                "title": "Vue.js - 渐进式 JavaScript 框架",
                "description": "易学易用，性能出色，适用场景丰富的 JavaScript 框架。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "Vue.js Official",
                "title": "Vue.js - The Progressive JavaScript Framework",
                "description": "An approachable, performant and versatile framework for building web user interfaces.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://react.dev",
        "icon": "https://react.dev/favicon.ico",
        "category_slugs": ["react-nextjs", "frontend"],
        "keywords": ["React", "前端", "JSX", "JavaScript"],
        "translations": [
            {
                "language_code": "zh",
                "name": "React 官网",
                "title": "React - 用于构建 Web 和原生交互界面的库",
                "description": "使用组件方式构建 Web 与原生应用的 JavaScript 界面库。",
                "sort": 2,
            },
            {
                "language_code": "en",
                "name": "React Official",
                "title": "React - The library for web and native user interfaces",
                "description": "Build web and native user interfaces using components.",
                "sort": 2,
            },
        ],
    },
    {
        "href": "https://fastapi.tiangolo.com",
        "icon": "https://fastapi.tiangolo.com/img/favicon.png",
        "category_slugs": ["backend-frameworks", "python"],
        "keywords": ["Python", "FastAPI", "后端", "API"],
        "translations": [
            {
                "language_code": "zh",
                "name": "FastAPI 官网",
                "title": "FastAPI 现代高效 Python Web 框架",
                "description": "基于标准 Python 类型提示的高性能 Python Web 框架。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "FastAPI Documentation",
                "title": "FastAPI framework, high performance, easy to learn",
                "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://developer.mozilla.org",
        "icon": "https://developer.mozilla.org/favicon-48x48.png",
        "category_slugs": ["frontend", "dev-tools"],
        "keywords": ["MDN", "Web", "HTML", "CSS", "JavaScript"],
        "translations": [
            {
                "language_code": "zh",
                "name": "MDN 开发者文档",
                "title": "MDN Web Docs - HTML, CSS, JavaScript 权威指南",
                "description": "面向 Web 开发者的开放文档，包含 HTML、CSS 和 JavaScript 教程与 API 规范。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "MDN Web Docs",
                "title": "MDN Web Docs - Resources for Developers",
                "description": "The MDN Web Docs site provides information about Open Web technologies including HTML, CSS, and APIs.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://github.com",
        "icon": "https://github.githubassets.com/favicons/favicon.png",
        "category_slugs": ["git-version-control", "dev-tools"],
        "keywords": ["GitHub", "Git", "开源", "代码托管"],
        "translations": [
            {
                "language_code": "zh",
                "name": "GitHub",
                "title": "GitHub - 全球最大的开源代码托管与协作平台",
                "description": "汇聚全球数千万开发者的开源代码托管与敏捷开发平台。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "GitHub",
                "title": "GitHub: Let's build from here",
                "description": "GitHub is where over 100 million developers shape the future of software, together.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://www.sqlite.org",
        "icon": "https://www.sqlite.org/favicon.ico",
        "category_slugs": ["database", "backend"],
        "keywords": ["SQLite", "数据库", "嵌入式", "SQL"],
        "translations": [
            {
                "language_code": "zh",
                "name": "SQLite 官网",
                "title": "SQLite 嵌入式 SQL 数据库引擎",
                "description": "无需独立服务器进程、轻量级且广为使用的 C 语言 SQL 数据库。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "SQLite Home Page",
                "title": "SQLite Self-Contained Serverless Database Engine",
                "description": "SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://vitejs.dev",
        "icon": "https://vitejs.dev/logo.svg",
        "category_slugs": ["build-tools", "frontend"],
        "keywords": ["Vite", "构建工具", "打包", "ESModule"],
        "translations": [
            {
                "language_code": "zh",
                "name": "Vite 官方构建工具",
                "title": "Vite - 下一代前端开发与打包工具",
                "description": "基于原生 ES 模块的高性能前端开发服务器与构建工具。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "Vite Next Generation Frontend Tooling",
                "title": "Vite - Next Generation Frontend Tooling",
                "description": "Get ready for a development environment that can finally keep up with you.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://tailwindcss.com",
        "icon": "https://tailwindcss.com/favicons/favicon.ico",
        "category_slugs": ["css-styling", "frontend"],
        "keywords": ["Tailwind", "CSS", "样式", "前端"],
        "translations": [
            {
                "language_code": "zh",
                "name": "Tailwind CSS 官网",
                "title": "Tailwind CSS - 原子化 CSS 样式框架",
                "description": "无需离开 HTML 即可快速构建现代响应式 UI 的 Utility-First CSS 框架。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "Tailwind CSS",
                "title": "Tailwind CSS - Rapidly build modern websites without ever leaving your HTML",
                "description": "A utility-first CSS framework packed with classes that can be composed to build any design.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://www.python.org",
        "icon": "https://www.python.org/static/favicon.ico",
        "category_slugs": ["python", "programming-languages"],
        "keywords": ["Python", "编程语言", "后端", "数据分析"],
        "translations": [
            {
                "language_code": "zh",
                "name": "Python 官方网站",
                "title": "Welcome to Python.org",
                "description": "Python 是一种易于学习且功能强大的面向对象编程语言。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "Python Official",
                "title": "Welcome to Python.org",
                "description": "Python is a programming language that lets you work quickly and integrate systems more effectively.",
                "sort": 1,
            },
        ],
    },
    {
        "href": "https://stackoverflow.com",
        "icon": "https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico",
        "category_slugs": ["dev-tools", "frontend"],
        "keywords": ["StackOverflow", "问答", "开发者", "社区"],
        "translations": [
            {
                "language_code": "zh",
                "name": "Stack Overflow",
                "title": "Stack Overflow - 全球开发者问答社区",
                "description": "程序员解决代码疑难杂症、技术问答与交流的专业社区。",
                "sort": 1,
            },
            {
                "language_code": "en",
                "name": "Stack Overflow",
                "title": "Stack Overflow - Where Developers Learn, Share, & Build Careers",
                "description": "Every month, over 50 million developers come to Stack Overflow to learn, share their knowledge, and build their careers.",
                "sort": 1,
            },
        ],
    },
]


def seed_sample_bookmarks():
    init_db()
    db = SessionLocal()

    inserted_count = 0
    for data in SAMPLE_BOOKMARKS:
        existing = db.query(Bookmark).filter(Bookmark.href == data["href"]).first()
        if existing:
            print(f"Bookmark {data['href']} already exists. Skipping.")
            continue

        bookmark = Bookmark(
            href=data["href"],
            icon=data["icon"],
            status=True,
        )

        cat_objs = (
            db.query(Category)
            .filter(Category.slug.in_(data["category_slugs"]))
            .all()
        )
        bookmark.categories = cat_objs

        kw_objs = []
        for word in data["keywords"]:
            word_clean = word.strip()
            kw = db.query(Keyword).filter(Keyword.word == word_clean).first()
            if not kw:
                kw = Keyword(word=word_clean)
                db.add(kw)
                db.flush()
            kw_objs.append(kw)
        bookmark.keywords = kw_objs

        for tr in data["translations"]:
            t_obj = BookmarkTranslation(
                language_code=tr["language_code"],
                name=tr["name"],
                title=tr["title"],
                description=tr["description"],
                sort=tr["sort"],
            )
            bookmark.translations.append(t_obj)

        db.add(bookmark)
        inserted_count += 1

    db.commit()
    print(f"Successfully seeded {inserted_count} sample bookmarks.")
    db.close()


if __name__ == "__main__":
    seed_sample_bookmarks()
