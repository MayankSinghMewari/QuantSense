import pickle
import os
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from models.prepare import get_features_and_labels
from config import STOCKS
from logger import logger

def train(ticker):
    logger.info(f"Training XGBoost for {ticker}...")

    X, y = get_features_and_labels(ticker)
    if X is None or len(X) < 100:
        logger.warning(f"Not enough data for {ticker}")
        return None

    # Split — last 20% is test (time-aware, no shuffle)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    # Evaluate
    y_pred    = model.predict(X_test)
    accuracy  = accuracy_score(y_test, y_pred)
    logger.info(f"{ticker} accuracy: {round(accuracy * 100, 2)}%")
    logger.info(f"\n{classification_report(y_test, y_pred, target_names=['HOLD','BUY','SELL'])}")

    # Save model
    os.makedirs("models/saved", exist_ok=True)
    path = f"models/saved/{ticker.replace('.','_').replace('^','')}_xgb.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Model saved: {path}")

    return model, accuracy


def train_all():
    results = {}
    for ticker in STOCKS[:10]:  # start with first 10
        result = train(ticker)
        if result:
            _, accuracy = result
            results[ticker] = round(accuracy * 100, 2)

    logger.info("=== Training Complete ===")
    for ticker, acc in results.items():
        logger.info(f"{ticker}: {acc}%")

    return results


if __name__ == "__main__":
    train_all()