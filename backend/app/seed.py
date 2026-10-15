from app.database import engine, Base, SessionLocal
from app import models
from app.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin_user = db.query(models.User).filter(models.User.email == "admin@uco.edu.co").first()
        if not admin_user:
            admin_user = models.User(
                name="Administrador UCO",
                email="admin@uco.edu.co",
                password_hash=hash_password("admin123"),
                role="Administrador"
            )
            db.add(admin_user)

        analyst_user = db.query(models.User).filter(models.User.email == "analista@uco.edu.co").first()
        if not analyst_user:
            analyst_user = models.User(
                name="Analista Académico",
                email="analista@uco.edu.co",
                password_hash=hash_password("analista123"),
                role="Analista"
            )
            db.add(analyst_user)

        db.commit()
        print("Database seeded successfully with default admin and analyst users.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
