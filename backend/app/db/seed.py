from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import Permission, Role, User

ROLES = ["admin", "teacher", "student", "parent", "analyst"]

PERMISSIONS = [
    "manage_users",
    "create_course",
    "upload_material",
    "generate_questions",
    "evaluate_assignment",
    "submit_assignment",
    "view_analytics",
    "view_all_analytics",
    "view_predictions",
    "manage_agents",
]

ADMIN_EMAIL = "admin@tutorix.com"
ADMIN_PASSWORD = "admin123"


def seed():
    db: Session = SessionLocal()
    try:
        # Roles
        for name in ROLES:
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name))
        db.commit()

        # Permissions
        for name in PERMISSIONS:
            if not db.query(Permission).filter(Permission.name == name).first():
                db.add(Permission(name=name))
        db.commit()

        # Admin user
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                full_name="Tutorix Admin",
            )
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin.roles.append(admin_role)
            db.add(admin)
            db.commit()

        print("Seed complete.")
        print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()