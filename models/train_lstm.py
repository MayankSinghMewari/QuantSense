import numpy as np
import os
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from models.prepare import load_data
from config import STOCKS
from logger import logger

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

SEQUENCE_LENGTH = 30  # use last 30 days to predict next day

FEATURES = [
    'close', 'volume', 'rsi', 'macd',
    'ma_20', 'ma_50', 'momentum_score', 'qs_score'
]

def create_sequences(data, seq_length):
    """Convert flat data into sequences for LSTM."""
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i])
        y.append(data[i, 0])  # predict 'close' price
    return np.array(X), np.array(y)


def train(ticker):
    logger.info(f"Training LSTM for {ticker}...")

    df = load_data(ticker)
    if df is None or len(df) < 200:
        logger.warning(f"Not enough data for {ticker}")
        return None

    # Use only selected features
    available = [f for f in FEATURES if f in df.columns]
    data = df[available].values

    # Scale to 0-1 range
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Create sequences
    X, y = create_sequences(data_scaled, SEQUENCE_LENGTH)

    # Split — 80% train, 20% test (no shuffle)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build LSTM model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )

    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=0
    )

    # Evaluate
    y_pred = model.predict(X_test, verbose=0)
    mae    = mean_absolute_error(y_test, y_pred)
    logger.info(f"{ticker} LSTM MAE: {round(mae, 4)}")

    # Save model + scaler
    os.makedirs("models/saved", exist_ok=True)
    model.save(f"models/saved/{ticker.replace('.','_').replace('^','')}_lstm.keras")

    scaler_path = f"models/saved/{ticker.replace('.','_').replace('^','')}_scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    logger.info(f"LSTM model saved for {ticker}")
    return model, scaler, mae


def train_all():
    results = {}
    for ticker in STOCKS[:5]:  # start with 5 — LSTM is slower
        result = train(ticker)
        if result:
            _, _, mae = result
            results[ticker] = round(mae, 4)

    logger.info("=== LSTM Training Complete ===")
    for ticker, mae in results.items():
        logger.info(f"{ticker} MAE: {mae}")

    return results


if __name__ == "__main__":
    train_all()