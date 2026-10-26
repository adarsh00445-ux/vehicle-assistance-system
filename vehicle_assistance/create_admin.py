from werkzeug.security import generate_password_hash
from modules.database import get_connection
from modules.db_init import init_database, check_database

def main():
    if not check_database():
        print("Initializing database...")
        init_database()
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM admin")
    print("Old admin deleted...")

    username = "admin"
    password = "admin123"
    hashed_password = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO admin (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    connection.commit()
    connection.close()

    print("\nAdmin created successfully!")
    print("=" * 40)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("=" * 40)


if __name__ == "__main__":
    main()

