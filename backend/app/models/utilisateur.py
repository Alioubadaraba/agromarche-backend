from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime
from app.core.database import Base
import enum

class RoleEnum(str, enum.Enum):
    agriculteur = "agriculteur"
    acheteur    = "acheteur"
    admin       = "admin"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id           = Column(Integer, primary_key=True)
    nom          = Column(String(100), nullable=False)
    email        = Column(String(150), unique=True, nullable=False)
    telephone    = Column(String(20))
    mot_de_passe = Column(String(255), nullable=False)
    role         = Column(Enum(RoleEnum), default=RoleEnum.agriculteur)
    region       = Column(String(100))
    actif        = Column(Boolean, default=True)
    cree_le      = Column(DateTime, default=datetime.utcnow)
