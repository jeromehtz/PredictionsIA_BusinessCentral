from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import numpy as np
import pandas as pd
from typing import List, Dict
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler


app = FastAPI()


# --- Modèle de données ---
class DonneesVentes(BaseModel):
    target_year: int
    target_month: int = 0  # 0 par défaut au lieu de None

CSVFileName = "output/sales_data.csv"


# --- Création et entraînement du modèle ML ---
def create_model(input_dim: int = 3):
    model = Sequential([
        Dense(64, activation='relu', input_shape=(input_dim,)),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def train_model_with_file(csv_filename=CSVFileName):
    df = None
    if os.path.exists(csv_filename):
        try:
            df = pd.read_csv(csv_filename, encoding='utf-8-sig', sep=';')
            df.columns = df.columns.str.strip().str.replace('\ufeff', '')
            print(f"CSV chargé. Colonnes: {list(df.columns)}")

            # Conversion des types
            for col in ['UnitPrice', 'Quantity', 'LineAmount']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

            # Conversion date
            if 'DocumentDate' in df.columns:
                df['DocumentDate'] = pd.to_datetime(df['DocumentDate'], format='%d/%m/%Y', errors='coerce')
                df['Month'] = df['DocumentDate'].dt.month
                df['Year'] = df['DocumentDate'].dt.year
                df['Quarter'] = df['DocumentDate'].dt.quarter

            print(f"Lignes chargées: {len(df)}")
        except Exception as e:
            print(f"Erreur lors de la lecture du CSV: {e}")
            df = None
    else:
        print(f"Fichier {csv_filename} non trouvé, utilisation de données synthétiques")

    n_samples = 1000

    if df is not None and len(df) > 0 and 'UnitPrice' in df.columns and 'Quantity' in df.columns:
        if len(df) < n_samples:
            repeat_factor = (n_samples // len(df)) + 1
            df_expanded = pd.concat([df] * repeat_factor, ignore_index=True)[:n_samples]
        else:
            df_expanded = df.sample(n_samples, random_state=42).reset_index(drop=True)

        prices         = df_expanded['UnitPrice'].values
        last_quantities = df_expanded['Quantity'].values
        avg_prices     = df_expanded['UnitPrice'].rolling(window=5, min_periods=1).mean().values

        # ✅ Target réelle au lieu de synthétique
        quantities = df_expanded['Quantity'].values

        extra_features = []
        for col in ['Month', 'Year', 'Quarter']:
            if col in df_expanded.columns:
                extra_features.append(df_expanded[col].fillna(0).values)

    else:
        prices = np.random.uniform(10, 200, n_samples)
        last_quantities = np.random.uniform(0, 300, n_samples)
        avg_prices = np.random.uniform(10, 200, n_samples)
        extra_features = []
        # ✅ Target synthétique uniquement en fallback
        quantities = 200 * np.exp(-0.015 * prices) + 0.3 * last_quantities + np.random.normal(0, 10, n_samples)

    # Target
    quantities = np.maximum(0, quantities)

    # Features finales
    base_features = [prices, last_quantities, avg_prices]
    all_features = base_features + extra_features
    X = np.column_stack(all_features)
    y = quantities

    # Normalisation
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Entraînement
    model = create_model(input_dim=X.shape[1])  # passer la dim en paramètre
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    ]

    history = model.fit(
        X, y,
        epochs=100,          # plus d'epochs, early stopping s'en occupe
        batch_size=32,
        verbose=1,
        validation_split=0.2,
        callbacks=callbacks
    )

    # Courbe
    plt.figure(figsize=(10, 5))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Courbe d\'entraînement')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.tight_layout()
    plt.savefig('courbe_modele.png', dpi=300)
    plt.close()
    print("Courbe sauvegardée.")

    return model, scaler, df


# Charger le modèle au démarrage
print("Entraînement du modèle ML...")
ml_model, scaler, df_global = train_model_with_file(CSVFileName)
print("Modèle prêt!")


# --- Fonction de prédiction avec historique ---
def predict_global_profit(target_year: int, target_month: int = None) -> dict:
    if ml_model is None or df_global is None:
        print("Modèle ou données non chargés.")
        return {}

    start_year  = 2026
    start_month = 4  # Avril 2026

    end_year  = target_year
    end_month = target_month if target_month else 12

    # Générer toutes les périodes entre aujourd'hui et la cible
    periods = []
    for year in range(start_year, end_year + 1):
        m_start = start_month if year == start_year else 1
        m_end   = end_month   if year == end_year   else 12
        for month in range(m_start, m_end + 1):
            periods.append((year, month))

    last_quantities  = df_global.groupby('ItemNo')['Quantity'].last()
    unit_prices      = df_global.groupby('ItemNo')['UnitPrice'].last()
    orders_per_month = (
        df_global.groupby('ItemNo').size() /
        df_global.groupby('ItemNo')['Month'].nunique()
    )
    print(orders_per_month)
    print(orders_per_month.mean())
            

    total_profit = 0
    results = {}

    for year, month in periods:
        quarter = (month - 1) // 3 + 1

        features = np.array([
            [unit_prices[item], last_quantities[item], unit_prices[item], month, year, quarter]
            for item in last_quantities.index
        ])

        if scaler is not None:
            features = scaler.transform(features)

        predicted_quantities = ml_model.predict(features, verbose=0).flatten()
        predicted_quantities = np.maximum(0, predicted_quantities)

        profits = predicted_quantities * orders_per_month.values * unit_prices.values

        for i, item in enumerate(last_quantities.index):
            results[item] = results.get(item, 0) + round(profits[i], 2)
            total_profit += profits[i]

    results['TOTAL'] = round(total_profit, 2)
    return results


@app.post("/predict")
def predict(data: DonneesVentes):
    """Endpoint de prédiction des ventes globales"""
    global ml_model, df_global, scaler

    # ml_model, scaler, dfRes = train_model_with_file()

    results = predict_global_profit(
        target_year  = data.target_year,
        target_month = data.target_month if data.target_month != 0 else None
    )

    return {
        "model": "TensorFlow Neural Network",
        "target_year": data.target_year,
        "target_month": data.target_month if hasattr(data, 'target_month') else "Année complète",
        "profits_par_article": results,
        "profit_total": results.get('TOTAL', 0),
        "nb_articles": len(df_global['ItemNo'].unique()) if df_global is not None else 0,
        "nb_lignes_csv": len(df_global) if df_global is not None else 0,
    }


@app.get("/health")
def health():
    """Endpoint de vérification de santé"""
    return {"status": "ok", "model_loaded": ml_model is not None}


@app.get("/")
def root():
    """Endpoint racine"""
    return {
        "message": "Achat Prediction API",
        "endpoints": {
            "/predict": "POST - Prédire les ventes",
            "/health": "GET - Vérifier l'état du service"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)