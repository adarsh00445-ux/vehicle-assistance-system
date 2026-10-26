#!/usr/bin/env python

import sys

print("=" * 50)
print("Testing Vehicle Assistance System")
print("=" * 50)

print("\n[1/5] Testing database module...")
try:
    from modules.database import get_connection, test_connection
    from modules.db_init import check_database, init_database
    
    if not check_database():
        print("  [OK] Creating database...")
        init_database()
    else:
        print("  [OK] Database already initialized")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

print("\n[2/5] Testing admin module...")
try:
    from modules.admin import check_admin_login, get_admin_stats
    stats = get_admin_stats()
    print(f"  [OK] Admin stats: {len(stats)} stat fields")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

print("\n[3/5] Testing users module...")
try:
    from modules.users import check_user_exists, get_user_by_id
    print("  [OK] Users module loaded")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

print("\n[4/5] Testing bookings module...")
try:
    from modules.bookings import get_all_bookings, get_pending_bookings
    bookings = get_pending_bookings()
    print(f"  [OK] Bookings module loaded, {len(bookings)} pending bookings")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

print("\n[5/5] Testing Flask app...")
try:
    from app import app
    print("  [OK] Flask app imported successfully")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("[OK] All tests passed!")
print("=" * 50)
print("\nYou can now run: python app.py")
print("\nServer will start at: http://localhost:5000")
