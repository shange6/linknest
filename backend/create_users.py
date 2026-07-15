import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.core.auth import get_password_hash
from app.models.user import User

db = SessionLocal()

existing = db.query(User).count()
if existing == 0:
    u1 = User(email="shange@linknest.local", username="shange", password=get_pa…ash("admin123"), role="admin")
    u2 = User(email="normal@test.com", username="normal", password=get_pa…ash("user1234"), role="user")
    db.add_all([u1, u2])
    db.commit()
    print(f"Users created: admin id={u1.id}, normal id={u2.id}")
else:
    print(f"Already {existing} users in DB")

db.close()
