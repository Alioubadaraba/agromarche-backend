from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.offre import Offre
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class OffreCreate(BaseModel):
    acheteur_nom: str
    acheteur_tel: str | None = None
    acheteur_wa:  str | None = None
    produit:      str
    quantite_kg:  float
    prix_propose: float
    region:       str
    description:  str | None = None

class OffreResponse(BaseModel):
    id:           int
    acheteur_nom: str
    acheteur_tel: str | None
    acheteur_wa:  str | None
    produit:      str
    quantite_kg:  float
    prix_propose: float
    region:       str
    description:  str | None
    statut:       str
    cree_le:      datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=OffreResponse, status_code=201)
def creer_offre(data: OffreCreate, db: Session = Depends(get_db)):
    """Un acheteur publie une offre d'achat."""
    offre = Offre(**data.model_dump())
    db.add(offre)
    db.commit()
    db.refresh(offre)
    return offre

@router.get("/", response_model=list[OffreResponse])
def get_offres(
    region: str | None = None,
    produit: str | None = None,
    db: Session = Depends(get_db)
):
    """Les agriculteurs voient les offres disponibles."""
    query = db.query(Offre).filter(Offre.statut == "active").order_by(desc(Offre.cree_le))
    if region:
        query = query.filter(Offre.region.ilike(f"%{region}%"))
    if produit:
        query = query.filter(Offre.produit.ilike(f"%{produit}%"))
    return query.limit(50).all()

@router.delete("/{offre_id}")
def fermer_offre(offre_id: int, db: Session = Depends(get_db)):
    """Fermer une offre."""
    offre = db.query(Offre).filter(Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    offre.statut = "fermee"
    db.commit()
    return {"message": "Offre fermée"}
