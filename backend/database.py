import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./coop.db")

# Render Postgres fournit souvent "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class ProUser(Base):
    __tablename__ = "pro_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="")
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relation: demandes prises en charge
    assignments = relationship("RequestAssignment", back_populates="artisan", cascade="all, delete-orphan")


class ArtisanUser(Base):
    __tablename__ = "artisan_users"

    id = Column(Integer, primary_key=True, index=True)
    contact_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    commune = Column(String, nullable=False, default="")
    radius_km = Column(Integer, nullable=False, default=0)
    phone = Column(String, nullable=True, default="")
    zone_note = Column(String, nullable=True, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("RequestAssignment", back_populates="artisan", cascade="all, delete-orphan")


class WorkRequest(Base):
    """
    Archive des demandes (persistant en DB).
    """
    __tablename__ = "work_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # statut global (pour l'affichage)
    status = Column(String, default="nouvelle")  # nouvelle / en_traitement / etc.

    # demandeur (obligatoire)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    commune = Column(String, nullable=False)

    # lot / infos générales
    lot_type = Column(String, nullable=False, default="")  # "lot" / "charpente" / "couverture" / "zinguerie"
    surface_m2 = Column(String, nullable=False, default="")  # obligatoire côté API
    budget = Column(String, nullable=True, default="")
    message = Column(Text, nullable=True, default="")

    # Couverture
    cover_type = Column(String, nullable=True, default="")  # tuile, ardoise, zinc...
    cover_surface_m2 = Column(String, nullable=True, default="")
    insulation = Column(Boolean, default=False)
    sarking = Column(Boolean, default=False)

    # Zinguerie (quantités)
    gouttiere_ml = Column(String, nullable=True, default="")
    habillage_rives_ml = Column(String, nullable=True, default="")
    habillage_mur_m2 = Column(String, nullable=True, default="")
    couverture_zinc_m2 = Column(String, nullable=True, default="")
    tour_cheminee_nb = Column(String, nullable=True, default="")

    # Charpente (liste simple d’options cochées)
    charp_options = Column(String, nullable=True, default="")  # ex: "renovation;extension;..."

    # Assignation artisan (optionnelle)
    assignments = relationship("RequestAssignment", back_populates="request", cascade="all, delete-orphan")


class RequestAssignment(Base):
    """
    Table d'assignation : un artisan peut marquer une demande "en traitement".
    """
    __tablename__ = "request_assignments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("work_requests.id", ondelete="CASCADE"), nullable=False)
    artisan_id = Column(Integer, ForeignKey("artisan_users.id", ondelete="CASCADE"), nullable=False)

    status = Column(String, default="en_traitement")  # en_traitement / termine / etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("WorkRequest", back_populates="assignments")
    artisan = relationship("ArtisanUser", back_populates="assignments")


Base.metadata.create_all(bind=engine)
