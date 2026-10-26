import sqlite3
import os
from config import DB_PATH


def ensure_schema_updates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'")
        if not cursor.fetchone():
            conn.close()
            return True

        cursor.execute("PRAGMA table_info(bookings)")
        booking_cols = {row[1] for row in cursor.fetchall()}

        if 'latitude' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN latitude REAL")

        if 'longitude' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN longitude REAL")

        if 'assigned_staff_name' not in booking_cols:
            cursor.execute("ALTER TABLE bookings ADD COLUMN assigned_staff_name TEXT")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_chat_user_id'")
        if not cursor.fetchone():
            cursor.execute('CREATE INDEX idx_chat_user_id ON chat_history(user_id)')
        cursor.execute("""
            UPDATE bookings
            SET assigned_staff_name = (
                SELECT s.name FROM staff s WHERE s.id = bookings.staff_id
            )
            WHERE staff_id IS NOT NULL
              AND (assigned_staff_name IS NULL OR assigned_staff_name = '')
              AND EXISTS (SELECT 1 FROM staff s2 WHERE s2.id = bookings.staff_id)
        """)

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Schema update error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def init_database():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users')")
        if cursor.fetchone():
            print("[OK] Database already initialized")
            return True
        
        print("Initializing database...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                specialization TEXT DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                registered_phone TEXT NOT NULL,
                alternate_phone TEXT,
                problem_type TEXT NOT NULL,
                problem_description TEXT,
                status TEXT DEFAULT 'pending',
                staff_id INTEGER,
                assigned_staff_name TEXT,
                completion_otp TEXT,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE SET NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE otp_verify (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                otp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('CREATE INDEX idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX idx_users_phone ON users(phone)')
        cursor.execute('CREATE INDEX idx_staff_email ON staff(email)')
        cursor.execute('CREATE INDEX idx_bookings_user_id ON bookings(user_id)')
        cursor.execute('CREATE INDEX idx_bookings_staff_id ON bookings(staff_id)')
        cursor.execute('CREATE INDEX idx_chat_user_id ON chat_history(user_id)')
        
        conn.commit()
        print("[OK] Database initialized successfully")
        print(f"[OK] Database file: {DB_PATH}")
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def check_database():
    if not os.path.exists(DB_PATH):
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False
