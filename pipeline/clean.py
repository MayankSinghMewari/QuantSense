import pandas as pd
import os
from config import STOCKS, GLOBAL_INDICES
from logger import logger

def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = -delta.where(delta < 0, 0).rolling(period).mean()
    rs    = gain / loss
    return 100 - (100 / (1 + rs))

def clean(ticker):
    filename = ticker.replace(".", "_").replace("^", "").replace("=", "")
    path = f"data/raw/{filename}.csv"

    if not os.path.exists(path):
        logger.warning(f"File missing: {path}")
        return None

    try:
        df = pd.read_csv(path, header=[0,1], index_col=0)
        df.columns = [col[0].lower() for col in df.columns]
        df.index = pd.to_datetime(df.index)
        df = df[['open','high','low','close','volume']].dropna()

        # basic
        df['ticker']       = ticker
        df['daily_return'] = df['close'].pct_change()

        # moving averages
        df['ma_20']        = df['close'].rolling(20).mean()
        df['ma_50']        = df['close'].rolling(50).mean()

        # volatility
        df['volatility']   = df['daily_return'].rolling(20).std()

        # RSI
        df['rsi']          = compute_rsi(df['close'])

        # MACD
        df['macd']         = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()

        # Bollinger Bands
        df['bb_upper']     = df['ma_20'] + 2 * df['close'].rolling(20).std()
        df['bb_lower']     = df['ma_20'] - 2 * df['close'].rolling(20).std()

        # Volume trend
        df['volume_ma']    = df['volume'].rolling(20).mean()

        df = df.dropna()
        logger.info(f"Cleaned {ticker} — {len(df)} rows")
        return df

    except Exception as e:
        logger.error(f"Failed cleaning {ticker} — {e}")
        return None


def clean_all():
    all_data = {}
    all_tickers = STOCKS + GLOBAL_INDICES

    for ticker in all_tickers:
        df = clean(ticker)
        if df is not None:
            all_data[ticker] = df

    logger.info(f"Clean complete | {len(all_data)} tickers ready")
    return all_data