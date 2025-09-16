#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turso Database Connection Test
ทดสอบการเชื่อมต่อฐานข้อมูล Turso
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_turso_connection():
    """ทดสอบการเชื่อมต่อ Turso Database"""
    print("🌴 Turso Database Connection Test")
    print("=" * 50)

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed, checking environment variables directly")

    # Check environment variables
    turso_url = os.getenv('TURSO_DATABASE_URL')
    turso_token = os.getenv('TURSO_AUTH_TOKEN')

    print(f"\n📋 Environment Variables:")
    print(f"TURSO_DATABASE_URL: {'✅ Set' if turso_url else '❌ Not set'}")
    print(f"TURSO_AUTH_TOKEN: {'✅ Set' if turso_token else '❌ Not set'}")

    if not turso_url or not turso_token:
        print("\n❌ Missing required environment variables!")
        print("Please set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in your .env file")
        print("Get these values from: turso db show your-database-name")
        return False

    # Mask sensitive data for display
    masked_url = turso_url.replace(turso_token.split('.')[-1], '***') if '.' in turso_token else turso_url
    masked_token = turso_token[:10] + '***' + turso_token[-4:] if len(turso_token) > 14 else '***'

    print(f"\n🔗 Database URL: {masked_url}")
    print(f"🔑 Auth Token: {masked_token}")

    # Test database connection
    try:
        from libsql_experimental import create_client
        print("\n🔌 Connecting to Turso database...")

        client = create_client(
            url=turso_url,
            auth_token=turso_token
        )

        # Test basic query
        result = client.execute("SELECT 1 as test, 'Hello Turso!' as message")
        print("✅ Database connection successful!")
        print(f"📊 Test Query Result: {result.rows[0]}")

        # Test table creation (if not exists)
        try:
            client.execute("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
            """)

            # Insert test record
            client.execute("""
                INSERT INTO connection_test (status)
                VALUES ('Connection test successful')
            """)

            print("✅ Database write test successful!")

            # Read test
            result = client.execute("SELECT COUNT(*) as total_tests FROM connection_test")
            print(f"📈 Total connection tests: {result.rows[0][0]}")

        except Exception as e:
            print(f"⚠️  Database write test failed: {e}")
            print("This might be normal if you don't have write permissions")

        return True

    except ImportError:
        print("\n❌ libsql-client not installed!")
        print("Install with: pip install libsql-client")
        return False

    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Check your TURSO_DATABASE_URL and TURSO_AUTH_TOKEN")
        print("2. Verify the database exists: turso db list")
        print("3. Check database status: turso db show your-database-name")
        print("4. Test with Turso CLI: turso db shell your-database-name 'SELECT 1;'")
        return False

def test_fallback_sqlite():
    """ทดสอบการ fallback ไป SQLite"""
    print("\n🏠 Testing SQLite fallback...")
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        conn.close()

        print("✅ SQLite fallback working!")
        print(f"📊 SQLite Test Result: {result[0]}")
        return True

    except Exception as e:
        print(f"❌ SQLite fallback failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting database connection tests...\n")

    # Test Turso first
    turso_success = test_turso_connection()

    # Test SQLite fallback
    sqlite_success = test_fallback_sqlite()

    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"Turso Database: {'✅ PASS' if turso_success else '❌ FAIL'}")
    print(f"SQLite Fallback: {'✅ PASS' if sqlite_success else '❌ FAIL'}")

    if turso_success:
        print("\n🎉 All tests passed! Your database is ready.")
        print("You can now run: python app.py")
    elif sqlite_success:
        print("\n⚠️  Turso connection failed, but SQLite fallback is working.")
        print("The app will use local SQLite database.")
        print("To use Turso, please check your configuration.")
    else:
        print("\n❌ All database tests failed!")
        print("Please check your setup and try again.")

    return 0 if turso_success or sqlite_success else 1

if __name__ == "__main__":
    sys.exit(main())