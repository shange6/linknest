BEGIN TRANSACTION;

CREATE TABLE "users" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile VARCHAR(20) UNIQUE,
        email VARCHAR(255) UNIQUE,
        username VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CHECK (mobile IS NOT NULL OR email IS NOT NULL)
      );

CREATE TABLE "tags" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        parent_id INTEGER REFERENCES "tags"(id),
        sort_order INTEGER DEFAULT 0,
        description TEXT,
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


INSERT INTO "users" VALUES(1,NULL,'shange@shange.com','shange','$2b$12$hmQ9rnrqycZpmOyjjUc0seF73MjjqzzXhrJzp7rHf838VvXM8PQ72','admin',1,'2026-07-14 07:47:45.275085','2026-07-14 07:47:45.275089');

CREATE INDEX ix_users_mobile ON users(mobile);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_tags_slug ON tags(slug);
CREATE INDEX ix_bookmarks_url ON bookmarks(url);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('users',4);
INSERT INTO "sqlite_sequence" VALUES('tags',504);
INSERT INTO "sqlite_sequence" VALUES('bookmarks',2298);
COMMIT;