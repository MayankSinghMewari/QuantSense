import pickle
import numpy as np
import pandas as pd
from pymongo import MongoClient
from config import MONGO_URL, DB_NAME
from models.prepare import get_features_and_labels, load_data, FEATURES
from sentiment.sentiment_pipeline import get_latest_sentiment
from logger import logger

LABEL_MAP = {0: "HOLD", 1: "BUY", 2: "SELL"}

def load_xgb_model(ticker):
    path = f"models/saved/{ticker.replace('.','_').replace('^','')}_xgb.pkl"
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        logger.warning(f"No XGBoost model for {ticker}")
        return None


def get_signal(ticker):
    """
    Combines XGBoost prediction + QuantSense Score + Sentiment
    into a final signal with confidence score.
    """
    try:
        # 1. Load latest data
        df = load_data(ticker)
        if df is None or len(df) < 60:
            logger.warning(f"Not enough data for {ticker}")
            return None

        # 2. Get latest row features
        available = [f for f in FEATURES if f in df.columns]
        latest    = df[available].iloc[-1:]

        # 3. XGBoost prediction
        model = load_xgb_model(ticker)
        if model:
            xgb_pred  = model.predict(latest)[0]
            xgb_proba = model.predict_proba(latest)[0]
            xgb_label = LABEL_MAP[xgb_pred]
            xgb_conf  = round(float(max(xgb_proba)) * 100, 2)
        else:
            xgb_label = "HOLD"
            xgb_conf  = 50.0

        # 4. QuantSense Score from latest data
        qs_score = float(df['qs_score'].iloc[-1]) if 'qs_score' in df.columns else 50.0

        # 5. Sentiment score
        sentiment = get_latest_sentiment(ticker)

        # 6. Combine into final signal
        # XGBoost gets 50% weight, QS Score 30%, Sentiment 20%
        xgb_numeric   = {"BUY": 1, "HOLD": 0, "SELL": -1}[xgb_label]
        qs_numeric    = (qs_score - 50) / 50   # normalise to -1 to 1
        combined      = (xgb_numeric * 0.50) + (qs_numeric * 0.30) + (sentiment * 0.20)

        # Convert combined score to signal
        if combined > 0.2:
            final_signal = "BUY"
        elif combined < -0.2:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        # Confidence = how strong the combined score is
        confidence = round(min(abs(combined) * 100, 100), 2)

        # Risk level based on volatility
        volatility = float(df['volatility'].iloc[-1]) if 'volatility' in df.columns else 0
        if volatility > 0.03:
            risk = "HIGH"
        elif volatility > 0.015:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        result = {
            "ticker"        : ticker,
            "signal"        : final_signal,
            "confidence"    : confidence,
            "risk"          : risk,
            "xgb_signal"    : xgb_label,
            "xgb_confidence": xgb_conf,
            "qs_score"      : round(qs_score, 2),
            "sentiment"     : sentiment,
            "combined_score": round(combined, 4),
            "latest_close"  : round(float(df['close'].iloc[-1]), 2),
            "rsi"           : round(float(df['rsi'].iloc[-1]), 2),
            "ma_20"         : round(float(df['ma_20'].iloc[-1]), 2),
        }

        logger.info(
            f"{ticker} | {final_signal} | "
            f"Conf: {confidence}% | Risk: {risk} | "
            f"Sentiment: {sentiment}"
        )
        return result

    except Exception as e:
        logger.error(f"Signal error for {ticker}: {e}")
        return None


def get_all_signals(tickers):
    """Generate signals for all tickers and save to MongoDB."""
    client     = MongoClient(MONGO_URL)
    collection = client[DB_NAME]["signals"]
    collection.create_index([("ticker", 1), ("generated_at", -1)])

    results = []
    for ticker in tickers:
        signal = get_signal(ticker)
        if signal:
            signal["generated_at"] = pd.Timestamp.now()
            collection.insert_one(signal)
            results.append(signal)

    client.close()
    logger.info(f"Generated {len(results)} signals")
    return results