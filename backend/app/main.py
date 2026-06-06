from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import prix, acheteurs, meteo, conseils, auth, ml, init, offres
from app.core.config import settings
from app.core.database import Base, engine
from app.models import prix as prix_model, utilisateur, acheteur, offre

# Créer les tables automatiquement au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgroMarché API",
    description="API pour connecter agriculteurs, marchés et données agricoles au Sénégal",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(offres.router, prefix="/api/offres", tags=["Offres"])
app.include_router(init.router, prefix="/api", tags=["Init"])
app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(prix.router,      prefix="/api/prix",      tags=["Prix"])
app.include_router(acheteurs.router, prefix="/api/acheteurs", tags=["Acheteurs"])
app.include_router(meteo.router,     prefix="/api/meteo",     tags=["Météo"])
app.include_router(ml.router,        prefix="/api/ml",        tags=["ML / Prédictions"])
app.include_router(conseils.router,  prefix="/api/conseils",  tags=["Conseils"])

@app.get("/")
def root():
    return {"message": "AgroMarché API v1.0 🌱", "status": "online"}
