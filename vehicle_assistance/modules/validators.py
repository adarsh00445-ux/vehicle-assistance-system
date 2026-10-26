import re

def validate_phone(phone):

    phone = phone.replace(' ', '').replace('-', '').replace('+', '')

    if phone.startswith('91') and len(phone) > 10:
        phone = phone[2:]

    if len(phone) == 10 and phone.isdigit():
        return True, phone

    return False, None

def validate_email(email):

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    return len(password) >= 6


