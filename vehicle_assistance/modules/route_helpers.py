import csv
import io
from flask import Response, render_template, session

from modules.validators import validate_phone, validate_email, validate_password
from modules.users import check_user_exists, get_user_by_id
from modules.email_service import generate_otp, save_otp, send_otp


def normalize_phone_input(value):
    value = value.strip()
    return '+91' + value if value.isdigit() and len(value) == 10 else value


def send_registration_otp(email):
    otp = generate_otp()
    save_otp(email, otp, 'registration')
    return send_otp(email, otp, 'Registration')


def validate_user_registration_form(form):
    name = form['name'].strip()
    phone = form['phone'].strip()
    email = form['email'].strip().lower()
    password = form['password']
    confirm_password = form['confirm_password']

    is_valid_phone, clean_phone = validate_phone(phone)
    if not is_valid_phone:
        return None, 'Please enter valid 10 digit phone number!'
    if not validate_email(email):
        return None, 'Please enter valid email address!'
    if not validate_password(password):
        return None, 'Password must be at least 6 characters!'
    if password != confirm_password:
        return None, 'Passwords do not match!'

    full_phone = '+91' + clean_phone
    if check_user_exists(email, full_phone):
        return None, 'Email or Phone already registered!'

    return {
        'name': name,
        'phone': full_phone,
        'email': email,
        'password': password,
    }, None


def get_current_user_data(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return None
    user = dict(user)
    return {
        'name': user.get('name', 'User'),
        'email': user.get('email', ''),
        'phone': user.get('phone', ''),
    }


def parse_booking_form(form):
    address = form.get('address', '').strip()
    alt_phone = form.get('alternate_phone', '').strip() or None
    prob_type = form.get('problem_type', '').strip()
    description = form.get('description', '').strip() or ''
    latitude = form.get('latitude', '').strip()
    longitude = form.get('longitude', '').strip()
    lat = float(latitude) if latitude else None
    lon = float(longitude) if longitude else None
    return {
        'address': address,
        'alternate_phone': alt_phone,
        'problem_type': prob_type,
        'description': description,
        'latitude': lat,
        'longitude': lon,
    }


def admin_name(default='Admin'):
    return session.get('admin_name', default)


def render_admin(template, **kwargs):
    kwargs.setdefault('name', admin_name())
    return render_template(template, **kwargs)


def send_staff_registration_otp(email):
    otp = generate_otp()
    save_otp(email, otp, 'staff_registration')
    return send_otp(email, otp, 'Staff Registration')


def csv_download(filename, headers, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    csv_data = output.getvalue()
    output.close()
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


def staff_label(data):
    return data.get('staff_display_name') or data.get('staff_name') or data.get('mechanic_name') or 'Unassigned'


def staff_name(default='Staff'):
    return session.get('staff_name', default)


def render_staff(template, **kwargs):
    kwargs.setdefault('name', staff_name())
    return render_template(template, **kwargs)


def rows_to_dicts(rows):
    return [dict(r) for r in rows]


def count_jobs_by_status(jobs_list, statuses):
    return {status: len([j for j in jobs_list if j.get('status') == status]) for status in statuses}
