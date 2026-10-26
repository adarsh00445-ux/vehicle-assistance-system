import re

import google.generativeai as genai

from config import GEMINI_API_KEY
from modules.database import get_connection

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a vehicle assistance chatbot.

Rules:
1. Answer only vehicle-related questions.
2. Keep responses short (maximum 3 sentences).
3. For troubleshooting, suggest basic checks first.
4. If repair or advanced diagnosis is needed, clearly ask the user to contact a mechanic.
5. Mention that delay can increase damage and repair cost when relevant.
6. Do not use emojis, headings, or extra marketing text.
7. If the message is not about vehicles, reply exactly: "I can only help with vehicle issues."
8. If the user says hi or hello, reply: "Hello! How can I assist you with your vehicle today?"
9. If the user asks who created , reply: "I am a vehicle assistance chatbot created by Aryan & Adarsh"
"""

MODEL_FALLBACKS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-lite-latest",
]

SERVICE_UNAVAILABLE = "Service is temporarily unavailable. Please try again."


def _clean_ai_text(text):
    cleaned = text.replace("*", "").replace("#", "").replace("`", "")
    lines = []
    for line in cleaned.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    joined_text = " ".join(lines)

    parts = re.split(r"(?<=[.!?])\s+", joined_text)
    sentences = []
    for part in parts:
        part = part.strip()
        if part:
            sentences.append(part)

    if len(sentences) > 3:
        return " ".join(sentences[:3])
    return joined_text


def get_ai_response(user_message):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\n\nAssistant:"

        last_error = None
        for model_name in MODEL_FALLBACKS:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                response_text = (response.text or "").strip()
                if response_text:
                    return _clean_ai_text(response_text)
            except Exception as model_error:
                last_error = model_error

        if last_error:
            print(f"AI Error: {last_error}")
        return SERVICE_UNAVAILABLE

    except Exception as error:
        print(f"AI Error: {error}")
        return SERVICE_UNAVAILABLE

def save_chat(user_id, user_message, ai_response):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO chat_history (user_id, user_message, ai_response) VALUES (?, ?, ?)",
            (user_id, user_message, ai_response)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Chat save error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_chat_history(user_id, limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        history = cursor.fetchall()
        return list(reversed(history))
    except Exception as e:
        print(f"Chat history error: {e}")
        return []
    finally:
        conn.close()
