from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.prix import Produit, Region
from app.ml.train import entrainer_modele, predire

router = APIRouter()

@router.post("/train")
def train(produit: str, region: str, db: Session = Depends(get_db)):
    """Entraîne un modèle ML pour un produit et une région donnés."""
    p = db.query(Produit).filter(Produit.nom.ilike(f"%{produit}%")).first()
    r = db.query(Region).filter(Region.code == region.lower()).first()

    if not p:
        raise HTTPException(404, detail=f"Produit '{produit}' introuvable")
    if not r:
        raise HTTPException(404, detail=f"Région '{region}' introuvable")

    result = entrainer_modele(p.id, r.id)
    return {"produit": p.nom, "region": r.nom, **result}

@router.get("/predict")
def predict(produit: str, region: str, db: Session = Depends(get_db)):
    """Prédit le prix futur et le meilleur moment pour vendre."""
    p = db.query(Produit).filter(Produit.nom.ilike(f"%{produit}%")).first()
    r = db.query(Region).filter(Region.code == region.lower()).first()

    if not p:
        raise HTTPException(404, detail=f"Produit '{produit}' introuvable")
    if not r:
        raise HTTPException(404, detail=f"Région '{region}' introuvable")

    result = predire(p.id, r.id)
    return {"produit": p.nom, "region": r.nom, **result}

@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """Liste tous les modèles entraînés disponibles."""
    import os
    models_dir = "app/ml/models"
    if not os.path.exists(models_dir):
        return []
    fichiers = [f for f in os.listdir(models_dir) if f.endswith(".joblib")]
    result = []
    for f in fichiers:
        parts = f.replace("model_","").replace(".joblib","").split("_")
        if len(parts) == 2:
            try:
                pid, rid = int(parts[0]), int(parts[1])
                p = db.query(Produit).filter(Produit.id == pid).first()
                r = db.query(Region).filter(Region.id == rid).first()
                result.append({
                    "fichier": f,
                    "produit": p.nom if p else pid,
                    "region":  r.nom if r else rid,
                })
            except: pass
    return result
