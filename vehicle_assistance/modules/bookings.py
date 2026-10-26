from modules.database import get_connection

def create_booking(user_id, address, registered_phone,
                   alternate_phone=None, problem_type='', description='',
                   latitude=None, longitude=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bookings
            (user_id, address, registered_phone,
             alternate_phone, problem_type,
             problem_description, status, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (
            user_id,
            address,
            registered_phone,
            alternate_phone,
            problem_type,
            description,
            latitude,
            longitude
        ))
        booking_id = cursor.lastrowid
        conn.commit()
        return booking_id
    except Exception as e:
        conn.rollback()
        print(f"Error creating booking: {e}")
        raise
    finally:
        conn.close()

def get_user_bookings(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.*,
                u.name as user_name,
                u.phone as user_phone,
                u.email as user_email,
                s.name as mechanic_name,
                s.phone as mechanic_phone,
                s.specialization as mechanic_specialization
            FROM bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN staff s ON b.staff_id = s.id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
        """, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching user bookings: {e}")
        return []
    finally:
        conn.close()

def get_pending_bookings():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.*,
                u.name as user_name,
                u.phone as user_phone,
                u.email as user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            WHERE b.status = 'pending'
            ORDER BY b.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching pending bookings: {e}")
        return []
    finally:
        conn.close()

def get_booking_by_id(booking_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.*,
                u.name as user_name,
                u.phone as user_phone,
                u.email as user_email
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ?
        """, (booking_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching booking: {e}")
        return None
    finally:
        conn.close()

def accept_booking(booking_id, staff_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'accepted',
                staff_id = ?,
                assigned_staff_name = (SELECT name FROM staff WHERE id = ?),
                accepted_at = datetime('now')
            WHERE id = ?
            AND status = 'pending'
        """, (staff_id, staff_id, booking_id))
        accepted = cursor.rowcount > 0
        conn.commit()
        return accepted
    except Exception as e:
        conn.rollback()
        print(f"Error accepting booking: {e}")
        return False
    finally:
        conn.close()

def cancel_booking(booking_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'cancelled',
                staff_id = NULL
            WHERE id = ?
            AND status IN ('pending', 'accepted')
        """, (booking_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error cancelling booking: {e}")
        return False
    finally:
        conn.close()

def reset_booking_to_pending(booking_id):
    """Reset an accepted booking back to pending (staff cancellation)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'pending',
                staff_id = NULL,
                completion_otp = NULL
            WHERE id = ?
            AND status = 'accepted'
        """, (booking_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error resetting booking to pending: {e}")
        return False
    finally:
        conn.close()

def set_completion_otp(booking_id, otp):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET completion_otp = ?
            WHERE id = ?
            AND status = 'accepted'
        """, (otp, booking_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error setting completion OTP: {e}")
        return False
    finally:
        conn.close()

def complete_booking(booking_id, otp):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM bookings
            WHERE id = ?
            AND completion_otp = ?
            AND status = 'accepted'
        """, (booking_id, otp))
        booking = cursor.fetchone()

        if booking:
            cursor.execute("""
                UPDATE bookings
                SET status = 'completed',
                    completed_at = datetime('now'),
                    completion_otp = NULL
                WHERE id = ?
            """, (booking_id,))
            conn.commit()
            return True
        return False
    except Exception as e:
        conn.rollback()
        print(f"Error completing booking: {e}")
        return False
    finally:
        conn.close()

def get_all_bookings():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.*,
                u.name as user_name,
                u.phone as user_phone,
                u.email as user_email,
                s.name as mechanic_name,
                s.phone as mechanic_phone,
                s.specialization as mechanic_specialization,
                COALESCE(
                    s.name,
                    b.assigned_staff_name,
                    CASE
                        WHEN b.staff_id IS NOT NULL THEN 'Deleted Staff'
                        ELSE 'Unassigned'
                    END
                ) as staff_display_name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            LEFT JOIN staff s ON b.staff_id = s.id
            ORDER BY b.created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching all bookings: {e}")
        return []
    finally:
        conn.close()

def cancel_user_booking(booking_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = 'cancelled'
            WHERE id = ?
            AND user_id = ?
            AND status IN ('pending', 'accepted')
        """, (booking_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error cancelling user booking: {e}")
        return False
    finally:
        conn.close()

def get_service_history():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                b.*,
                u.name as user_name,
                u.phone as user_phone,
                s.name as staff_name,
                s.phone as staff_phone,
                COALESCE(
                    s.name,
                    b.assigned_staff_name,
                    CASE
                        WHEN b.staff_id IS NOT NULL THEN 'Deleted Staff'
                        ELSE 'Unassigned'
                    END
                ) as staff_display_name
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            LEFT JOIN staff s ON b.staff_id = s.id
            WHERE b.status = 'completed'
            ORDER BY b.completed_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching service history: {e}")
        return []
    finally:
        conn.close()
