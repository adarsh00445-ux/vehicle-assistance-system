from functools import wraps
import secrets
from flask import request, session, flash, redirect, url_for


def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def verify_csrf_token():
    token = session.get('csrf_token')
    form_token = request.form.get('csrf_token')
    if not token or token != form_token:
        flash('Security check failed. Please try again.', 'error')
        return False
    return True


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('staff_login'))

        from modules.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM staff WHERE id = ?', (session.get('staff_id'),))
        staff_exists = cursor.fetchone() is not None
        conn.close()

        if not staff_exists:
            session.clear()
            flash('Your staff account no longer exists. Please login again.', 'error')
            return redirect(url_for('staff_login'))

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
