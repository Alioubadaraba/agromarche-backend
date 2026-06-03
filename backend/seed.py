import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prix import Region, Produit, PrixMarche
from app.models.acheteur import Acheteur
from datetime import datetime, timedelta
import random
import json

db = SessionLocal()

print("🌱 Initialisation des données AgroMarché...")

# ─── RÉGIONS ───────────────────────────────────────────────
regions_data = [
    {"nom": "Dakar",       "code": "dakar"},
    {"nom": "Thiès",       "code": "thies"},
    {"nom": "Kaolack",     "code": "kaolack"},
    {"nom": "Ziguinchor",  "code": "ziguinchor"},
    {"nom": "Saint-Louis", "code": "saint-louis"},
]

regions = {}
for r in regions_data:
    existing = db.query(Region).filter(Region.code == r["code"]).first()
    if not existing:
        obj = Region(**r)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        regions[r["code"]] = obj
    else:
        regions[r["code"]] = existing
print(f"✅ {len(regions)} régions")

# ─── PRODUITS ──────────────────────────────────────────────
produits_data = [
    {"nom": "Tomates",    "unite": "kg",  "categorie": "Légumes"},
    {"nom": "Oignons",    "unite": "kg",  "categorie": "Légumes"},
    {"nom": "Mil",        "unite": "kg",  "categorie": "Céréales"},
    {"nom": "Maïs",       "unite": "kg",  "categorie": "Céréales"},
    {"nom": "Arachides",  "unite": "kg",  "categorie": "Oléagineux"},
    {"nom": "Riz local",  "unite": "kg",  "categorie": "Céréales"},
    {"nom": "Mangues",    "unite": "kg",  "categorie": "Fruits"},
    {"nom": "Pastèques",  "unite": "kg",  "categorie": "Fruits"},
    {"nom": "Niébé",      "unite": "kg",  "categorie": "Légumineuses"},
    {"nom": "Manioc",     "unite": "kg",  "categorie": "Tubercules"},
    {"nom": "Aubergines", "unite": "kg",  "categorie": "Légumes"},
    {"nom": "Choux",      "unite": "pièce","categorie": "Légumes"},
]

produits = {}
for p in produits_data:
    existing = db.query(Produit).filter(Produit.nom == p["nom"]).first()
    if not existing:
        obj = Produit(**p)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        produits[p["nom"]] = obj
    else:
        produits[p["nom"]] = existing
print(f"✅ {len(produits)} produits")

# ─── PRIX PAR RÉGION ───────────────────────────────────────
prix_data = {
    "dakar": {
        "Tomates": 450, "Oignons": 310, "Mil": 290,
        "Arachides": 520, "Maïs": 270, "Riz local": 400,
        "Mangues": 200, "Aubergines": 380, "Choux": 350,
    },
    "thies": {
        "Tomates": 390, "Oignons": 280, "Mil": 275,
        "Maïs": 260, "Mangues": 180, "Arachides": 500,
        "Niébé": 420, "Aubergines": 340,
    },
    "kaolack": {
        "Arachides": 490, "Mil": 280, "Maïs": 255,
        "Niébé": 410, "Riz local": 380, "Oignons": 300,
        "Manioc": 150, "Tomates": 420,
    },
    "ziguinchor": {
        "Riz local": 370, "Mangues": 160, "Maïs": 255,
        "Manioc": 130, "Pastèques": 120, "Tomates": 400,
        "Niébé": 390, "Arachides": 470,
    },
    "saint-louis": {
        "Tomates": 410, "Oignons": 290, "Mil": 285,
        "Riz local": 360, "Maïs": 265, "Arachides": 480,
        "Choux": 320, "Pastèques": 140,
    },
}

prix_count = 0
for region_code, produits_prix in prix_data.items():
    region = regions[region_code]
    for produit_nom, prix_base in produits_prix.items():
        if produit_nom not in produits:
            continue
        produit = produits[produit_nom]
        # Générer 3 jours d'historique pour les tendances
        for j in range(3):
            date = datetime.utcnow() - timedelta(days=2-j)
            variation = random.uniform(-0.05, 0.05)
            prix_jour = round(prix_base * (1 + variation * j))
            existing = db.query(PrixMarche).filter(
                PrixMarche.region_id == region.id,
                PrixMarche.produit_id == produit.id,
                PrixMarche.date >= date.replace(hour=0, minute=0),
            ).first()
            if not existing:
                obj = PrixMarche(
                    region_id=region.id,
                    produit_id=produit.id,
                    prix=prix_jour,
                    date=date,
                    source="Marché local"
                )
                db.add(obj)
                prix_count += 1

