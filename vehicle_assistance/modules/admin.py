from werkzeug.security import check_password_hash
from modules.database import get_connection

def check_admin_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE username = ?", (username,))
    admin = cursor.fetchone()
    conn.close()

    if admin:

        if check_password_hash(admin['password'], password):
            return admin

    return None

def get_admin_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staff")
    total_staff = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute(
        """SELECT COUNT(*) FROM bookings
           WHERE status = 'completed' AND date(completed_at) = date('now')"""
    )
    today_services = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'completed'")
    completed_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
    pending_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'accepted'")
    in_progress = cursor.fetchone()[0]

    conn.close()

    return {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'today_services': today_services,
        'total_services': completed_bookings,
        'pending_services': pending_bookings,
        'in_progress': in_progress
    }
