import sqlite3, os, json

base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base, 'app', 'linknest.db')
html_path = os.path.join(base, 'db_schema_viewer.html')

# 1. Dump current schema
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
db_schema = {"tables": [], "relationships": []}
for table in ['users', 'tags', 'bookmarks', 'bookmarks_tags', 'user_favorites', 'user_history']:
    cursor.execute(f'PRAGMA table_info("{table}")')
    columns = [dict(cid=c[0], name=c[1], type=c[2], notnull=bool(c[3]), dflt_value=str(c[4]) if c[4] is not None else None, pk=bool(c[5])) for c in cursor.fetchall()]
    cursor.execute(f'PRAGMA foreign_key_list("{table}")')
    fks = [dict(id=f[0],seq=f[1],from_col=f[3],to_table=f[2],to_col=f[4],on_update=f[5],on_delete=f[6]) for f in cursor.fetchall()]
    for fk in fks:
        db_schema["relationships"].append(dict(from_table=table, from_col=fk["from_col"], to_table=fk["to_table"], to_col=fk["to_col"], on_delete=fk["on_delete"]))
    cursor.execute(f'PRAGMA index_list("{table}")')
    indexes = []
    for idx in cursor.fetchall():
        cursor.execute(f'PRAGMA index_info("{idx[1]}")')
        indexes.append(dict(name=idx[1], unique=bool(idx[2]), columns=[ic[2] for ic in cursor.fetchall()]))
    cursor.execute(f'SELECT COUNT(*) FROM [{table}]')
    db_schema["tables"].append(dict(name=table, columns=columns, foreign_keys=fks, indexes=indexes, row_count=cursor.fetchone()[0]))
conn.close()

# 2. Read current HTML and replace SCHEMA
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_schema_js = json.dumps(db_schema, ensure_ascii=False, indent=2)

# Find "const SCHEMA = ..." start and end to replace
start_marker = 'const SCHEMA = '
start = html.find(start_marker)
if start == -1:
    print("ERROR: SCHEMA not found")
    exit(1)

# Find the matching closing ";"
# Count braces
brace_count = 0
end = start + len(start_marker)
for i in range(end, len(html)):
    if html[i] == '{':
        brace_count += 1
    elif html[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end = i + 1
            if i + 1 < len(html) and html[i+1] == ';':
                end = i + 2
            break

if brace_count != 0:
    print("ERROR: unmatched braces in SCHEMA")
    exit(1)

before = html[:start]
after = html[end:]
html = before + start_marker + new_schema_js + ';\n' + after

# Replace COMMENTS
comments = {
    "users": {"id":"用户ID","mobile":"手机号","email":"登录邮箱","username":"显示名称","password":"bcrypt哈希密码","role":"角色(admin|user)","is_active":"激活状态","created_at":"注册时间","updated_at":"更新时间"},
    "tags": {"id":"标签ID","name":"标签名","slug":"URL标识","parent_id":"父标签(自引用)","sort_order":"同级排序","description":"标签说明","created_at":"创建时间","updated_at":"修改时间"},
    "bookmarks": {"id":"书签ID","title":"标题","url":"URL(唯一)","favicon_url":"favicon地址","description":"描述","created_at":"创建时间","updated_at":"修改时间"},
    "bookmarks_tags": {"bookmark_id":"FK→bookmarks.id","tag_id":"FK→tags.id"}
}
start_marker2 = 'const COMMENTS = '
start2 = html.find(start_marker2)
brace_count = 0
end2 = start2 + len(start_marker2)
for i in range(end2, len(html)):
    if html[i] == '{': brace_count += 1
    elif html[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end2 = i + 1
            if i+1 < len(html) and html[i+1] == ';': end2 = i+2
            break

new_comments_js = json.dumps(comments, ensure_ascii=False, indent=2)
html = html[:start2] + start_marker2 + new_comments_js + ';\n' + html[end2:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated db_schema_viewer.html")
print(f"Tables: {len(db_schema['tables'])}, Relationships: {len(db_schema['relationships'])}")
