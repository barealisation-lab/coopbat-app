import os
import json
import hashlib
import secrets
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .database import (
    Base,
    User, WorkRequest, LeadRequest, AdvancedRequest,
    ArtisanAccount, ArtisanRequestStatus,
    CatalogItem, WoodSpecies, TimberSection
)

# -------------------------
# CONFIG
# -------------------------
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token")  # change en prod
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # en prod: "https://ton-front.vercel.app,https://ton-domaine.com"
DATABASE_URL = os.getenv("DATABASE_URL", "")  # en prod Render Postgres
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", "")  # optionnel si tu utilises disque Render (payant)

# -------------------------
# DB engine override (si DATABASE_URL fourni)
# -------------------------
if DATABASE_URL:
    # Render fournit souvent postgres:// -> SQLAlchemy préfère postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
else:
    # fallback SQLite = celui de database.py (local)
    from .database import engine, SessionLocal
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coop'Bat API")

origins = [o.strip() for o in CORS_ORIGINS.split(",")] if CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# HELPERS
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def make_artisan_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def require_admin(x_admin_token: Optional[str]):
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")


def require_artisan_token(artisan_id: int, db: Session, x_artisan_token: Optional[str]):
    if not x_artisan_token:
        raise HTTPException(status_code=401, detail="Missing artisan token")
    a = db.query(ArtisanAccount).filter(ArtisanAccount.id == artisan_id).first()
    if not a or not a.token_hash:
        raise HTTPException(status_code=401, detail="Invalid artisan token")
    if hash_token(x_artisan_token) != a.token_hash:
        raise HTTPException(status_code=401, detail="Invalid artisan token")
    return True


def write_archive(kind: str, payload: dict):
    """
    Optionnel.
    Sur Render, le disque est éphémère sauf si tu ajoutes un Persistent Disk (payant). :contentReference[oaicite:1]{index=1}
    Tu peux laisser vide (ARCHIVE_DIR="") et tout sera en DB.
    """
    if not ARCHIVE_DIR:
        return
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(ARCHIVE_DIR, f"{kind}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# -------------------------
# MODELS
# -------------------------
class RegisterIn(BaseModel):
    name: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class SimpleRequestIn(BaseModel):
    name: str
    email: str
    work_type: str
    option_choice: str
    surface: str | None = ""
    budget: str | None = ""
    message: str | None = ""


class LeadRequestIn(BaseModel):
    couverture_type: str
    couverture_surface_m2: str
    couverture_isolation: bool = False
    couverture_sarking: bool = False
    couverture_ecran: bool = True

    zinguerie: list = []
    charpente: list = []

    contact_name: str
    contact_commune: str
    contact_email: str
    contact_message: str = ""


class AdvancedRequestIn(BaseModel):
    contact_name: str
    contact_commune: str
    contact_email: str
    payload: dict


class ArtisanRegisterIn(BaseModel):
    contact_name: str
    email: str
    password: str
    commune: str
    radius_km: int = 30
    phone: str | None = ""
    zone_note: str | None = ""


class ArtisanLoginIn(BaseModel):
    email: str
    password: str


class StatusUpdateIn(BaseModel):
    status: str  # "in_progress" ou "new"


class CatalogUpsertIn(BaseModel):
    category: str
    name: str
    unit: str | None = ""
    price: float | None = None
    note: str | None = ""


class WoodUpsertIn(BaseModel):
    name: str
    note: str | None = ""


class SectionUpsertIn(BaseModel):
    section_mm: str
    note: str | None = ""


# -------------------------
# HEALTH
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# PRO AUTH
# -------------------------
@app.post("/register")
def register_user(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    u = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password.strip()),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"message": "ok", "user_id": u.id}


