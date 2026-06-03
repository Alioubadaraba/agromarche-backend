# AgroMarché 🌱

Application web/mobile pour connecter les agriculteurs sénégalais aux marchés.

## Démarrage rapide

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # Éditez avec vos vraies valeurs
uvicorn app.main:app --reload
```

Documentation API interactive : http://localhost:8000/docs

## Endpoints principaux

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | /api/auth/register | Créer un compte |
| POST | /api/auth/login | Se connecter |
| GET | /api/prix/ | Tous les prix par région |
| GET | /api/prix/{region} | Prix d'une région (ex: dakar) |
| GET | /api/acheteurs/?produit=tomates | Acheteurs par produit |
| GET | /api/meteo/{ville} | Météo + conseil agricole |
| GET | /api/conseils/ | Conseils de saison |

## Déploiement Railway

1. Pusher le code sur GitHub
2. Connecter le repo sur railway.app
3. Ajouter les variables d'environnement
4. Railway détecte Python automatiquement ✅
