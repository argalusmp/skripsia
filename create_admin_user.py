# Create admin_user.py
import sys
sys.path.append('/var/www/skripsia')

from app.database import SessionLocal
from app.users.models import User
from app.auth.utils import get_password_hash

def create_admin():
    db = SessionLocal()
    admin = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=get_password_hash("adminTIK900"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    print("Admin user created successfully")

if __name__ == "__main__":
    create_admin()