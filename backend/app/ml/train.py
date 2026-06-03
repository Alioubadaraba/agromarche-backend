import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
from app.ml.features import extraire_features, FEATURE_COLS
from app.core.database import SessionLocal
from app.models.prix import PrixMarche, Produit, Region

MODELS_DIR = "app/ml/models"
os.makedirs(MODELS_DIR, exist_ok=True)

def charger_donnees(produit_id: int, region_id: int) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = (
            db.query(PrixMarche)
            .filter(PrixMarche.produit_id == produit_id,
                    PrixMarche.region_id == region_id)
            .order_by(PrixMarche.date)
            .all()
        )
        return pd.DataFrame([{"date": r.date, "prix": r.prix} for r in rows])
    finally:
        db.close()

def entrainer_modele(produit_id: int, region_id: int) -> dict:
    """Entraîne un modèle Random Forest pour un produit/région."""
    df = charger_donnees(produit_id, region_id)

    if len(df) < 10:
        return {"erreur": "Pas assez de données (minimum 10 entrées)"}

    df = extraire_features(df)

    # Target : prix dans 30 jours
    df["target"] = df["prix"].shift(-30)
    df = df.dropna(subset=["target"] + FEATURE_COLS)

    if len(df) < 5:
        return {"erreur": "Pas assez de données après feature engineering"}

    X = df[FEATURE_COLS]
    y = df["target"]

    # Comparer 3 modèles
    modeles = {
        "random_forest":      RandomForestRegressor(n_estimators=100, random_state=42),
        "gradient_boosting":  GradientBoostingRegressor(n_estimators=100, random_state=42),
        "ridge":              Pipeline([("scaler", StandardScaler()), ("model", Ridge())]),
    }

    meilleur_nom  = None
    meilleur_score = -999
    resultats = {}

    for nom, modele in modeles.items():
        try:
            scores = cross_val_score(modele, X, y, cv=min(3, len(X)),
                                     scoring="neg_mean_absolute_error")
            mae = -scores.mean()
            resultats[nom] = round(mae, 2)
            if -mae > meilleur_score:
                meilleur_score = -mae
                meilleur_nom   = nom
        except Exception as e:
            resultats[nom] = str(e)

    # Entraîner le meilleur sur tout le dataset
    meilleur_modele = modeles[meilleur_nom]
    meilleur_modele.fit(X, y)

    # Sauvegarder
    chemin = f"{MODELS_DIR}/model_{produit_id}_{region_id}.joblib"
    joblib.dump({"modele": meilleur_modele, "feature_cols": FEATURE_COLS,
                 "produit_id": produit_id, "region_id": region_id}, chemin)

    # Métriques finales
    y_pred = meilleur_modele.predict(X)
    mae_final = mean_absolute_error(y, y_pred)
    r2_final  = r2_score(y, y_pred)

    return {
        "modele_choisi": meilleur_nom,
        "comparaison_modeles": resultats,
        "mae": round(mae_final, 2),
        "r2":  round(r2_final, 4),
        "nb_observations": len(df),
        "chemin": chemin
    }

def predire(produit_id: int, region_id: int, horizon_jours: int = 30) -> dict:
    """Prédit le prix futur et le meilleur moment pour vendre."""
    chemin = f"{MODELS_DIR}/model_{produit_id}_{region_id}.joblib"

    if not os.path.exists(chemin):
        return {"erreur": "Modèle non entraîné. Lancez d'abord /api/ml/train"}

    artefact = joblib.load(chemin)
    modele   = artefact["modele"]

    df = charger_donnees(produit_id, region_id)
    if df.empty:
        return {"erreur": "Aucune donnée disponible"}

    df = extraire_features(df)
    derniere_ligne = df[FEATURE_COLS].iloc[-1:]

    prix_actuel  = float(df["prix"].iloc[-1])
    prix_predit  = float(modele.predict(derniere_ligne)[0])
    variation    = round(((prix_predit - prix_actuel) / prix_actuel) * 100, 1)

    # Simuler les 30 prochains jours pour trouver le meilleur moment
    predictions_jours = []
    df_sim = df.copy()

    for j in range(1, horizon_jours + 1):
        try:
            x = df_sim[FEATURE_COLS].iloc[-1:]
            p = float(modele.predict(x)[0])
            predictions_jours.append({"jour": j, "prix_predit": round(p)})
            # Simuler une nouvelle ligne
            nouvelle = df_sim.iloc[-1:].copy()
            nouvelle["prix"]      = p
            nouvelle["jour_annee"] = (nouvelle["jour_annee"] + 1) % 365
            df_sim = pd.concat([df_sim, nouvelle], ignore_index=True)
            df_sim = extraire_features(df_sim)
        except:
            break

    if predictions_jours:
        meilleur_jour = max(predictions_jours, key=lambda x: x["prix_predit"])
        pire_jour     = min(predictions_jours, key=lambda x: x["prix_predit"])
    else:
        meilleur_jour = pire_jour = None

    conseil = _generer_conseil(variation, meilleur_jour)

    return {
        "prix_actuel":      round(prix_actuel),
        "prix_predit_j30":  round(prix_predit),
        "variation_pct":    variation,
        "tendance":         "hausse" if variation > 2 else "baisse" if variation < -2 else "stable",
        "meilleur_moment":  meilleur_jour,
        "pire_moment":      pire_jour,
        "predictions_30j":  predictions_jours,
        "conseil":          conseil,
    }

def _generer_conseil(variation: float, meilleur_jour: dict) -> str:
    if variation > 10:
        return f"📈 Prix en forte hausse prévue (+{variation}%). Attendez avant de vendre !"
    if variation > 2:
        return f"📈 Prix en légère hausse (+{variation}%). Bon moment pour patienter."
    if variation < -10:
        return f"📉 Prix en forte baisse prévue ({variation}%). Vendez rapidement !"
    if variation < -2:
        return f"📉 Prix en légère baisse ({variation}%). Envisagez de vendre maintenant."
    if meilleur_jour:
        return f"📊 Prix stable. Meilleur moment : jour {meilleur_jour['jour']} ({meilleur_jour['prix_predit']} FCFA)."
    return "📊 Prix relativement stable sur les 30 prochains jours."