db.commit()
print(f"✅ {prix_count} entrées de prix")

# ─── ACHETEURS ─────────────────────────────────────────────
acheteurs_data = [
    {
        "nom": "Souleymane Fall",
        "type": "grossiste",
        "region": "Thiès",
        "latitude": 14.7886, "longitude": -16.9261,
        "telephone": "+221771234567",
        "whatsapp": "221771234567",
        "produits": json.dumps(["Tomates", "Oignons", "Aubergines"]),
        "prix_moyen": 450.0, "qte_min_kg": 200.0,
        "description": "Grossiste fiable, collecte mardi et vendredi. Paie à la livraison.",
        "note": 4.8,
    },
    {
        "nom": "Marché de Dieuppeul",
        "type": "marche_local",
        "region": "Dakar",
        "latitude": 14.7200, "longitude": -17.4700,
        "telephone": "+221338001234",
        "whatsapp": "221338001234",
        "produits": json.dumps(["Tomates", "Oignons", "Choux", "Aubergines"]),
        "prix_moyen": 420.0, "qte_min_kg": 50.0,
        "description": "Marché local Dakar. Livraison tôt le matin (5h–8h). Petits volumes acceptés.",
        "note": 4.2,
    },
    {
        "nom": "Agro-Sénégal Export",
        "type": "exportateur",
        "region": "Dakar",
        "latitude": 14.6800, "longitude": -17.4200,
        "telephone": "+221339001234",
        "whatsapp": "221339001234",
        "produits": json.dumps(["Mangues", "Pastèques", "Tomates"]),
        "prix_moyen": 380.0, "qte_min_kg": 2000.0,
        "description": "Exportateur zone industrielle. Normes qualité export requises. Paiement 30 jours.",
        "note": 4.0,
    },
    {
        "nom": "Coopérative de Kaolack",
        "type": "cooperative",
        "region": "Kaolack",
        "latitude": 14.1652, "longitude": -16.0726,
        "telephone": "+221771112233",
        "whatsapp": "221771112233",
        "produits": json.dumps(["Arachides", "Mil", "Niébé", "Maïs"]),
        "prix_moyen": 490.0, "qte_min_kg": 500.0,
        "description": "Coopérative agricole. Meilleurs prix pour arachides et céréales. Paiement immédiat.",
        "note": 4.6,
    },
    {
        "nom": "Ibrahima Diallo",
        "type": "grossiste",
        "region": "Ziguinchor",
        "latitude": 12.5605, "longitude": -16.2719,
        "telephone": "+221775556677",
        "whatsapp": "221775556677",
        "produits": json.dumps(["Mangues", "Manioc", "Riz local", "Pastèques"]),
        "prix_moyen": 200.0, "qte_min_kg": 300.0,
        "description": "Grossiste Casamance. Spécialiste fruits tropicaux. Collecte à domicile possible.",
        "note": 4.4,
    },
    {
        "nom": "Marché Central Saint-Louis",
        "type": "marche_local",
        "region": "Saint-Louis",
        "latitude": 16.0179, "longitude": -16.4896,
        "telephone": "+221338901234",
        "whatsapp": "221338901234",
        "produits": json.dumps(["Oignons", "Tomates", "Mil", "Riz local"]),
        "prix_moyen": 350.0, "qte_min_kg": 100.0,
        "description": "Grand marché Saint-Louis. Ouvert tous les jours. Volume moyen accepté.",
        "note": 4.1,
    },
]

acheteur_count = 0
for a in acheteurs_data:
    existing = db.query(Acheteur).filter(Acheteur.nom == a["nom"]).first()
    if not existing:
        obj = Acheteur(**a)
        db.add(obj)
        acheteur_count += 1

db.commit()
print(f"✅ {acheteur_count} acheteurs")
print("\n🎉 Base de données initialisée avec succès !")
print("   Relancez uvicorn et testez les endpoints /api/prix/dakar et /api/acheteurs/")
