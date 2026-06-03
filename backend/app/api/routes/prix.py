from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.core.database import get_db
from app.models.prix import PrixMarche, Region, Produit
from app.schemas.prix import PrixResponse, PrixParRegion, PrixCreate
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=list[PrixParRegion])
def get_tous_les_prix(db: Session = Depends(get_db)):
    regions = db.query(Region).all()
    result = []
    for region in regions:
        produits = _get_derniers_prix(db, region.id)
        result.append(PrixParRegion(region=region.nom, code_region=region.code, produits=produits))
    return result

@router.get("/{region_code}", response_model=list[PrixResponse])
def get_prix_par_region(
    region_code: str,
    produit: str | None = Query(None),
    db: Session = Depends(get_db)
):
    region = db.query(Region).filter(Region.code == region_code.lower()).first()
    if not region:
        raise HTTPException(status_code=404, detail=f"Région '{region_code}' introuvable")
    return _get_derniers_prix(db, region.id, region.nom, produit)

@router.post("/", response_model=PrixResponse, status_code=201)
def ajouter_prix(data: PrixCreate, db: Session = Depends(get_db)):
    nouveau = PrixMarche(**data.model_dump())
    db.add(nouveau)
    db.commit()
    db.refresh(nouveau)
    return PrixResponse(
        id=nouveau.id, region=nouveau.region.nom, produit=nouveau.produit.nom,
        unite=nouveau.produit.unite, prix=nouveau.prix, date=nouveau.date,
        source=nouveau.source, tendance=None
    )

def _get_derniers_prix(db, region_id, region_nom="", filtre_produit=None):
    sous_requete = (
        db.query(PrixMarche.produit_id, func.max(PrixMarche.date).label("date_max"))
        .filter(PrixMarche.region_id == region_id)
        .group_by(PrixMarche.produit_id)
        .subquery()
    )
    query = (
        db.query(PrixMarche)
        .join(Produit)
        .join(sous_requete, (PrixMarche.produit_id == sous_requete.c.produit_id) &
                            (PrixMarche.date == sous_requete.c.date_max))
        .filter(PrixMarche.region_id == region_id)
    )
    if filtre_produit:
        query = query.filter(Produit.nom.ilike(f"%{filtre_produit}%"))

    region = db.query(Region).filter(Region.id == region_id).first()
    return [
        PrixResponse(
            id=p.id, region=region.nom if region else region_nom,
            produit=p.produit.nom, unite=p.produit.unite,
            prix=p.prix, date=p.date, source=p.source,
            tendance=_calculer_tendance(db, p.produit_id, region_id, p.prix)
        )
        for p in query.all()
    ]

def _calculer_tendance(db, produit_id, region_id, prix_actuel):
    hier = datetime.utcnow() - timedelta(days=1)
    prix_hier = (
        db.query(PrixMarche)
        .filter(PrixMarche.produit_id == produit_id,
                PrixMarche.region_id == region_id,
                PrixMarche.date <= hier)
        .order_by(desc(PrixMarche.date))
        .first()
    )
    if prix_hier and prix_hier.prix > 0:
        return round(((prix_actuel - prix_hier.prix) / prix_hier.prix) * 100, 1)
    return None
