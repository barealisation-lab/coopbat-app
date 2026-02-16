import os
import json
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, Float
)
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'coop.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# -------------------------
# USERS PRO
# -------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------
# SIMPLE REQUEST
# -------------------------
class WorkRequest(Base):
    __tablename__ = "work_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    work_type = Column(String, nullable=False)
    surface = Column(String, nullable=True)
    budget = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------------------------
# LEAD LOT COMPLET
# -------------------------
class LeadRequest(Base):
    __tablename__ = "lead_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)

    couverture_type = Column(String, nullable=False)
    couverture_surface_m2 = Column(String, nullable=False)
    couverture_isolation = Column(String, default="false")
    couverture_sarking = Column(String, default="false")
    couverture_ecran = Column(String, default="true")

    zinguerie_choices_json = Column(Text, default="[]")
    charpente_choices_json = Column(Text, default="[]")

    contact_name = Column(String, nullable=False)
    contact_commune = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_message = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    def set_zinguerie_choices(self, arr):
        self.zinguerie_choices_json = json.dumps(arr or [], ensure_ascii=False)

    def set_charpente_choices(self, arr):
        self.charpente_choices_json = json.dumps(arr or [], ensure_ascii=False)

    def get_zinguerie_choices(self):
        try:
            return json.loads(self.zinguerie_choices_json or "[]")
        except Exception:
            return []

    def get_charpente_choices(self):
        try:
            return json.loads(self.charpente_choices_json or "[]")
        except Exception:
            return []


# -------------------------
# ADVANCED REQUEST (V2++)
# -------------------------
class AdvancedRequest(Base):
    __tablename__ = "advanced_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)

    contact_name = Column(String, nullable=False)
    contact_commune = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)

    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================================================
# ARTISANS + TOKEN (V5)
# =========================================================
class ArtisanAccount(Base):
    __tablename__ = "artisan_accounts"
    id = Column(Integer, primary_key=True, index=True)

    contact_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)

    commune = Column(String, nullable=False)
    radius_km = Column(Integer, default=30)
    zone_note = Column(String, nullable=True)

    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ token stocké sous forme hash (sécurité)
    token_hash = Column(String, nullable=True)
    token_created_at = Column(DateTime, nullable=True)


class ArtisanRequestStatus(Base):
    __tablename__ = "artisan_request_status"
    id = Column(Integer, primary_key=True, index=True)

    artisan_id = Column(Integer, index=True, nullable=False)
    request_kind = Column(String, index=True, nullable=False)  # "simple"|"lead"|"advanced"
    request_id = Column(Integer, index=True, nullable=False)
    status = Column(String, default="new")  # "new"|"in_progress"

    updated_at = Column(DateTime, default=datetime.utcnow)


# =========================================================
# CATALOGUE (base modifiable)
# =========================================================
class CatalogItem(Base):
    __tablename__ = "catalog_items"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    price = Column(Float, nullable=True)   # à remplir par toi
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class WoodSpecies(Base):
    __tablename__ = "wood_species"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TimberSection(Base):
    __tablename__ = "timber_sections"
    id = Column(Integer, primary_key=True, index=True)
    section_mm = Column(String, unique=True, index=True, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
