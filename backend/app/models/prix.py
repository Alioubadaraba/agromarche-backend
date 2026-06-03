from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Region(Base):
    __tablename__ = "regions"
    id       = Column(Integer, primary_key=True)
    nom      = Column(String(100), nullable=False)
    code     = Column(String(20), unique=True, nullable=False)
    prix     = relationship("PrixMarche", back_populates="region")

class Produit(Base):
    __tablename__ = "produits"
    id          = Column(Integer, primary_key=True)
    nom         = Column(String(100), nullable=False)
    unite       = Column(String(20), default="kg")
    categorie   = Column(String(50))
    prix        = relationship("PrixMarche", back_populates="produit")

class PrixMarche(Base):
    __tablename__ = "prix_marche"
    id          = Column(Integer, primary_key=True)
    region_id   = Column(Integer, ForeignKey("regions.id"))
    produit_id  = Column(Integer, ForeignKey("produits.id"))
    prix        = Column(Float, nullable=False)
    date        = Column(DateTime, default=datetime.utcnow)
    source      = Column(String(100))
    region      = relationship("Region",  back_populates="prix")
    produit     = relationship("Produit", back_populates="prix")
