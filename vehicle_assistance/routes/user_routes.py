from flask import render_template, request, redirect, session, url_for, flash, jsonify
import traceback
from modules.users import create_user, check_user_login
from modules.bookings import create_booking, get_user_bookings, cancel_user_booking
from modules.email_service import verify_otp
from modules.web_utils import user_required, verify_csrf_token
from modules.route_helpers import (
    normalize_phone_input,
    send_registration_otp,
    validate_user_registration_form,
    get_current_user_data,
    parse_booking_form,
)

try:
    from modules.ai_service import get_ai_response, save_chat
except Exception as e:
    print(f"Warning: AI service not available - {e}")

    def get_ai_response(msg):
        return "AI service unavailable"

    def save_chat(u, m, r):
        return None


def register_user_routes(app):
    @app.route('/user/register', methods=['GET', 'POST'])
    def user_register():
        if request.method == 'POST':
            try:
                if not verify_csrf_token():
                    return render_template('user/register.html')

                temp_user, error = validate_user_registration_form(request.form)
                if error:
                    flash(error, 'error')
                    return render_template('user/register.html')

                session['temp_user'] = temp_user
                if send_registration_otp(temp_user['email']):
                    flash('OTP sent to your email!', 'success')
                    return redirect(url_for('user_verify_otp'))
                flash('Failed to send OTP. Try again!', 'error')
            except Exception as e:
                print(f"Registration error: {e}")
                flash('An error occurred during registration. Please try again.', 'error')

        return render_template('user/register.html')

    @app.route('/user/verify-otp', methods=['GET', 'POST'])
    def user_verify_otp():
        if 'temp_user' not in session:
            return redirect(url_for('user_register'))

        if request.method == 'POST':
            try:
                if not verify_csrf_token():
                    return render_template('user/verify_otp.html', email=session['temp_user']['email'])

                otp = request.form['otp'].strip()
                temp_user = session['temp_user']

                if verify_otp(temp_user['email'], otp):
                    create_user(
                        temp_user['name'],
                        temp_user['phone'],
                        temp_user['email'],
                        temp_user['password']
                    )
                    session.pop('temp_user')
                    flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('user_login'))
                flash('Invalid or expired OTP!', 'error')
            except Exception as e:
                print(f"OTP verification error: {e}")
                flash('An error occurred during verification. Please try again.', 'error')

        return render_template('user/verify_otp.html', email=session['temp_user']['email'])

    @app.route('/user/resend-otp')
    def user_resend_otp():
        temp_user = session.get('temp_user')
        if not temp_user:
            flash('Please register first.', 'error')
            return redirect(url_for('user_register'))

        if send_registration_otp(temp_user['email']):
            flash('New OTP sent to your email.', 'success')
        else:
            flash('Failed to resend OTP. Please try again.', 'error')

        return redirect(url_for('user_verify_otp'))

    @app.route('/user/login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            try:
                if not verify_csrf_token():
                    return render_template('user/login.html')

                email_or_phone = normalize_phone_input(request.form['email_or_phone'])
                password = request.form['password']

                user = check_user_login(email_or_phone, password)

                if user:
                    user = dict(user)  # Convert Row to dict
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    session['user_phone'] = user['phone']
                    flash(f'Welcome back, {user["name"]}!', 'success')
                    return redirect(url_for('user_dashboard'))
                flash('Invalid email/phone or password!', 'error')
            except Exception as e:
                print(f"Login error: {e}")
                flash('An error occurred during login. Please try again.', 'error')

        return render_template('user/login.html')

    @app.route('/user/dashboard')
    @user_required
    def user_dashboard():
        bookings = get_user_bookings(session['user_id'])
        return render_template('user/dashboard.html', bookings=bookings[:5], name=session.get('user_name', 'User'))

    @app.route('/user/book-mechanic', methods=['GET', 'POST'])
    @user_required
    def user_book_mechanic():
        user_id = session.get('user_id')
        user_data = get_current_user_data(user_id)
        if not user_data:
            flash('User not found. Please login again.', 'error')
            return redirect(url_for('user_login'))

        if request.method == 'POST':
            if not verify_csrf_token():
                flash('Security check failed. Please try again.', 'error')
                return redirect(url_for('user_book_mechanic'))

            form_data = parse_booking_form(request.form)
            if not form_data['address']:
                flash('Please enter a service address.', 'error')
                return redirect(url_for('user_book_mechanic'))
            if not form_data['problem_type']:
                flash('Please select a problem type.', 'error')
                return redirect(url_for('user_book_mechanic'))

            try:
                booking_id = create_booking(
                    user_id=user_id,
                    address=form_data['address'],
                    registered_phone=user_data['phone'],
                    alternate_phone=form_data['alternate_phone'],
                    problem_type=form_data['problem_type'],
                    description=form_data['description'],
                    latitude=form_data['latitude'],
                    longitude=form_data['longitude']
                )

                if booking_id:
                    flash(f'Booking #{booking_id} created successfully!', 'success')
                    return redirect(url_for('user_dashboard'))
                flash('Failed to create booking.', 'error')
                return redirect(url_for('user_book_mechanic'))
            except Exception as db_err:
                print(f"DB Error: {db_err}")
                traceback.print_exc()
                flash(f'Booking error: {str(db_err)}', 'error')
                return redirect(url_for('user_book_mechanic'))

        try:
            return render_template(
                'user/book_mechanic.html',
                user_name=user_data['name'],
                user_email=user_data['email'],
                user_phone=user_data['phone']
            )
        except Exception as template_err:
            print(f"Template render error: {template_err}")
            traceback.print_exc()
            flash('Could not load booking form.', 'error')
            return redirect(url_for('user_dashboard'))

    @app.route('/user/cancel-booking/<int:booking_id>', methods=['POST'])
    @user_required
    def user_cancel_booking(booking_id):
        if cancel_user_booking(booking_id, session['user_id']):
            flash('Booking cancelled successfully.', 'info')
        else:
            flash('Cannot cancel this booking.', 'error')
        return redirect(url_for('user_my_bookings'))

    @app.route('/user/my-bookings')
    @user_required
    def user_my_bookings():
        bookings = get_user_bookings(session['user_id'])
        return render_template('user/my_bookings.html', bookings=bookings, name=session.get('user_name', 'User'))

    @app.route('/user/send-message', methods=['POST'])
    @user_required
    def user_send_message():
        data = request.get_json(silent=True) or {}
        message = (data.get('message') or '').strip()

        if not message:
            return jsonify({'error': 'No message'}), 400

        try:
            response = get_ai_response(message)
            save_chat(session['user_id'], message, response)
            return jsonify({'response': response})
        except Exception as e:
            print(f"Chat route error: {e}")
            return jsonify({'response': 'Sorry, the assistant is temporarily unavailable. Please try again.'}), 500

    @app.route('/user/logout')
    def user_logout():
        session.clear()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('user_login'))
