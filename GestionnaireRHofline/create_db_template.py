"""
Create a clean pre-migrated db_template.sqlite3 for fresh installs.
Dumps the schema from the dev database and creates a clean template.
Usage: python create_db_template.py [output_path]
"""
import os
import sys
import sqlite3

output = sys.argv[1] if len(sys.argv) > 1 else 'db_template.sqlite3'
source = 'db.sqlite3'

if not os.path.exists(source):
    print(f"ERREUR: {source} introuvable")
    sys.exit(1)

# Remove existing template
if os.path.exists(output):
    os.remove(output)

# Extract schema from dev database
src_conn = sqlite3.connect(source)
schema_statements = []
for row in src_conn.execute(
    "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY "
    "CASE type WHEN 'table' THEN 1 WHEN 'index' THEN 2 ELSE 3 END"
):
    schema_statements.append(row[0])
src_conn.close()

# Create template with schema only (no data)
dst_conn = sqlite3.connect(output)
for stmt in schema_statements:
    try:
        dst_conn.execute(stmt)
    except sqlite3.OperationalError:
        pass  # Skip duplicates or internal tables
dst_conn.commit()

# Copy django_migrations data so migrate knows which migrations are applied
src_conn = sqlite3.connect(source)
rows = src_conn.execute("SELECT app, name, applied FROM django_migrations").fetchall()
src_conn.close()
dst_conn.executemany(
    "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)", rows
)
dst_conn.commit()

# Verify
count = dst_conn.execute(
    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
).fetchone()[0]
has_session = dst_conn.execute(
    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='django_session'"
).fetchone()
dst_conn.close()

print(f"db_template.sqlite3 cree: {count} tables, django_session={'OK' if has_session else 'MANQUANT'}")
