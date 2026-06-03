from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base

class Acheteur(Base):
    __tablename__ = "acheteurs"
    id          = Column(Integer, primary_key=True)
    nom         = Column(String(150), nullable=False)
    type        = Column(String(50))       # grossiste, marche_local, exportateur
    region      = Column(String(100))
    latitude    = Column(Float)
    longitude   = Column(Float)
    telephone   = Column(String(20))
    whatsapp    = Column(String(20))
    produits    = Column(Text)             # JSON list: ["tomates","oignons"]
    prix_moyen  = Column(Float)
    qte_min_kg  = Column(Float, default=50)
    description = Column(Text)
    note        = Column(Float, default=0)
