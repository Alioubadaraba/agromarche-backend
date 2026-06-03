from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import prix, acheteurs, meteo, conseils, auth, ml
from app.core.config import settings

import logging
logging.basicConfig(level=logging.DEBUG)
app = FastAPI(
    title="AgroMarché API",
    description="API pour connecter agriculteurs, marchés et données agricoles au Sénégal",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(prix.router,      prefix="/api/prix",      tags=["Prix"])
app.include_router(acheteurs.router, prefix="/api/acheteurs", tags=["Acheteurs"])
app.include_router(meteo.router,     prefix="/api/meteo",     tags=["Météo"])
app.include_router(ml.router,      prefix="/api/ml",      tags=["ML / Prédictions"])
app.include_router(conseils.router,  prefix="/api/conseils",  tags=["Conseils"])

@app.get("/")
def root():
    return {"message": "AgroMarché API v1.0 🌱", "status": "online"}
