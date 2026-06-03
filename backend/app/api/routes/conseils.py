from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def get_conseils(region: str | None = None):
    """Retourne les conseils agricoles du moment selon la saison."""
    mois = datetime.utcnow().month
    saison = _get_saison(mois)
    return {
        "saison": saison,
        "mois": mois,
        "conseils": CONSEILS_PAR_SAISON.get(saison, [])
    }

def _get_saison(mois: int) -> str:
    if mois in [6, 7, 8, 9, 10]:
        return "hivernage"
    if mois in [11, 12, 1, 2]:
        return "saison_seche_froide"
    return "saison_seche_chaude"

CONSEILS_PAR_SAISON = {
    "hivernage": [
        {"categorie": "Saison", "titre": "Début d'hivernage — préparez vos semis", "texte": "Les premières pluies arrivent. Idéal pour semer le sorgho, le mil et le niébé."},
        {"categorie": "Sol", "titre": "Amender le sol avant les pluies", "texte": "Apportez du compost ou du fumier. L'humidité facilitera la dégradation organique."},
        {"categorie": "Santé", "titre": "Surveillance des pucerons sur oignons", "texte": "Inspectez le dessous des feuilles deux fois par semaine. Savon insecticide si nécessaire."},
    ],
    "saison_seche_froide": [
        {"categorie": "Récolte", "titre": "Période de récolte des céréales", "texte": "Mil, sorgho et maïs sont prêts. Récoltez par temps sec pour éviter les moisissures."},
        {"categorie": "Maraîchage", "titre": "Saison idéale pour les légumes", "texte": "Tomates, oignons, choux profitent des nuits fraîches. Arrosage réduit."},
    ],
    "saison_seche_chaude": [
        {"categorie": "Eau", "titre": "Gérez l'eau avec soin", "texte": "Irriguez tôt le matin (5h–8h) pour limiter l'évaporation. Paillage recommandé."},
        {"categorie": "Sol", "titre": "Préparez vos champs", "texte": "Labour et préparation des sillons avant l'hivernage. Bonne période pour le compostage."},
    ],
}
