from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.acheteur import Acheteur
import json, math

router = APIRouter()

@router.get("/")
def get_acheteurs(
    produit: str | None = Query(None),
    region: str | None = Query(None),
    lat: float | None = Query(None),
    lon: float | None = Query(None),
    db: Session = Depends(get_db)
):
    """Liste les acheteurs, filtrable par produit, région ou position GPS."""
    query = db.query(Acheteur)
    if region:
        query = query.filter(Acheteur.region.ilike(f"%{region}%"))

    acheteurs = query.all()

    result = []
    for a in acheteurs:
        produits_list = json.loads(a.produits) if a.produits else []
        if produit and produit.lower() not in [p.lower() for p in produits_list]:
            continue
        distance = None
        if lat and lon and a.latitude and a.longitude:
            distance = round(_haversine(lat, lon, a.latitude, a.longitude), 1)
        result.append({
            "id": a.id,
            "nom": a.nom,
            "type": a.type,
            "region": a.region,
            "telephone": a.telephone,
            "whatsapp": a.whatsapp,
            "produits": produits_list,
            "prix_moyen": a.prix_moyen,
            "qte_min_kg": a.qte_min_kg,
            "description": a.description,
            "note": a.note,
            "distance_km": distance
        })

    if lat and lon:
        result.sort(key=lambda x: x["distance_km"] or 9999)
    return result

def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Distance en km entre deux coordonnées GPS."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
