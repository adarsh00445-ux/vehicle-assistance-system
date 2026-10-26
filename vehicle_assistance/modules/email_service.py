import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, SMTP_FROM_EMAIL
from modules.database import get_connection


def _send_html_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = f"Vehicle Assistance <{SMTP_FROM_EMAIL}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()


def _build_otp_email_html(otp, purpose, title, color, note_html=''):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 500px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 30px;">
            <h2 style="color: {color}; text-align: center;">{title}</h2>
            <hr>
            <p>Hello,</p>
            <p>Your OTP for <strong>{purpose}</strong> is:</p>
            <h1 style="text-align: center; color: {color}; font-size: 40px; letter-spacing: 10px;">{otp}</h1>
            <p>This OTP is valid for 10 minutes.</p>
            {note_html}
            <hr>
            <p style="color: #888; font-size: 12px; text-align: center;">Vehicle Assistance Team</p>
        </div>
    </body>
    </html>
    """

def generate_otp():
    return str(random.randint(100000, 999999))

def save_otp(email, otp, purpose='registration'):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM otp_verify WHERE email = ?", (email,))

    cursor.execute(
        "INSERT INTO otp_verify (email, otp) VALUES (?, ?)",
        (email, otp)
    )
    conn.commit()
    conn.close()

def verify_otp(email, otp):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM otp_verify WHERE email = ? AND otp = ?",
        (email, otp)
    )
    result = cursor.fetchone()

    if result:

        cursor.execute("DELETE FROM otp_verify WHERE email = ?", (email,))
        conn.commit()

    conn.close()
    return result is not None

def send_otp(to_email, otp, purpose="Registration"):
    try:
        body = _build_otp_email_html(
            otp=otp,
            purpose=purpose,
            title='🚗 Vehicle Assistance',
            color='#667eea',
            note_html="<p>If you didn't request this, please ignore this email.</p>"
        )
        _send_html_email(to_email, f'Vehicle Assistance - OTP for {purpose}', body)

        print(f"[OK] OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"[ERROR] Email Error: {e}")
        return False

def send_completion_otp(to_email, otp, mechanic_name):
    try:
        body = _build_otp_email_html(
            otp=otp,
            purpose='Service Completion',
            title='✅ Service Completed!',
            color='#27ae60',
            note_html=(
                f"<p>Mechanic <strong>{mechanic_name}</strong> has completed your service.</p>"
                "<p style=\"color: #e74c3c;\">⚠️ Only share after work is done properly.</p>"
            )
        )
        _send_html_email(to_email, 'Service Completion OTP - Vehicle Assistance', body)

        print(f"[OK] Completion OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"[ERROR] Email Error: {e}")
        return False

def send_booking_info_to_mechanic(mechanic_email, user_name, user_email, user_phone,
                                  alternate_phone, problem_type, address, booking_id):
    try:
        alternate_phone_text = f"<p><strong>Phone (Alternate):</strong> {alternate_phone}</p>" if alternate_phone else ""

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; padding: 30px;">
                <h2 style="color: #667eea; text-align: center;">NEW BOOKING ASSIGNED</h2>
                <hr>
                <p>Hello,</p>
                <p>You have a new booking assigned to you. Here are the customer details:</p>

                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">BOOKING DETAILS</h3>
                    <p><strong>Booking ID:</strong> #{booking_id}</p>

                    <h3 style="color: #333;">CUSTOMER INFORMATION (VERIFIED)</h3>
                    <p><strong>Name:</strong> {user_name}</p>
                  

                    <h3 style="color: #333;">SERVICE INFORMATION</h3>
                    <p><strong>Problem Type:</strong> {problem_type}</p>
                </div>

                <p style="color: #666;">Please contact the customer using the provided phone numbers to confirm the appointment time and any other details.</p>
                <p style="color: #e74c3c;"><strong>Note:</strong> The name, email, and registered phone are verified information. The customer cannot edit these details.</p>

                <hr>
                <p style="color: #888; font-size: 12px; text-align: center;">Vehicle Assistance Team</p>
            </div>
        </body>
        </html>
        """

        _send_html_email(
            mechanic_email,
            f'New Booking Accepted - Booking #{booking_id} - Vehicle Assistance',
            body,
        )

        print(f"[OK] Booking info sent to mechanic {mechanic_email}")
        return True

    except Exception as e:
        print(f"[ERROR] Email Error: {e}")
        return False
