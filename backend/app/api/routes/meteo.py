from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings

router = APIRouter()

VILLES_SENEGAL = {
    "dakar": (14.6937, -17.4441),
    "thies": (14.7886, -16.9261),
    "kaolack": (14.1652, -16.0726),
    "ziguinchor": (12.5605, -16.2719),
    "saint-louis": (16.0179, -16.4896),
}

@router.get("/{ville}")
async def get_meteo(ville: str):
    """Météo actuelle + conseil agricole pour une ville sénégalaise."""
    ville_lower = ville.lower()
    if ville_lower not in VILLES_SENEGAL:
        raise HTTPException(status_code=404, detail=f"Ville '{ville}' non supportée. Villes disponibles: {list(VILLES_SENEGAL.keys())}")

    lat, lon = VILLES_SENEGAL[ville_lower]

    if not settings.OPENWEATHER_API_KEY:
        return _meteo_demo(ville_lower, lat, lon)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": "metric", "lang": "fr"}
        )
        data = resp.json()
        return {
            "ville": ville.title(),
            "temperature": round(data["main"]["temp"]),
            "description": data["weather"][0]["description"],
            "humidite": data["main"]["humidity"],
            "vent_kmh": round(data["wind"]["speed"] * 3.6),
            "pluie_prob": data.get("clouds", {}).get("all", 0),
            "conseil": _conseil_agricole(data["main"]["temp"], data["main"]["humidity"]),
            "coordonnees": {"lat": lat, "lon": lon}
        }

def _meteo_demo(ville, lat, lon):
    return {
        "ville": ville.title(),
        "temperature": 28,
        "description": "Partiellement nuageux",
        "humidite": 72,
        "vent_kmh": 14,
        "pluie_prob": 60,
        "conseil": "Évitez d'irriguer entre 11h et 15h. Bon moment pour semer.",
        "coordonnees": {"lat": lat, "lon": lon},
        "mode": "demo"
    }

def _conseil_agricole(temp: float, humidite: int) -> str:
    if temp > 35:
        return "Chaleur excessive. Irriguez tôt le matin ou en soirée, couvrez les jeunes plants."
    if humidite > 80:
        return "Humidité élevée — risque de champignons. Vérifiez vos cultures, aérez si possible."
    if temp < 18:
        return "Températures fraîches. Protégez les cultures sensibles au froid."
    return "Conditions favorables. Bon moment pour les travaux agricoles."
