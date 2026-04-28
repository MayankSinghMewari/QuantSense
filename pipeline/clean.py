import pandas as pd
import numpy as np
from logger import logger

def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False).mean()
    loss  = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def clean_ticker_data(ticker, df):
    if df is None or df.empty:
        return None
    try:
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [c.lower() for c in df.columns]
        df = df[['open','high','low','close','volume']].dropna()

        df['ticker']       = ticker
        df['daily_return'] = df['close'].pct_change()
        df['ma_20']        = df['close'].rolling(20).mean()
        df['ma_50']        = df['close'].rolling(50).mean()
        df['volatility']   = df['daily_return'].rolling(20).std()
        df['rsi']          = compute_rsi(df['close'])
        df['macd']         = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()

        std20              = df['close'].rolling(20).std()
        df['bb_upper']     = df['ma_20'] + 2 * std20
        df['bb_lower']     = df['ma_20'] - 2 * std20
        df['volume_ma']    = df['volume'].rolling(20).mean()

        # Custom indicators
        price_range            = (df['high'] - df['low']).replace(0, np.nan)
        df['candle_strength']  = (df['close'] - df['open']) / price_range
        df['momentum_score']   = (
            df['close'].pct_change(5)  * 0.3 +
            df['close'].pct_change(10) * 0.3 +
            df['close'].pct_change(20) * 0.4
        )
        df['gap_score']            = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        df['resistance_distance']  = (df['close'].rolling(20).max() - df['close']) / df['close']
        df['support_distance']     = (df['close'] - df['close'].rolling(20).min()) / df['close']

        # QuantSense Score
        rsi_score     = (100 - df['rsi']).fillna(50) / 100
        mom_score     = df['momentum_score'].clip(-1, 1)
        candle_score  = (df['candle_strength'].fillna(0) + 1) / 2
        support_score = 1 - df['support_distance'].clip(0, 1)
        volume_score  = ((df['close'] - df['open']) / price_range > 0).astype(int)

        df['qs_score'] = (
            rsi_score     * 0.25 +
            mom_score     * 0.25 +
            volume_score  * 0.20 +
            candle_score  * 0.15 +
            support_score * 0.15
        ) * 100

        df = df.dropna()
        logger.info(f"Cleaned {ticker} — {len(df)} rows")
        return df

    except Exception as e:
        logger.error(f"Clean failed {ticker}: {e}")
        return None