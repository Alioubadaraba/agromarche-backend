from pydantic import BaseModel

class AcheteurResponse(BaseModel):
    id: int
    nom: str
    type: str
    region: str
    telephone: str | None
    whatsapp: str | None
    produits: list[str]
    prix_moyen: float | None
    qte_min_kg: float
    description: str | None
    note: float
    distance_km: float | None = None

    class Config:
        from_attributes = True
