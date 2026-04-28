import pandas as pd
from pymongo import MongoClient
from config import MONGO_URL, DB_NAME, COLLECTION_NAME
from logger import logger

def load_data(ticker):
    """Load stock data from MongoDB for a single ticker."""
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME][COLLECTION_NAME]

        records = list(collection.find(
            {"ticker": ticker},
            {"_id": 0}
        ).sort("date", 1))

        client.close()

        if not records:
            logger.warning(f"No data found for {ticker}")
            return None

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        logger.info(f"Loaded {ticker} — {len(df)} rows")
        return df

    except Exception as e:
        logger.error(f"Failed to load {ticker}: {e}")
        return None


def create_labels(df, horizon=5):
    """
    Create Buy/Sell/Hold labels.
    Look 'horizon' days ahead — if price goes up >1% = BUY,
    down >1% = SELL, else = HOLD.
    """
    df = df.copy()
    future_return = df['close'].pct_change(horizon).shift(-horizon)

    df['label'] = 0  # HOLD
    df.loc[future_return >  0.01, 'label'] = 1  # BUY
    df.loc[future_return < -0.01, 'label'] = 2  # SELL

    return df.dropna()


FEATURES = [
    'open', 'high', 'low', 'close', 'volume',
    'daily_return', 'ma_20', 'ma_50', 'volatility',
    'rsi', 'macd', 'bb_upper', 'bb_lower', 'volume_ma',
    'candle_strength', 'momentum_score', 'gap_score',
    'resistance_distance', 'support_distance', 'qs_score'
]

def get_features_and_labels(ticker):
    """Returns X (features) and y (labels) ready for ML."""
    df = load_data(ticker)
    if df is None:
        return None, None

    df = create_labels(df)

    # Keep only available feature columns
    available = [f for f in FEATURES if f in df.columns]
    X = df[available]
    y = df['label']

    logger.info(f"{ticker} — X: {X.shape} | Labels: {y.value_counts().to_dict()}")
    return X, y