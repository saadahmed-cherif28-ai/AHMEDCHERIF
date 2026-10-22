import uuid
from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

# Rôles prévus dans le schéma corrigé
ROLES = ("ALUMNI", "SERVICE", "DIRECTION", "ADMIN", "STUDENT")


def new_id():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )


class AlumniProfile(Base):
    __tablename__ = "alumni_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), unique=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    graduation_year: Mapped[int] = mapped_column(Integer, nullable=False)
    program: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # DRAFT, PENDING, NEEDS_CORRECTION, VALIDATED, REJECTED
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )


class ConsentVersion(Base):
    __tablename__ = "consent_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    purpose_code: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(10), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    alumni_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alumni_profiles.id"), nullable=False
    )
    consent_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consent_versions.id"), nullable=False
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Vide tant que le consentement est actif
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    alumni_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("alumni_profiles.id"), nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
