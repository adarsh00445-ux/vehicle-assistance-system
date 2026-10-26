from werkzeug.security import generate_password_hash, check_password_hash
from modules.database import get_connection

def create_user(name, phone, email, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, phone, email, password) VALUES (?, ?, ?, ?)",
            (name, phone, email, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating user: {e}")
        raise
    finally:
        conn.close()

def check_user_login(email_or_phone, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ? OR phone = ?",
            (email_or_phone, email_or_phone)
        )
        user = cursor.fetchone()
        return user if user and check_password_hash(user['password'], password) else None
    except Exception as e:
        print(f"Error during login: {e}")
        return None
    finally:
        conn.close()

def check_user_exists(email, phone):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (email, phone))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()
