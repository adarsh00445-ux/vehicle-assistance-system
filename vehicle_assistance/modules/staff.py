from werkzeug.security import generate_password_hash, check_password_hash
from modules.database import get_connection

def create_staff(name, phone, email, password, specialization='General'):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    cursor.execute(
        """INSERT INTO staff (name, phone, email, password, specialization)
           VALUES (?, ?, ?, ?, ?)""",
        (name, phone, email, hashed_password, specialization)
    )

    staff_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return staff_id

def check_staff_login(email_or_phone, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM staff WHERE email = ? OR phone = ?",
        (email_or_phone, email_or_phone)
    )
    staff = cursor.fetchone()
    conn.close()

    if staff and check_password_hash(staff['password'], password):
        return staff

    return None

def check_staff_exists(email, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM staff WHERE email = ? OR phone = ?",
        (email, phone)
    )
    result = cursor.fetchone()
    conn.close()

    return result is not None

def get_staff_by_id(staff_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
    staff = cursor.fetchone()
    conn.close()

    return staff

def get_all_staff():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*,
        (SELECT COUNT(*) FROM bookings WHERE staff_id = s.id AND status = 'completed') as jobs_completed
        FROM staff s
        ORDER BY s.created_at DESC
    """)

    staff_list = cursor.fetchall()
    conn.close()

    return staff_list

def delete_staff(staff_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM staff WHERE id = ?", (staff_id,))
        staff_row = cursor.fetchone()
        if not staff_row:
            return False

        staff_name = staff_row['name']

        cursor.execute(
            """SELECT COUNT(*) FROM bookings
               WHERE staff_id = ? AND lower(status) IN ('accepted', 'completed')""",
            (staff_id,)
        )
        linked_jobs = cursor.fetchone()[0]

        if linked_jobs > 0:
            return False

        cursor.execute(
            """UPDATE bookings
               SET assigned_staff_name = ?
               WHERE staff_id = ?
                 AND (assigned_staff_name IS NULL OR assigned_staff_name = '')""",
            (staff_name, staff_id)
        )

        cursor.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_staff_stats(staff_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) as total FROM bookings WHERE staff_id = ?",
        (staff_id,)
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) as accepted FROM bookings WHERE staff_id = ? AND lower(status) = 'accepted'",
        (staff_id,)
    )
    accepted = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) as completed FROM bookings WHERE staff_id = ? AND lower(status) = 'completed'",
        (staff_id,)
    )
    completed = cursor.fetchone()[0]

    cursor.execute(
        """SELECT COUNT(*) as today FROM bookings
           WHERE staff_id = ? AND lower(status) = 'completed'
           AND date(completed_at) = date('now')""",
        (staff_id,)
    )
    today = cursor.fetchone()[0]

    cursor.execute(
        """SELECT COUNT(*) as week FROM bookings
           WHERE staff_id = ? AND lower(status) = 'completed'
           AND strftime('%Y%W', completed_at) = strftime('%Y%W', 'now')""",
        (staff_id,)
    )
    week = cursor.fetchone()[0]

    conn.close()

    return {
        'total': total,
        'accepted': accepted,
        'completed': completed,
        'today': today,
        'week': week,
        'pending': accepted
    }

def get_staff_jobs(staff_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            b.*,
            u.name as user_name,
            u.phone as user_phone,
            u.email as user_email
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        WHERE b.staff_id = ?
        ORDER BY b.created_at DESC
    """, (staff_id,))

    jobs = cursor.fetchall()
    conn.close()

    return jobs
