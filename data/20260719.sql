BEGIN TRANSACTION;

-- 用户表
CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mobile VARCHAR(20),
	email VARCHAR(255),
	username VARCHAR(100) NOT NULL,
	password VARCHAR(255) NOT NULL,
	role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
	status BOOLEAN NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CHECK (mobile IS NOT NULL OR email IS NOT NULL),
	UNIQUE (mobile),
	UNIQUE (email)
);
CREATE INDEX ix_users_mobile ON users(mobile);
CREATE INDEX ix_users_email ON users(email);

--书签表
CREATE TABLE bookmarks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title_zh VARCHAR(500) NOT NULL,
	title_en VARCHAR(500),
	href VARCHAR(2048) NOT NULL UNIQUE,
	icon TEXT DEFAULT NULL,
	sort_zh INTEGER DEFAULT NULL,
	sort_en INTEGER DEFAULT NULL,
	status BOOLEAN NOT NULL DEFAULT 1,
	desc_zh TEXT,
	desc_en TEXT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_bookmarks_href ON bookmarks(href);

--分类表
CREATE TABLE categories (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name_zh VARCHAR(100) NOT NULL, 
	name_en VARCHAR(100), 
	slug VARCHAR(100) NOT NULL CHECK (slug NOT GLOB '*[^a-zA-Z0-9-]*'), 
	sort_zh INTEGER DEFAULT NULL, 
	sort_en INTEGER DEFAULT NULL, 
	parent_id INTEGER, 
	status BOOLEAN NOT NULL DEFAULT 1,
	desc_zh TEXT, 
	desc_en TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	FOREIGN KEY(parent_id) REFERENCES categories (id)
);
CREATE UNIQUE INDEX ix_categories_slug ON categories (slug);

-- 分类管理员关联表
CREATE TABLE category_managers (
	category_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	status BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY (category_id, user_id),
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

--书签分类关联表
CREATE TABLE bookmarks_categories (
	bookmark_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	PRIMARY KEY (bookmark_id, category_id), 
	FOREIGN KEY(bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE
);

--用户书签关联表
CREATE TABLE user_bookmarks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL, 
	title VARCHAR(500) NOT NULL,
	href VARCHAR(2048) NOT NULL UNIQUE,
	icon TEXT DEFAULT NULL,
	description TEXT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_user_bookmarks_user_id ON user_bookmarks(user_id);
CREATE INDEX ix_user_bookmarks_href ON user_bookmarks(href);

--用户分类关联表
CREATE TABLE user_categories (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	slug VARCHAR(100) NOT NULL CHECK (slug NOT GLOB '*[!a-zA-Z0-9-]*'), 
	parent_id INTEGER, 
	sort INTEGER, 
	description TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_user_category_slug UNIQUE (user_id, slug), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(parent_id) REFERENCES user_categories (id)
);
CREATE INDEX ix_user_categories_user_id ON user_categories (user_id);

--用户书签分类关联表
CREATE TABLE user_bookmarks_categories (
	bookmark_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	PRIMARY KEY (bookmark_id, category_id), 
	FOREIGN KEY(bookmark_id) REFERENCES user_bookmarks (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES user_categories (id) ON DELETE CASCADE
);

--用户历史关联表
CREATE TABLE user_history (
	user_id INTEGER NOT NULL,
	bookmark_id INTEGER NOT NULL,
	click_count INTEGER NOT NULL DEFAULT 1,
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id, bookmark_id),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
);
CREATE INDEX ix_history_user_count ON user_history(user_id, click_count DESC);

COMMIT;
