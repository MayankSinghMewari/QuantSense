import pickle
import numpy as np
import pandas as pd
from models.prepare import get_features_and_labels, load_data, FEATURES
from logger import logger

LABEL_MAP = {0: "HOLD", 1: "BUY", 2: "SELL"}

def load_xgb_model(ticker):
    path = f"models/saved/{ticker.replace('.','_').replace('^','')}_xgb.pkl"
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        logger.error(f"No model found for {ticker} — train first")
        return None


def backtest(ticker, initial_capital=100000):
    """
    Simulate trading using XGBoost signals on historical data.
    Starts with ₹1,00,000 and tracks portfolio value.
    """
    logger.info(f"Backtesting {ticker}...")

    model = load_xgb_model(ticker)
    if model is None:
        return None

    X, y = get_features_and_labels(ticker)
    if X is None:
        return None

    # Use last 20% as backtest window (same as test set)
    split       = int(len(X) * 0.8)
    X_test      = X.iloc[split:]
    df_test     = load_data(ticker).iloc[split + 5:]  # +5 for label horizon

    if len(df_test) != len(X_test):
        df_test = df_test.iloc[:len(X_test)]

    predictions = model.predict(X_test)

    # Simulate trades
    capital      = initial_capital
    position     = 0      # shares held
    buy_price    = 0
    trades       = []
    portfolio    = []

    for i, (pred, idx) in enumerate(zip(predictions, X_test.index)):
        if i >= len(df_test):
            break

        price  = df_test['close'].iloc[i]
        signal = LABEL_MAP[pred]

        if signal == "BUY" and position == 0 and capital > price:
            # Buy as many shares as possible
            shares    = int(capital / price)
            position  = shares
            buy_price = price
            capital  -= shares * price
            trades.append({
                "date": idx, "action": "BUY",
                "price": price, "shares": shares
            })

        elif signal == "SELL" and position > 0:
            # Sell all shares
            capital  += position * price
            profit    = (price - buy_price) * position
            trades.append({
                "date": idx, "action": "SELL",
                "price": price, "shares": position,
                "profit": round(profit, 2)
            })
            position  = 0
            buy_price = 0

        # Track portfolio value
        portfolio_value = capital + (position * price)
        portfolio.append(portfolio_value)

    # Final liquidation
    if position > 0:
        final_price = df_test['close'].iloc[-1]
        capital    += position * final_price

    # Results
    final_value   = capital
    total_return  = round((final_value - initial_capital) / initial_capital * 100, 2)
    total_trades  = len([t for t in trades if t['action'] == 'BUY'])

    # Accuracy — how many BUY trades were profitable
    profitable    = [t for t in trades if t.get('action') == 'SELL' and t.get('profit', 0) > 0]
    win_rate      = round(len(profitable) / max(total_trades, 1) * 100, 2)

    logger.info(f"=== Backtest Results: {ticker} ===")
    logger.info(f"Initial Capital : ₹{initial_capital:,.0f}")
    logger.info(f"Final Value     : ₹{final_value:,.0f}")
    logger.info(f"Total Return    : {total_return}%")
    logger.info(f"Total Trades    : {total_trades}")
    logger.info(f"Win Rate        : {win_rate}%")

    return {
        "ticker"          : ticker,
        "initial_capital" : initial_capital,
        "final_value"     : round(final_value, 2),
        "total_return"    : total_return,
        "total_trades"    : total_trades,
        "win_rate"        : win_rate,
        "trades"          : trades,
        "portfolio"       : portfolio
    }


def backtest_all():
    from config import STOCKS
    results = []
    for ticker in STOCKS[:10]:
        result = backtest(ticker)
        if result:
            results.append({
                "ticker"       : result['ticker'],
                "return_%"     : result['total_return'],
                "win_rate_%"   : result['win_rate'],
                "total_trades" : result['total_trades']
            })

    df = pd.DataFrame(results).sort_values("return_%", ascending=False)
    logger.info(f"\n=== Backtest Summary ===\n{df.to_string()}")
    return df


if __name__ == "__main__":
    backtest_all()