"""Check database integrity after migration."""
import sqlite3

conn = sqlite3.connect('instance/gestao_editais_new.db')
c = conn.cursor()

print("=== PRAGMA integrity_check ===")
c.execute("PRAGMA integrity_check")
result = c.fetchone()
print(result[0])

print("\n=== PRAGMA foreign_key_check(bolsistas) ===")
c.execute("PRAGMA foreign_key_check(bolsistas)")
fk_errors = c.fetchall()
if fk_errors:
    print(f"Found {len(fk_errors)} foreign key violations:")
    for err in fk_errors[:5]:
        print(f"  {err}")
else:
    print("No foreign key violations found.")

print("\n=== bolsistas schema ===")
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bolsistas'")
row = c.fetchone()
if row:
    print(row[0][:800])

conn.close()
