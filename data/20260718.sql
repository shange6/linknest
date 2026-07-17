BEGIN TRANSACTION;
CREATE TABLE "users" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile VARCHAR(20),
        email VARCHAR(255),
        username VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CHECK (mobile IS NOT NULL OR email IS NOT NULL),
        UNIQUE (mobile),
        UNIQUE (email)
      );
CREATE TABLE "tags" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        parent_id INTEGER REFERENCES "tags"(id),
        sort_order INTEGER DEFAULT 0,
        description VARCHAR(500),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
CREATE TABLE "bookmarks" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(500) NOT NULL,
        url VARCHAR(2048) NOT NULL UNIQUE,
        favicon_url VARCHAR(2048),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
CREATE TABLE "bookmarks_tags" (
	bookmark_id INTEGER NOT NULL, 
	tag_id INTEGER NOT NULL, 
	PRIMARY KEY (bookmark_id, tag_id), 
	FOREIGN KEY(bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE, 
	FOREIGN KEY(tag_id) REFERENCES tags (id) ON DELETE CASCADE
);
CREATE TABLE user_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) NOT NULL,
        parent_id INTEGER REFERENCES user_tags(id),
        sort_order INTEGER DEFAULT 0,
        description VARCHAR(500),
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (user_id, slug)
      );
CREATE TABLE "user_bookmarks" (
        user_id INTEGER NOT NULL,
        bookmark_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, bookmark_id, tag_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
      );
CREATE TABLE "user_history" (
        user_id INTEGER NOT NULL,
        bookmark_id INTEGER NOT NULL,
        click_count INTEGER NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, bookmark_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE
      );

INSERT INTO "users" VALUES(1,NULL,'shange@shange.com','shange','$2b$12$hmQ9rnrqycZpmOyjjUc0seF73MjjqzzXhrJzp7rHf838VvXM8PQ72','admin',1,'2026-07-14 07:47:45.275085','2026-07-14 07:47:45.275089');

CREATE INDEX ix_users_mobile ON users(mobile);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_tags_slug ON tags(slug);
CREATE INDEX ix_bookmarks_url ON bookmarks(url);
CREATE INDEX ix_history_user_count ON user_history(user_id, click_count DESC);
CREATE INDEX ix_user_tags_user ON user_tags(user_id);
CREATE INDEX ix_user_tags_parent ON user_tags(parent_id);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',4);
INSERT INTO "sqlite_sequence" VALUES('tags',504);
INSERT INTO "sqlite_sequence" VALUES('bookmarks',2298);
COMMIT;
