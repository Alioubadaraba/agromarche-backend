from pydantic import BaseModel
from datetime import datetime

class PrixBase(BaseModel):
    prix: float
    source: str | None = None

class PrixCreate(PrixBase):
    region_id: int
    produit_id: int

class PrixResponse(PrixBase):
    id: int
    region: str
    produit: str
    unite: str
    date: datetime
    tendance: float | None = None   # % variation vs jour précédent

    class Config:
        from_attributes = True

class PrixParRegion(BaseModel):
    region: str
    code_region: str
    produits: list[PrixResponse]
