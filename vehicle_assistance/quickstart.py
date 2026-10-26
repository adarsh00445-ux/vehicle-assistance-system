import subprocess
import sys
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("[VEHICLE ASSISTANCE SYSTEM] QUICK START")
    print("="*60)
    
    db_path = Path("vehicle_assistance.db")
    
    if not db_path.exists():
        print("\n[1/2] Creating database...")
        result = subprocess.run([sys.executable, "create_admin.py"], capture_output=True)
        if result.returncode == 0:
            print("[OK] Database created")
        else:
            print("[ERROR] Failed to create database")
            return
    else:
        print("\n[OK] Database already exists")
    
    print("\n[2/2] Starting Flask application...")
    print("-" * 60)
    print("[INFO] Server: http://localhost:5000")
    print("[AUTH] Admin: http://localhost:5000/admin/login")
    print("[USER] User: http://localhost:5000/user/login")
    print("[STAFF] Staff: http://localhost:5000/staff/login")
    print("-" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n[OK] Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
