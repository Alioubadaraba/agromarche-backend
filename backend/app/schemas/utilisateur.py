from pydantic import BaseModel, EmailStr

class UtilisateurCreate(BaseModel):
    nom: str
    email: EmailStr
    telephone: str | None = None
    mot_de_passe: str
    role: str = "agriculteur"
    region: str | None = None

class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    utilisateur: dict
