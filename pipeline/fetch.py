import yfinance as yf
import os
from config import STOCKS, GLOBAL_INDICES, START_DATE, END_DATE
from logger import logger

def fetch_all():
    os.makedirs("data/raw", exist_ok=True)

    all_tickers = STOCKS + GLOBAL_INDICES
    success, failed = [], []

    for ticker in all_tickers:
        logger.info(f"Fetching {ticker}...")
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)

            if df.empty:
                logger.warning(f"No data for {ticker}")
                failed.append(ticker)
                continue

            filename = ticker.replace(".", "_").replace("^", "").replace("=", "")
            df.to_csv(f"data/raw/{filename}.csv")
            logger.info(f"Saved {ticker} — {len(df)} rows")
            success.append(ticker)

        except Exception as e:
            logger.error(f"Failed {ticker} — {e}")
            failed.append(ticker)

    logger.info(f"Fetch complete | Success: {len(success)} | Failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed: {failed}")