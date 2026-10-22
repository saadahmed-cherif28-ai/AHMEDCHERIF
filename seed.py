"""Crée les tables et ajoute les données de test.

Le script peut être relancé sans risque : il n'ajoute pas deux fois la même donnée.
Mot de passe de test pour tous les comptes : test1234
"""

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from database import Base, SessionLocal, engine
from models import ConsentVersion, User, utcnow

TEST_USERS = [
    ("alumni@example.com", "ALUMNI"),
    ("service@example.com", "SERVICE"),
    ("direction@example.com", "DIRECTION"),
    ("admin@example.com", "ADMIN"),
    ("etudiant@example.com", "STUDENT"),
]

CONSENT_TEXT = (
    "J'autorise l'EIGSI à utiliser mes données personnelles pour le suivi "
    "des alumni, et à les afficher dans l'annuaire réservé aux étudiants."
)


def main():
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        for email, role in TEST_USERS:
            existing = session.scalar(select(User).where(User.email == email))
            if existing is None:
                session.add(
                    User(
                        email=email,
                        role=role,
                        password_hash=generate_password_hash("test1234"),
                    )
                )

        version = session.scalar(
            select(ConsentVersion).where(
                ConsentVersion.purpose_code == "suivi_alumni",
                ConsentVersion.version == "1.0",
            )
        )
        if version is None:
            session.add(
                ConsentVersion(
                    purpose_code="suivi_alumni",
                    version="1.0",
                    text=CONSENT_TEXT,
                    published_at=utcnow(),
                )
            )

        session.commit()

        print("Comptes dans la table users :")
        for user in session.scalars(select(User).order_by(User.email)):
            print(f"  {user.email:<24} {user.role:<10} actif={user.is_active}")


if __name__ == "__main__":
    main()
