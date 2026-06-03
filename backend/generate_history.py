import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.prix import PrixMarche, Region, Produit
from datetime import datetime, timedelta
import random

db = SessionLocal()

prix_base = {
    "dakar":      {"Tomates":450,"Oignons":310,"Mil":290,"Arachides":520,"Maïs":270,"Riz local":400,"Mangues":200,"Aubergines":380,"Choux":350},
    "thies":      {"Tomates":390,"Oignons":280,"Mil":275,"Maïs":260,"Mangues":180,"Arachides":500,"Niébé":420,"Aubergines":340},
    "kaolack":    {"Arachides":490,"Mil":280,"Maïs":255,"Niébé":410,"Riz local":380,"Oignons":300,"Manioc":150,"Tomates":420},
    "ziguinchor": {"Riz local":370,"Mangues":160,"Maïs":255,"Manioc":130,"Pastèques":120,"Tomates":400,"Niébé":390,"Arachides":470},
    "saint-louis":{"Tomates":410,"Oignons":290,"Mil":285,"Riz local":360,"Maïs":265,"Arachides":480,"Choux":320,"Pastèques":140},
}

regions = {r.code: r for r in db.query(Region).all()}
produits = {p.nom: p for p in db.query(Produit).all()}

count = 0
for region_code, produits_prix in prix_base.items():
    region = regions.get(region_code)
    if not region: continue
    for produit_nom, base in produits_prix.items():
        produit = produits.get(produit_nom)
        if not produit: continue
        prix_courant = base
        for j in range(180):
            date = datetime.utcnow() - timedelta(days=180-j)
            # Simulation réaliste : tendance + saisonnalité + bruit
            mois = date.month
            saison_factor = 1.1 if mois in [6,7,8] else 0.95 if mois in [12,1,2] else 1.0
            bruit = random.uniform(-0.03, 0.03)
            tendance = random.uniform(-0.005, 0.008)
            prix_courant = prix_courant * (1 + tendance + bruit) * saison_factor
            prix_courant = max(prix_courant, base * 0.5)

            existing = db.query(PrixMarche).filter(
                PrixMarche.region_id == region.id,
                PrixMarche.produit_id == produit.id,
                PrixMarche.date >= date.replace(hour=0, minute=0, second=0),
                PrixMarche.date < date.replace(hour=23, minute=59, second=59),
            ).first()
            if not existing:
                db.add(PrixMarche(
                    region_id=region.id,
                    produit_id=produit.id,
                    prix=round(prix_courant),
                    date=date,
                    source="Historique simulé"
                ))
                count += 1

db.commit()
print(f"✅ {count} entrées d'historique générées (6 mois)")
