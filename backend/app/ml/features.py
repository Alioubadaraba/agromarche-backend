import pandas as pd
import numpy as np
from datetime import datetime

def extraire_features(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme l'historique des prix en features ML."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Features temporelles
    df["jour_semaine"] = df["date"].dt.dayofweek
    df["mois"]         = df["date"].dt.month
    df["trimestre"]    = df["date"].dt.quarter
    df["jour_annee"]   = df["date"].dt.dayofyear

    # Saison sénégalaise
    def saison(mois):
        if mois in [6,7,8,9,10]:   return 0  # hivernage
        if mois in [11,12,1,2]:    return 1  # saison sèche froide
        return 2                              # saison sèche chaude
    df["saison"] = df["mois"].apply(saison)

    # Features prix (lag)
    df["prix_lag1"]  = df["prix"].shift(1)
    df["prix_lag7"]  = df["prix"].shift(7)
    df["prix_lag30"] = df["prix"].shift(30)

    # Moyennes mobiles
    df["ma_7"]  = df["prix"].rolling(7,  min_periods=1).mean()
    df["ma_30"] = df["prix"].rolling(30, min_periods=1).mean()

    # Volatilité
    df["volatilite_7"] = df["prix"].rolling(7, min_periods=1).std().fillna(0)

    # Variation
    df["variation_1j"] = df["prix"].pct_change(1).fillna(0)
    df["variation_7j"] = df["prix"].pct_change(7).fillna(0)

    return df.dropna(subset=["prix_lag1"])

FEATURE_COLS = [
    "jour_semaine","mois","trimestre","jour_annee","saison",
    "prix_lag1","prix_lag7","prix_lag30",
    "ma_7","ma_30","volatilite_7",
    "variation_1j","variation_7j"
]
