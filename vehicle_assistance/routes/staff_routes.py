from flask import render_template, request, redirect, session, url_for, flash
from modules.staff import check_staff_login, get_staff_stats, get_staff_jobs
from modules.bookings import get_pending_bookings, accept_booking, get_booking_by_id, set_completion_otp, complete_booking, reset_booking_to_pending
from modules.email_service import generate_otp, send_completion_otp, send_booking_info_to_mechanic
from modules.web_utils import staff_required
from modules.route_helpers import normalize_phone_input, render_staff, rows_to_dicts, count_jobs_by_status, staff_name


def register_staff_routes(app):
    @app.route('/staff/login', methods=['GET', 'POST'])
    def staff_login():
        if request.method == 'POST':
            email_or_phone = normalize_phone_input(request.form['email_or_phone'])
            password = request.form['password']
            staff = check_staff_login(email_or_phone, password)

            if staff:
                staff = dict(staff)
                session['staff_id'] = staff['id']
                session['staff_name'] = staff['name']
                session['staff_email'] = staff['email']
                flash(f'Welcome back, {staff["name"]}!', 'success')
                return redirect(url_for('staff_dashboard'))
            flash('Invalid credentials!', 'error')

        return render_template('staff/login.html')

    @app.route('/staff/dashboard')
    @staff_required
    def staff_dashboard():
        pending = get_pending_bookings()
        stats = get_staff_stats(session['staff_id'])
        return render_staff('staff/dashboard.html', bookings=pending, stats=stats)

    @app.route('/staff/accept/<int:booking_id>', methods=['POST'])
    @staff_required
    def staff_accept(booking_id):
        accepted = accept_booking(booking_id, session['staff_id'])

        if accepted:
            booking = get_booking_by_id(booking_id)

            if booking:
                booking = dict(booking)  # Convert Row to dict
                send_booking_info_to_mechanic(
                    mechanic_email=session.get('staff_email', ''),
                    user_name=booking.get('user_name', 'Customer'),
                    user_email=booking.get('user_email', ''),
                    user_phone=booking.get('registered_phone', ''),
                    alternate_phone=booking.get('alternate_phone'),
                    problem_type=booking.get('problem_type', ''),
                    address=booking.get('address', ''),
                    booking_id=booking_id
                )
                flash('Booking accepted! User details sent to your email.', 'success')
            else:
                flash('Booking accepted!', 'success')
        else:
            flash('Booking is no longer available to accept.', 'error')

        return redirect(url_for('staff_my_jobs'))

    @app.route('/staff/my-jobs')
    @staff_required
    def staff_my_jobs():
        jobs = rows_to_dicts(get_staff_jobs(session['staff_id']))
        status_counts = count_jobs_by_status(jobs, ['pending', 'accepted', 'completed'])
        return render_staff('staff/my_jobs.html', 
                          jobs=jobs, 
                          total_jobs=len(jobs),
                          pending_jobs=status_counts.get('pending', 0),
                          accepted_jobs=status_counts.get('accepted', 0),
                          completed_jobs=status_counts.get('completed', 0))

    @app.route('/staff/resolve/<int:booking_id>', methods=['POST'])
    @staff_required
    def staff_resolve(booking_id):
        booking = get_booking_by_id(booking_id)

        if booking:
            otp = generate_otp()
            set_completion_otp(booking_id, otp)

            if send_completion_otp(booking['user_email'], otp, staff_name()):
                flash('Completion OTP sent to customer!', 'success')
            else:
                flash('Failed to send OTP!', 'error')

        return redirect(url_for('staff_my_jobs'))

    @app.route('/staff/complete/<int:booking_id>', methods=['POST'])
    @staff_required
    def staff_complete(booking_id):
        otp = request.form['otp'].strip()

        if complete_booking(booking_id, otp):
            flash('Service completed!', 'success')
        else:
            flash('Invalid OTP!', 'error')

        return redirect(url_for('staff_my_jobs'))

    @app.route('/staff/cancel-job/<int:booking_id>', methods=['POST'])
    @staff_required
    def staff_cancel_job(booking_id):
        if reset_booking_to_pending(booking_id):
            flash('Job cancelled! It is now available for other staff.', 'success')
        else:
            flash('Error cancelling job!', 'error')
        
        return redirect(url_for('staff_my_jobs'))

    @app.route('/staff/statistics')
    @staff_required
    def staff_statistics():
        stats = get_staff_stats(session['staff_id'])
        jobs = get_staff_jobs(session['staff_id'])
        return render_staff('staff/statistics.html', stats=stats, jobs=jobs)

    @app.route('/staff/logout')
    def staff_logout():
        session.clear()
        flash('Logged out!', 'success')
        return redirect(url_for('staff_login'))
