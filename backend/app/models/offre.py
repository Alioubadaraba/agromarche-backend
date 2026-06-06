from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.core.database import Base

class Offre(Base):
    __tablename__ = "offres"
    id            = Column(Integer, primary_key=True)
    acheteur_nom  = Column(String(150), nullable=False)
    acheteur_tel  = Column(String(20))
    acheteur_wa   = Column(String(20))
    produit       = Column(String(100), nullable=False)
    quantite_kg   = Column(Float, nullable=False)
    prix_propose  = Column(Float, nullable=False)
    region        = Column(String(100), nullable=False)
    description   = Column(Text)
    statut        = Column(String(20), default="active")  # active, fermee
    cree_le       = Column(DateTime, default=datetime.utcnow)
