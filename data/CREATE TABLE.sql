-- 确保 SQLite 版本 ≥ 3.8.3（支持 CHECK 中的 GLOB）


BEGIN TRANSACTION;
PRAGMA foreign_keys = ON;

-- 用户表
CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mobile VARCHAR(20) UNIQUE,
	email VARCHAR(255) UNIQUE,
	username VARCHAR(100) NOT NULL,
	password VARCHAR(255) NOT NULL,
	role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CHECK (mobile IS NOT NULL OR email IS NOT NULL)
);

--分类表
CREATE TABLE categories (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	slug VARCHAR(100) NOT NULL UNIQUE CHECK (slug NOT GLOB '*[^a-z0-9-]*'), 
	parent_id INTEGER, 
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (parent_id) REFERENCES categories (id)
);

--分类翻译表
CREATE TABLE category_translations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	category_id INTEGER NOT NULL,
	language_code VARCHAR(10) NOT NULL, 					-- 'zh','en','ja'
	sort INTEGER DEFAULT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT DEFAULT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	UNIQUE (category_id, language_code), 					-- 同一个分类每种语言只一条
	FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- 分类管理员关联表
CREATE TABLE category_managers (
	category_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (category_id, user_id),
	FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
	FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX idx_category_managers_user_id ON category_managers(user_id);

--书签表
CREATE TABLE bookmarks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	href TEXT NOT NULL UNIQUE,
	icon TEXT DEFAULT NULL,
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--书签翻译表
CREATE TABLE bookmark_translations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	bookmark_id INTEGER NOT NULL,
	language_code VARCHAR(10) NOT NULL,						-- 'zh' / 'en'
	sort INTEGER DEFAULT NULL,
	name VARCHAR(100) NOT NULL,
	title VARCHAR(255) NOT NULL,
	description TEXT DEFAULT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	UNIQUE (bookmark_id, language_code),
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
);

--关键词表
CREATE TABLE keywords (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	word VARCHAR(20) NOT NULL UNIQUE,						-- 关键词，唯一约束
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--书签关键词关联表
CREATE TABLE bookmark_keywords (
	bookmark_id INTEGER NOT NULL,
	keyword_id INTEGER NOT NULL,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (bookmark_id, keyword_id),
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
	FOREIGN KEY (keyword_id) REFERENCES keywords(id) ON DELETE CASCADE
);
CREATE INDEX idx_bookmark_keywords_keyword_id ON bookmark_keywords(keyword_id);

--书签分类关联表
CREATE TABLE categories_bookmarks (
	category_id INTEGER NOT NULL,
	bookmark_id INTEGER NOT NULL,  
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (category_id, bookmark_id), 
	FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE
);
CREATE INDEX idx_categories_bookmarks_bookmark_id ON categories_bookmarks(bookmark_id);

--用户分类关联表
CREATE TABLE user_categories (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	slug VARCHAR(100) NOT NULL CHECK (slug NOT GLOB '*[^a-z0-9-]*'), 
	parent_id INTEGER, 
	sort INTEGER DEFAULT NULL, 
	description TEXT, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT uq_user_category_slug UNIQUE (user_id, slug), 
	FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY (parent_id) REFERENCES user_categories (id)
);
CREATE INDEX ix_user_categories_user_id ON user_categories (user_id);

--用户书签关联表
CREATE TABLE user_bookmarks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL,
	href TEXT NOT NULL,
	icon TEXT DEFAULT NULL,
	description TEXT,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_user_bookmarks_user_id ON user_bookmarks(user_id);
CREATE INDEX ix_user_bookmarks_href ON user_bookmarks(href);

--用户分类书签关联表
CREATE TABLE user_categories_bookmarks (			-- 用户分类中收藏的用户自定义书签
	user_id INTEGER NOT NULL, 
	user_category_id INTEGER NOT NULL, 
	user_bookmark_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_category_id, user_bookmark_id), 
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (user_category_id) REFERENCES user_categories (id) ON DELETE CASCADE,
	FOREIGN KEY (user_bookmark_id) REFERENCES user_bookmarks (id) ON DELETE CASCADE
);
CREATE INDEX idx_user_categories_bookmarks_user_id ON user_categories_bookmarks(user_id);
CREATE INDEX idx_user_categories_bookmarks_user_bookmark_id ON user_categories_bookmarks(user_bookmark_id);

--用户分类全局书签关联表
CREATE TABLE user_categories_global_bookmarks (		-- 用户分类中收藏的全局书签
	user_id INTEGER NOT NULL, 
	user_category_id INTEGER NOT NULL, 
	bookmark_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_category_id, bookmark_id), 
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (user_category_id) REFERENCES user_categories (id) ON DELETE CASCADE,
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE
);
CREATE INDEX idx_user_categories_global_bookmarks_bookmark_id ON user_categories_global_bookmarks(bookmark_id);

--用户历史关联表
CREATE TABLE user_history_bookmarks (
	user_id INTEGER NOT NULL,
	user_bookmark_id INTEGER NOT NULL,
	click_count INTEGER NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id, user_bookmark_id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (user_bookmark_id) REFERENCES user_bookmarks(id) ON DELETE CASCADE
);
CREATE INDEX idx_user_history_bookmarks_bookmark_id ON user_history_bookmarks(user_bookmark_id);

--用户历史关联表
CREATE TABLE user_history_global_bookmarks (
	user_id INTEGER NOT NULL,
	bookmark_id INTEGER NOT NULL,
	click_count INTEGER NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id, bookmark_id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
);
CREATE INDEX idx_user_history_global_bookmarks_bookmark_id ON user_history_global_bookmarks(bookmark_id);

COMMIT;
