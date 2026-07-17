import sqlite3, json

conn = sqlite3.connect('app/linknest.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_alembic%'")
tables = [row[0] for row in cursor.fetchall()]

db_schema = {"tables": [], "relationships": []}

for table in tables:
    cursor.execute(f'PRAGMA table_info("{table}")')
    cols = cursor.fetchall()
    columns = []
    for col in cols:
        columns.append({
            "cid": col[0], "name": col[1], "type": col[2],
            "notnull": bool(col[3]), "dflt_value": str(col[4]) if col[4] is not None else None,
            "pk": bool(col[5])
        })
    
    cursor.execute(f'PRAGMA foreign_key_list("{table}")')
    fks = cursor.fetchall()
    foreign_keys = []
    for fk in fks:
        foreign_keys.append({
            "id": fk[0], "seq": fk[1], "from_col": fk[3],
            "to_table": fk[2], "to_col": fk[4],
            "on_update": fk[5], "on_delete": fk[6]
        })
        db_schema["relationships"].append({
            "from_table": table, "from_col": fk[3],
            "to_table": fk[2], "to_col": fk[4],
            "on_delete": fk[6]
        })
    
    cursor.execute(f'PRAGMA index_list("{table}")')
    idxs = cursor.fetchall()
    indexes = []
    for idx in idxs:
        cursor.execute(f'PRAGMA index_info("{idx[1]}")')
        icols = cursor.fetchall()
        indexes.append({
            "name": idx[1], "unique": bool(idx[2]),
            "columns": [ic[2] for ic in icols]
        })
    
    cursor.execute(f'SELECT COUNT(*) FROM [{table}]')
    row_count = cursor.fetchone()[0]
    
    db_schema["tables"].append({
        "name": table, "columns": columns,
        "foreign_keys": foreign_keys, "indexes": indexes,
        "row_count": row_count
    })

conn.close()

with open('db_schema.json', 'w', encoding='utf-8') as f:
    json.dump(db_schema, f, ensure_ascii=False, indent=2)

print(json.dumps(db_schema, ensure_ascii=False, indent=2))
