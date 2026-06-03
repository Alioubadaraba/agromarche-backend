from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurLogin, TokenResponse

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=201)
def inscription(data: UtilisateurCreate, db: Session = Depends(get_db)):
    """Créer un compte agriculteur ou acheteur."""
    if db.query(Utilisateur).filter(Utilisateur.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user = Utilisateur(
        nom=data.nom,
        email=data.email,
        telephone=data.telephone,
        mot_de_passe=hash_password(data.mot_de_passe),
        role=data.role,
        region=data.region
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        utilisateur={"id": user.id, "nom": user.nom, "role": user.role}
    )

@router.post("/login", response_model=TokenResponse)
def connexion(data: UtilisateurLogin, db: Session = Depends(get_db)):
    """Connexion avec email + mot de passe."""
    user = db.query(Utilisateur).filter(Utilisateur.email == data.email).first()
    if not user or not verify_password(data.mot_de_passe, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        utilisateur={"id": user.id, "nom": user.nom, "role": user.role}
    )