@app.post("/login")
def login_user(data: LoginIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    u = db.query(User).filter(User.email == email).first()
    if not u or not verify_password(data.password.strip(), u.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return {"message": "ok", "user_id": u.id, "name": u.name, "email": u.email}


# -------------------------
# SIMPLE REQUEST
# -------------------------
@app.post("/submit_form")
def submit_form(data: SimpleRequestIn, db: Session = Depends(get_db)):
    req = WorkRequest(
        name=data.name,
        email=data.email,
        work_type=data.work_type,
        surface=data.surface or "",
        budget=data.budget or "",
        message=f"{data.option_choice} | {data.message or ''}",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    write_archive("simple", {"id": req.id, **data.model_dump()})
    return {"message": "ok", "id": req.id}


# -------------------------
# LEAD LOT COMPLET
# -------------------------
@app.post("/lead")
def submit_lead(data: LeadRequestIn, db: Session = Depends(get_db)):
    if not data.couverture_surface_m2 or not data.contact_name or not data.contact_commune or not data.contact_email:
        raise HTTPException(status_code=400, detail="Champs requis manquants")

    lead = LeadRequest(
        couverture_type=data.couverture_type,
        couverture_surface_m2=data.couverture_surface_m2,
        couverture_isolation=str(bool(data.couverture_isolation)).lower(),
        couverture_sarking=str(bool(data.couverture_sarking)).lower(),
        couverture_ecran=str(bool(data.couverture_ecran)).lower(),
        contact_name=data.contact_name,
        contact_commune=data.contact_commune,
        contact_email=data.contact_email,
        contact_message=data.contact_message or "",
    )
    lead.set_zinguerie_choices(data.zinguerie or [])
    lead.set_charpente_choices(data.charpente or [])

    db.add(lead)
    db.commit()
    db.refresh(lead)
    write_archive("lead", {"id": lead.id, **data.model_dump()})
    return {"message": "ok", "id": lead.id}


# -------------------------
# ADVANCED REQUEST
# -------------------------
@app.post("/advanced")
def submit_advanced(data: AdvancedRequestIn, db: Session = Depends(get_db)):
    if not data.contact_name or not data.contact_commune or not data.contact_email:
        raise HTTPException(status_code=400, detail="Champs requis manquants")

    ar = AdvancedRequest(
        contact_name=data.contact_name,
        contact_commune=data.contact_commune,
        contact_email=data.contact_email,
        payload_json=json.dumps(data.payload, ensure_ascii=False),
    )
    db.add(ar)
    db.commit()
    db.refresh(ar)
    write_archive("advanced", {"id": ar.id, **data.model_dump()})
    return {"message": "ok", "id": ar.id}


# -------------------------
# ARTISAN AUTH (TOKEN)
# -------------------------
@app.post("/artisan/register")
def artisan_register(data: ArtisanRegisterIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(ArtisanAccount).filter(ArtisanAccount.email == email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    a = ArtisanAccount(
        contact_name=data.contact_name.strip(),
        email=email,
        password_hash=hash_password(data.password.strip()),
        commune=data.commune.strip(),
        radius_km=int(data.radius_km or 30),
        phone=(data.phone or "").strip(),
        zone_note=(data.zone_note or "").strip(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"message": "ok", "artisan_id": a.id}


@app.post("/artisan/login")
def artisan_login(data: ArtisanLoginIn, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    a = db.query(ArtisanAccount).filter(ArtisanAccount.email == email).first()
    if not a or not verify_password(data.password.strip(), a.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants artisan incorrects")

    token = make_artisan_token()
    a.token_hash = hash_token(token)
    a.token_created_at = datetime.utcnow()
    db.add(a)
    db.commit()

    return {
        "message": "ok",
        "artisan_id": a.id,
        "artisan_token": token,
        "contact_name": a.contact_name,
        "email": a.email,
        "commune": a.commune,
        "radius_km": a.radius_km,
        "phone": a.phone or "",
        "zone_note": a.zone_note or "",
    }


@app.post("/artisan/logout/{artisan_id}")
def artisan_logout(
    artisan_id: int,
    x_artisan_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_artisan_token(artisan_id, db, x_artisan_token)
    a = db.query(ArtisanAccount).filter(ArtisanAccount.id == artisan_id).first()
    a.token_hash = None
    a.token_created_at = None
    db.add(a)
    db.commit()
    return {"message": "ok"}


# -------------------------
# ARTISAN REQUESTS (LOCKED)
# -------------------------
@app.get("/artisan/requests/{artisan_id}")
def artisan_list_requests(
    artisan_id: int,
    x_artisan_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_artisan_token(artisan_id, db, x_artisan_token)

    items = []

    # simple
    for r in db.query(WorkRequest).order_by(WorkRequest.created_at.desc()).limit(200).all():
        items.append({
            "kind": "simple",
            "id": r.id,
            "date": r.created_at.isoformat(),
            "work_type": r.work_type,
            "surface": r.surface or "",
            "budget": r.budget or "",
            "email": r.email,
            "commune": "",
            "status": "new",
        })

    # lead
    for r in db.query(LeadRequest).order_by(LeadRequest.created_at.desc()).limit(200).all():
        items.append({
            "kind": "lead",
            "id": r.id,
            "date": r.created_at.isoformat(),
            "work_type": "Lot complet",
            "surface": r.couverture_surface_m2,
            "budget": "",
            "email": r.contact_email,
            "commune": r.contact_commune,
            "status": "new",
        })

    # advanced
    for r in db.query(AdvancedRequest).order_by(AdvancedRequest.created_at.desc()).limit(200).all():
        items.append({
            "kind": "advanced",
            "id": r.id,
            "date": r.created_at.isoformat(),
            "work_type": "Chiffrage détaillé",
            "surface": "",
            "budget": "",
            "email": r.contact_email,
            "commune": r.contact_commune,
            "status": "new",
        })

    # statuses
    statuses = db.query(ArtisanRequestStatus).filter(ArtisanRequestStatus.artisan_id == artisan_id).all()
    status_map = {(s.request_kind, s.request_id): s.status for s in statuses}

    for it in items:
        it["status"] = status_map.get((it["kind"], it["id"]), "new")

    # tri global
    items.sort(key=lambda x: x["date"], reverse=True)
    return {"items": items}


@app.post("/artisan/requests/{artisan_id}/{kind}/{request_id}/status")
def artisan_set_status(
    artisan_id: int, kind: str, request_id: int, data: StatusUpdateIn,
    x_artisan_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_artisan_token(artisan_id, db, x_artisan_token)

    if data.status not in ("new", "in_progress"):
        raise HTTPException(status_code=400, detail="status invalide")

    s = db.query(ArtisanRequestStatus).filter(
        ArtisanRequestStatus.artisan_id == artisan_id,
        ArtisanRequestStatus.request_kind == kind,
        ArtisanRequestStatus.request_id == request_id
    ).first()

    if not s:
        s = ArtisanRequestStatus(
            artisan_id=artisan_id,
            request_kind=kind,
            request_id=request_id,
            status=data.status,
            updated_at=datetime.utcnow(),
        )
    else:
        s.status = data.status
        s.updated_at = datetime.utcnow()

    db.add(s)
    db.commit()
    return {"message": "ok"}


# -------------------------
# CATALOG ADMIN (LOCKED)
# -------------------------
@app.get("/admin/catalog")
def admin_list_catalog(
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_admin(x_admin_token)
    rows = db.query(CatalogItem).order_by(CatalogItem.category.asc(), CatalogItem.name.asc()).all()
    return {"items": [
        {"id": r.id, "category": r.category, "name": r.name, "unit": r.unit, "price": r.price, "note": r.note}
        for r in rows
    ]}


@app.post("/admin/catalog/upsert")
def admin_upsert_catalog(
    data: CatalogUpsertIn,
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_admin(x_admin_token)
    row = db.query(CatalogItem).filter(CatalogItem.category == data.category, CatalogItem.name == data.name).first()
    if not row:
        row = CatalogItem(category=data.category, name=data.name)

    row.unit = data.unit or ""
    row.price = data.price
    row.note = data.note or ""
    row.updated_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return {"message": "ok"}


@app.post("/admin/wood/upsert")
def admin_upsert_wood(
    data: WoodUpsertIn,
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_admin(x_admin_token)
    row = db.query(WoodSpecies).filter(WoodSpecies.name == data.name).first()
    if not row:
        row = WoodSpecies(name=data.name)
    row.note = data.note or ""
    row.updated_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return {"message": "ok"}


@app.post("/admin/section/upsert")
def admin_upsert_section(
    data: SectionUpsertIn,
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    require_admin(x_admin_token)
    row = db.query(TimberSection).filter(TimberSection.section_mm == data.section_mm).first()
    if not row:
        row = TimberSection(section_mm=data.section_mm)
    row.note = data.note or ""
    row.updated_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return {"message": "ok"}
