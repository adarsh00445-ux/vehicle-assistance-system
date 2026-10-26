from flask import request, redirect, session, url_for, flash
from modules.validators import validate_phone
from modules.staff import create_staff, check_staff_exists, get_all_staff, delete_staff
from modules.bookings import get_all_bookings, get_service_history, cancel_booking
from modules.admin import check_admin_login, get_admin_stats
from modules.email_service import verify_otp
from modules.web_utils import admin_required
from modules.route_helpers import render_admin, send_staff_registration_otp, csv_download, staff_label


def register_admin_routes(app):
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form['username'].strip()
            password = request.form['password']

            admin = check_admin_login(username, password)

            if admin:
                admin = dict(admin)  # Convert Row to dict
                session['admin_id'] = admin['id']
                session['admin_name'] = username
                flash('Welcome Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            flash('Invalid credentials!', 'error')

        return render_admin('admin/login.html')

    @app.route('/admin/cancel-booking/<int:booking_id>', methods=['POST'])
    @admin_required
    def admin_cancel_booking(booking_id):
        if cancel_booking(booking_id):
            flash('Booking cancelled successfully!', 'success')
        else:
            flash('Cannot cancel completed booking!', 'error')

        return redirect(url_for('admin_all_bookings'))

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        stats = get_admin_stats()
        return render_admin('admin/dashboard.html', stats=stats)

    @app.route('/admin/register-staff', methods=['GET', 'POST'])
    @admin_required
    def admin_register_staff():
        if request.method == 'POST':
            name = request.form['name'].strip()
            phone = request.form['phone'].strip()
            email = request.form['email'].strip().lower()
            password = request.form['password']
            specialization = request.form.get('specialization', 'General')

            is_valid_phone, clean_phone = validate_phone(phone)
            if not is_valid_phone:
                flash('Please enter valid 10 digit phone!', 'error')
                return render_admin('admin/register_staff.html')

            if check_staff_exists(email, '+91' + clean_phone):
                flash('Email or Phone already registered!', 'error')
                return render_admin('admin/register_staff.html')

            session['temp_staff'] = {
                'name': name,
                'phone': '+91' + clean_phone,
                'email': email,
                'password': password,
                'specialization': specialization
            }

            if send_staff_registration_otp(email):
                flash('OTP sent to staff email!', 'success')
                return redirect(url_for('admin_verify_staff_otp'))
            flash('Failed to send OTP!', 'error')

        return render_admin('admin/register_staff.html')

    @app.route('/admin/verify-staff-otp', methods=['GET', 'POST'])
    @admin_required
    def admin_verify_staff_otp():
        if 'temp_staff' not in session:
            return redirect(url_for('admin_register_staff'))

        if request.method == 'POST':
            otp = request.form['otp'].strip()
            temp_staff = session['temp_staff']

            if verify_otp(temp_staff['email'], otp):
                create_staff(
                    temp_staff['name'],
                    temp_staff['phone'],
                    temp_staff['email'],
                    temp_staff['password'],
                    temp_staff['specialization']
                )
                session.pop('temp_staff')
                flash('Staff registered!', 'success')
                return redirect(url_for('admin_view_staff'))
            flash('Invalid OTP!', 'error')

        return render_admin(
            'admin/verify_staff_otp.html',
            email=session['temp_staff']['email']
        )

    @app.route('/admin/resend-staff-otp')
    @admin_required
    def admin_resend_staff_otp():
        temp_staff = session.get('temp_staff')
        if not temp_staff:
            flash('No pending staff registration found.', 'error')
            return redirect(url_for('admin_register_staff'))

        if send_staff_registration_otp(temp_staff['email']):
            flash('New OTP sent to staff email.', 'success')
        else:
            flash('Failed to resend OTP.', 'error')

        return redirect(url_for('admin_verify_staff_otp'))

    @app.route('/admin/view-staff')
    @admin_required
    def admin_view_staff():
        staff_list = get_all_staff()
        return render_admin('admin/view_staff.html', staff_list=staff_list)

    @app.route('/admin/delete-staff/<int:staff_id>', methods=['POST'])
    @admin_required
    def admin_delete_staff(staff_id):
        staff_exists = any(int(s['id']) == int(staff_id) for s in get_all_staff())

        if not staff_exists:
            flash('Staff already deleted or not found.', 'info')
            return redirect(url_for('admin_view_staff'))

        deleted = delete_staff(staff_id)
        if deleted:
            flash('Staff deleted!', 'success')
        else:
            flash('Cannot delete staff with accepted/completed jobs. This protects service history.', 'error')
        return redirect(url_for('admin_view_staff'))

    @app.route('/admin/all-bookings')
    @admin_required
    def admin_all_bookings():
        bookings = get_all_bookings()
        return render_admin('admin/all_bookings.html', bookings=bookings)

    @app.route('/admin/service-history')
    @admin_required
    def admin_service_history():
        history = get_service_history()
        return render_admin('admin/service_history.html', history=history)

    @app.route('/admin/export/all-bookings.csv')
    @admin_required
    def export_all_bookings_csv():
        headers = [
            'Booking ID', 'Customer', 'Customer Phone', 'Problem Type',
            'Address', 'Staff', 'Status', 'Created At', 'Accepted At', 'Completed At'
        ]
        rows = []
        for b in [dict(item) for item in get_all_bookings()]:
            rows.append([
                b.get('id'),
                b.get('user_name'),
                b.get('user_phone'),
                b.get('problem_type'),
                b.get('address'),
                staff_label(b),
                b.get('status'),
                b.get('created_at'),
                b.get('accepted_at'),
                b.get('completed_at')
            ])
        return csv_download('all_bookings.csv', headers, rows)

    @app.route('/admin/export/service-history.csv')
    @admin_required
    def export_service_history_csv():
        headers = [
            'Booking ID', 'Customer', 'Customer Phone', 'Problem Type',
            'Staff', 'Status', 'Completed At'
        ]
        rows = []
        for item in [dict(row) for row in get_service_history()]:
            rows.append([
                item.get('id'),
                item.get('user_name'),
                item.get('user_phone'),
                item.get('problem_type'),
                staff_label(item),
                item.get('status'),
                item.get('completed_at') or item.get('created_at')
            ])
        return csv_download('service_history.csv', headers, rows)

    @app.route('/admin/logout')
    def admin_logout():
        session.clear()
        flash('Logged out!', 'success')
        return redirect(url_for('admin_login'))
