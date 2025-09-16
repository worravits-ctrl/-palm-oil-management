#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script
สำหรับ migrate ข้อมูลจาก SQLite ไป Turso
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def migrate_sqlite_to_turso(sqlite_path='palm_farm.db'):
    """Migrate ข้อมูลจาก SQLite ไป Turso"""

    print("🌴 Database Migration: SQLite → Turso")
    print("=" * 50)

    # Check if SQLite database exists
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        return False

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    turso_url = os.getenv('TURSO_DATABASE_URL')
    turso_token = os.getenv('TURSO_AUTH_TOKEN')

    if not turso_url or not turso_token:
        print("❌ Turso environment variables not set!")
        return False

    try:
        from libsql_client import create_client

        # Connect to both databases
        print("🔌 Connecting to databases...")
        sqlite_conn = sqlite3.connect(sqlite_path)
        turso_client = create_client(url=turso_url, auth_token=turso_token)

        # Get all tables from SQLite
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()

        print(f"📋 Found {len(tables)} tables to migrate:")
        for table in tables:
            print(f"  - {table[0]}")

        # Migrate each table
        for table_tuple in tables:
            table_name = table_tuple[0]
            print(f"\n🔄 Migrating table: {table_name}")

            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            if not columns:
                print(f"⚠️  Skipping empty table: {table_name}")
                continue

            # Create table in Turso
            column_defs = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                col_notnull = "NOT NULL" if col[3] else ""
                col_default = f"DEFAULT {col[4]}" if col[4] else ""
                column_defs.append(f"{col_name} {col_type} {col_notnull} {col_default}".strip())

            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"

            try:
                turso_client.execute(create_sql)
                print(f"✅ Created table: {table_name}")
            except Exception as e:
                print(f"⚠️  Table creation failed: {e}")
                continue

            # Get all data from SQLite
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            if not rows:
                print(f"📭 No data in table: {table_name}")
                continue

            # Prepare insert statement
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders});"

            # Insert data in batches
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                try:
                    # Convert to list of tuples for Turso
                    turso_batch = [tuple(row) for row in batch]
                    turso_client.execute(insert_sql, turso_batch)
                    print(f"✅ Inserted {len(batch)} rows into {table_name}")
                except Exception as e:
                    print(f"❌ Batch insert failed: {e}")
                    # Try individual inserts
                    for row in batch:
                        try:
                            turso_client.execute(insert_sql, [tuple(row)])
                        except Exception as e2:
                            print(f"❌ Row insert failed: {e2}")

        sqlite_conn.close()
        print("\n🎉 Migration completed!")
        return True

    except ImportError:
        print("❌ libsql-client not installed!")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def backup_sqlite(sqlite_path='palm_farm.db'):
    """สร้าง backup ของ SQLite database"""
    import datetime

    backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    try:
        import shutil
        shutil.copy2(sqlite_path, backup_name)
        print(f"✅ Backup created: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def main():
    """Main function"""
    if len(sys.argv) > 1:
        sqlite_path = sys.argv[1]
    else:
        sqlite_path = 'palm_farm.db'

    print(f"🔍 Looking for SQLite database: {sqlite_path}")

    if not os.path.exists(sqlite_path):
        print(f"❌ Database not found: {sqlite_path}")
        print("Usage: python migrate_db.py [path_to_sqlite.db]")
        return 1

    # Create backup
    print("\n💾 Creating backup...")
    backup_file = backup_sqlite(sqlite_path)

    if not backup_file:
        print("❌ Backup failed, aborting migration!")
        return 1

    # Confirm migration
    print(f"\n⚠️  This will migrate data from {sqlite_path} to Turso")
    print(f"   Backup created: {backup_file}")
    response = input("Continue? (y/N): ").lower().strip()

    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        return 0

    # Perform migration
    success = migrate_sqlite_to_turso(sqlite_path)

    if success:
        print("\n🎉 Migration successful!")
        print("You can now use Turso database.")
        print(f"Original SQLite file backed up as: {backup_file}")
    else:
        print("\n❌ Migration failed!")
        print(f"You can restore from backup: {backup_file}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())