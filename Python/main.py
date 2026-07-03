from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import numpy as np
import pandas as pd
from typing import List, Dict
import tensorflow as tf
from tensorflow import keras
import os
import matplotlib.pyplot as plt


app = FastAPI()


# --- Modèle de données ---
class SalesData(BaseModel):
    ItemNo: str
    unitPrice: float
    last_quantity: float
    history: List[Dict]
    name: str = ""  # Nom de fichier depuis AL

CSVFileName = "sales_data.csv"

def CSVNameFromRequest(data: SalesData) -> str:
    """Génère le nom du fichier CSV : No_sales_data.csv"""
    if data.name:
        return data.name
    else:
        return CSVFileName


# --- Création et entraînement du modèle ML ---
def create_model():
    """Crée un réseau de neurones simple"""
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(3,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def train_model_with_file(csv_filename: str):
    df = None
    if os.path.exists(csv_filename):
        try:
            # Tenter plusieurs encodages
            for encoding in ['ISO-8859-1', 'utf-8', 'cp1252']:
                try:
                    df = pd.read_csv(csv_filename, encoding=encoding, sep=';')
                    print(f"CSV chargé avec l'encodage {encoding}")
                    break
                except:
                    continue
            
            if df is not None:
                # Nettoyage des colonnes
                df.columns = df.columns.str.strip()
                df.columns = df.columns.str.replace('\ufeff', '')
                print(f"Colonnes détectées: {list(df.columns)}")
                
                # Conversion en float
                if 'unitPrice' in df.columns:
                    df['unitPrice'] = df['unitPrice'].astype(str).str.replace(',', '.').astype(float)
                if 'quantity' in df.columns:
                    df['quantity'] = df['quantity'].astype(str).str.replace(',', '.').astype(float)
                
                print(f"Nombre de lignes dans le CSV: {len(df)}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier CSV: {e}")
            df = None
    else:
        print(f"Fichier {csv_filename} non trouvé, utilisation de données synthétiques")
    
    # Générer X et y
    n_samples = 1000  # Nombre d'échantillons pour l'entraînement
    
    # Utiliser les données réelles si disponibles, sinon générer des données synthétiques
    if df is not None and len(df) > 0 and 'unitPrice' in df.columns and 'quantity' in df.columns:
        # Utiliser les données réelles répétées si nécessaire
        if len(df) < n_samples:
            # Répéter les données pour avoir assez d'échantillons
            repeat_factor = (n_samples // len(df)) + 1
            df_expanded = pd.concat([df] * repeat_factor, ignore_index=True)[:n_samples]
        else:
            df_expanded = df[:n_samples]
        
        prices = df_expanded['unitPrice'].values
        last_quantities = df_expanded['quantity'].values
        
        # Calculer rolling mean
        avg_prices = df_expanded['unitPrice'].rolling(window=min(5, len(df_expanded)), min_periods=1).mean().values

    else:
        # Données synthétiques
        prices = np.random.uniform(10, 200, n_samples)
        last_quantities = np.random.uniform(0, 300, n_samples)
        avg_prices = np.random.uniform(10, 200, n_samples)
    
    # Target synthétique avec relation prix-demande
    quantities = 200 * np.exp(-0.015 * prices) + 0.3 * last_quantities + np.random.normal(0, 10, n_samples)
    quantities = np.maximum(0, quantities)

    # Features
    X = np.column_stack([prices, last_quantities, avg_prices])
    y = quantities

    # Créer et entraîner le modèle
    model = create_model()
    
    # Entraîner avec validation split
    model.fit(X, y, epochs=30, batch_size=32, verbose=0, validation_split=0.2)

    #enregistrer l'image de la courbe du modèle dans un fichier png
    plt.figure()
    history = model.history.history
    plt.plot(history['loss'], label='loss')
    plt.plot(history['val_loss'], label='val_loss')
    plt.savefig('courbe_modele.png', dpi=300)
    


    return model, df


# Charger le modèle au démarrage
print("Entraînement du modèle ML...")
ml_model, dfRes = train_model_with_file(CSVFileName)
print("Modèle prêt!")


# --- Fonction de prédiction avec historique ---
def predict_sales(unitPrice: float, last_quantity: float, history: List[Dict[str, float]] = None) -> float:
    """
    Prédit les ventes avec TensorFlow
    
    Args:
        price: Prix actuel
        last_quantity: Dernière quantité vendue
        history: Historique [{price: float, quantity: float}, ...]
    """
    # Calculer stats depuis l'historique
    if history and len(history) > 0:
        try:
            df = pd.DataFrame(history)
            avg_price = df['unitPprice'].mean() if 'unitPrice' in df.columns else unitPrice
            avg_quantity = df['quantity'].mean() if 'quantity' in df.columns else last_quantity
        except:
            avg_price = unitPrice
            avg_quantity = last_quantity
    else:
        avg_price = unitPrice
        avg_quantity = last_quantity
    
    # Features pour le modèle
    features = np.array([[unitPrice, last_quantity, avg_price]])
    
    # Prédiction
    prediction = ml_model.predict(features, verbose=0)[0][0]
    
    return max(0, round(float(prediction), 2))


@app.post("/predict")
def predict(data: SalesData):
    """Endpoint de prédiction des ventes"""
    global ml_model, dfRes
    
    # Charger le modèle spécifique si un nom est fourni
    csv_filename = CSVNameFromRequest(data)
    if csv_filename != CSVFileName and os.path.exists(csv_filename):
        print(f"Chargement du modèle pour {csv_filename}")
        ml_model, dfRes = train_model_with_file(csv_filename)
    
    prediction = predict_sales(data.unitPrice, data.last_quantity, data.history)
    
    # Informations sur les colonnes du CSV
    csv_info = "No CSV loaded"
    if dfRes is not None:
        csv_info = {
            "columns": list(dfRes.columns),
            "rows": len(dfRes),
            "file": data.name,
            
        }
    
    return {
        "predicted_quantity": prediction,
        "model": "TensorFlow Neural Network",
        "name": data.name if data.name else "unknown",
        "prediction_type": "Prochaine vente ponctuelle (pas global)",
        "historique": len(data.history)
    }


@app.get("/health")
def health():
    """Endpoint de vérification de santé"""
    return {"status": "ok", "model_loaded": ml_model is not None}


@app.get("/")
def root():
    """Endpoint racine"""
    return {
        "message": "Sales Prediction API",
        "endpoints": {
            "/predict": "POST - Prédire les ventes",
            "/health": "GET - Vérifier l'état du service"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)