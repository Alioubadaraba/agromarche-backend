import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.prix import Produit, Region
from app.ml.train import entrainer_modele, predire

router = APIRouter()

MODELS_DIR = "app/ml/models"
os.makedirs(MODELS_DIR, exist_ok=True)  # le disque de Render est vidé à chaque redémarrage


def _trouver(db: Session, produit: str, region: str):
    p = db.query(Produit).filter(Produit.nom.ilike(f"%{produit}%")).first()
    r = db.query(Region).filter(Region.code == region.lower()).first()
    if not p:
        raise HTTPException(404, detail=f"Produit '{produit}' introuvable")
    if not r:
        raise HTTPException(404, detail=f"Région '{region}' introuvable")
    return p, r


@router.post("/train")
def train(produit: str, region: str, db: Session = Depends(get_db)):
    """Entraîne un modèle ML pour un produit et une région donnés."""
    p, r = _trouver(db, produit, region)
    result = entrainer_modele(p.id, r.id)
    return {"produit": p.nom, "region": r.nom, **result}


@router.get("/predict")
def predict(produit: str, region: str, db: Session = Depends(get_db)):
    """Prédit le prix futur. Réentraîne le modèle s'il n'existe plus."""
    p, r = _trouver(db, produit, region)
    result = predire(p.id, r.id)
    if "erreur" in result:  # modèle absent : on l'entraîne puis on réessaie
        entrainer_modele(p.id, r.id)
        result = predire(p.id, r.id)
    return {"produit": p.nom, "region": r.nom, **result}


@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """Liste tous les modèles entraînés disponibles."""
    if not os.path.exists(MODELS_DIR):
        return []
    result = []
    for f in os.listdir(MODELS_DIR):
        if not f.endswith(".joblib"):
            continue
        parts = f.replace("model_", "").replace(".joblib", "").split("_")
        if len(parts) != 2:
            continue
        try:
            pid, rid = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        p = db.query(Produit).filter(Produit.id == pid).first()
        r = db.query(Region).filter(Region.id == rid).first()
        result.append({
            "fichier": f,
            "produit": p.nom if p else pid,
            "region": r.nom if r else rid,
        })
    return result