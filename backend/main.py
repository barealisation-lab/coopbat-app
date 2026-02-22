import os
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from database import SessionLocal, ProUser, ArtisanUser, WorkRequest, RequestAssignment

app = FastAPI(title="Coop'Bat API")

# ---------- CORS ----------
cors_origins = os.getenv("CORS_ORIGINS", "*")
allow_origins = ["*"] if cors_origins.strip() == "*" else [o.strip() for o in cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Health ----------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# ---------- Schemas ----------
class ProRegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ArtisanRegisterIn(BaseModel):
    contact_name: str
    email: EmailStr
    password: str
    commune: str
    radius_km: int
    phone: Optional[str] = ""
    zone_note: Optional[str] = ""


class WorkRequestIn(BaseModel):
    # obligatoires
    name: str
    email: EmailStr
    commune: str
    surface_m2: str

    # infos générales
    lot_type: str = "lot"  # lot/charpente/couverture/zinguerie
    budget: Optional[str] = ""
    message: Optional[str] = ""

    # couverture
    cover_type: Optional[str] = ""
    cover_surface_m2: Optional[str] = ""
    insulation: bool = False
    sarking: bool = False

    # zinguerie quantités
    gouttiere_ml: Optional[str] = ""
    habillage_rives_ml: Optional[str] = ""
    habillage_mur_m2: Optional[str] = ""
    couverture_zinc_m2: Optional[str] = ""
    tour_cheminee_nb: Optional[str] = ""

    # charpente (options cochées)
    charp_options: List[str] = []


class WorkRequestOut(BaseModel):
    id: int
    created_at: str
    status: str

    name: str
    email: str
    commune: str

    lot_type: str
    surface_m2: str
    budget: str
    message: str

    cover_type: str
    cover_surface_m2: str
    insulation: bool
    sarking: bool

    gouttiere_ml: str
    habillage_rives_ml: str
    habillage_mur_m2: str
    couverture_zinc_m2: str
    tour_cheminee_nb: str

    charp_options: str


def require_admin(x_admin_token: Optional[str]):
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=500, detail="ADMIN_TOKEN non configuré")
    if (x_admin_token or "") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Admin token invalide")


# ---------- Auth PRO ----------
@app.post("/register")
def register_pro(data: ProRegisterIn, db: Session = Depends(get_db)):
    if db.query(ProUser).filter(ProUser.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    user = ProUser(
        name=data.name.strip(),
        email=data.email,
        password_hash=pwd_context.hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "ok", "user_id": user.id}


@app.post("/login")
def login_pro(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(ProUser).filter(ProUser.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return {"message": "ok", "user_id": user.id, "name": user.name, "email": user.email}


# ---------- Auth Artisan ----------
@app.post("/artisan/register")
def register_artisan(data: ArtisanRegisterIn, db: Session = Depends(get_db)):
    if db.query(ArtisanUser).filter(ArtisanUser.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    artisan = ArtisanUser(
        contact_name=data.contact_name.strip(),
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        commune=data.commune.strip(),
        radius_km=int(data.radius_km),
        phone=(data.phone or "").strip(),
        zone_note=(data.zone_note or "").strip(),
    )
    db.add(artisan)
    db.commit()
    db.refresh(artisan)
    return {"message": "ok", "artisan_id": artisan.id}


@app.post("/artisan/login")
def login_artisan(data: LoginIn, db: Session = Depends(get_db)):
    artisan = db.query(ArtisanUser).filter(ArtisanUser.email == data.email).first()
    if not artisan or not pwd_context.verify(data.password, artisan.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return {
        "message": "ok",
        "artisan_id": artisan.id,
        "contact_name": artisan.contact_name,
        "email": artisan.email,
    }


# ---------- Demandes ----------
@app.post("/requests")
def create_request(data: WorkRequestIn, db: Session = Depends(get_db)):
    # minimum obligatoire
    if not data.name.strip() or not data.commune.strip() or not data.surface_m2.strip():
        raise HTTPException(status_code=422, detail="Nom, commune et m² obligatoires")

    req = WorkRequest(
        name=data.name.strip(),
        email=data.email,
        commune=data.commune.strip(),
        surface_m2=data.surface_m2.strip(),
        lot_type=(data.lot_type or "lot").strip(),
        budget=(data.budget or "").strip(),
        message=(data.message or "").strip(),

        cover_type=(data.cover_type or "").strip(),
        cover_surface_m2=(data.cover_surface_m2 or "").strip(),
        insulation=bool(data.insulation),
        sarking=bool(data.sarking),

        gouttiere_ml=(data.gouttiere_ml or "").strip(),
        habillage_rives_ml=(data.habillage_rives_ml or "").strip(),
        habillage_mur_m2=(data.habillage_mur_m2 or "").strip(),
        couverture_zinc_m2=(data.couverture_zinc_m2 or "").strip(),
        tour_cheminee_nb=(data.tour_cheminee_nb or "").strip(),

        charp_options=";".join([x.strip() for x in (data.charp_options or []) if x.strip()]),
        status="nouvelle",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"message": "ok", "request_id": req.id}


@app.get("/requests", response_model=list[WorkRequestOut])
def list_requests(db: Session = Depends(get_db)):
    items = db.query(WorkRequest).order_by(WorkRequest.created_at.desc()).all()
    out = []
    for r in items:
        out.append(
            WorkRequestOut(
                id=r.id,
                created_at=r.created_at.isoformat(),
                status=r.status,

                name=r.name,
                email=r.email,
                commune=r.commune,

                lot_type=r.lot_type,
                surface_m2=r.surface_m2,
                budget=r.budget or "",
                message=r.message or "",

                cover_type=r.cover_type or "",
                cover_surface_m2=r.cover_surface_m2 or "",
                insulation=bool(r.insulation),
                sarking=bool(r.sarking),

                gouttiere_ml=r.gouttiere_ml or "",
                habillage_rives_ml=r.habillage_rives_ml or "",
                habillage_mur_m2=r.habillage_mur_m2 or "",
                couverture_zinc_m2=r.couverture_zinc_m2 or "",
                tour_cheminee_nb=r.tour_cheminee_nb or "",

                charp_options=r.charp_options or "",
            )
        )
    return out


# ---------- Artisan: traiter une demande ----------
class TreatIn(BaseModel):
    artisan_id: int
    action: str  # "treat" / "later"


@app.post("/artisan/requests/{request_id}/treat")
def artisan_treat_request(request_id: int, data: TreatIn, db: Session = Depends(get_db)):
    req = db.query(WorkRequest).filter(WorkRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Demande introuvable")

    artisan = db.query(ArtisanUser).filter(ArtisanUser.id == data.artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan introuvable")

    if data.action == "later":
        return {"message": "ok", "status": req.status}

    if data.action != "treat":
        raise HTTPException(status_code=422, detail="action invalide (treat/later)")

    # crée une assignation si pas déjà
    existing = db.query(RequestAssignment).filter(
        RequestAssignment.request_id == request_id,
        RequestAssignment.artisan_id == data.artisan_id,
    ).first()

    if not existing:
        assign = RequestAssignment(request_id=request_id, artisan_id=data.artisan_id, status="en_traitement")
        db.add(assign)

    # statut global
    req.status = "en_traitement"
    db.commit()
    db.refresh(req)

    return {"message": "ok", "request_status": req.status}
