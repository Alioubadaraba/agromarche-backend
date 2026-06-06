from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings

router = APIRouter()

VILLES_SENEGAL = {
    "dakar":       {"nom": "Dakar",       "lat": 14.6937, "lon": -17.4441},
    "thies":       {"nom": "Thiès",       "lat": 14.7886, "lon": -16.9261},
    "kaolack":     {"nom": "Kaolack",     "lat": 14.1652, "lon": -16.0726},
    "ziguinchor":  {"nom": "Ziguinchor",  "lat": 12.5605, "lon": -16.2719},
    "saint-louis": {"nom": "Saint-Louis", "lat": 16.0179, "lon": -16.4896},
}

METEO_DEMO = {
    "dakar":       {"temperature":28, "description":"Partiellement nuageux", "humidite":72, "vent_kmh":14, "pluie_prob":60},
    "thies":       {"temperature":30, "description":"Ensoleillé",             "humidite":65, "vent_kmh":12, "pluie_prob":20},
    "kaolack":     {"temperature":33, "description":"Chaud et sec",           "humidite":55, "vent_kmh":10, "pluie_prob":15},
    "ziguinchor":  {"temperature":27, "description":"Nuageux avec pluies",    "humidite":85, "vent_kmh":8,  "pluie_prob":80},
    "saint-louis": {"temperature":26, "description":"Brumeux",                "humidite":78, "vent_kmh":18, "pluie_prob":30},
}

@router.get("/{ville}")
async def get_meteo(ville: str):
    ville_lower = ville.lower()
    if ville_lower not in VILLES_SENEGAL:
        raise HTTPException(status_code=404, detail=f"Ville '{ville}' non supportée.")

    info = VILLES_SENEGAL[ville_lower]
    demo = METEO_DEMO[ville_lower]

    if not settings.OPENWEATHER_API_KEY:
        return {
            "ville": info["nom"],
            "temperature": demo["temperature"],
            "description": demo["description"],
            "humidite": demo["humidite"],
            "vent_kmh": demo["vent_kmh"],
            "pluie_prob": demo["pluie_prob"],
            "conseil": _conseil_agricole(demo["temperature"], demo["humidite"]),
            "coordonnees": {"lat": info["lat"], "lon": info["lon"]},
            "mode": "demo"
        }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": info["lat"], "lon": info["lon"], "appid": settings.OPENWEATHER_API_KEY, "units": "metric", "lang": "fr"}
        )
        data = resp.json()
        return {
            "ville": info["nom"],
            "temperature": round(data["main"]["temp"]),
            "description": data["weather"][0]["description"],
            "humidite": data["main"]["humidity"],
            "vent_kmh": round(data["wind"]["speed"] * 3.6),
            "pluie_prob": data.get("clouds", {}).get("all", 0),
            "conseil": _conseil_agricole(data["main"]["temp"], data["main"]["humidity"]),
            "coordonnees": {"lat": info["lat"], "lon": info["lon"]}
        }

def _conseil_agricole(temp: float, humidite: int) -> str:
    if temp > 35:
        return "Chaleur excessive. Irriguez tôt le matin ou en soirée, couvrez les jeunes plants."
    if humidite > 80:
        return "Humidité élevée — risque de champignons. Vérifiez vos cultures, aérez si possible."
    if temp < 18:
        return "Températures fraîches. Protégez les cultures sensibles au froid."
    return "Évitez d'irriguer entre 11h et 15h. Bon moment pour semer."
