import yfinance as yf
import time
import random
from pymongo import MongoClient
from config import MONGO_URL, DB_NAME, COLLECTION_NAME, START_DATE
from logger import logger

def get_last_date(ticker):
    try:
        client = MongoClient(MONGO_URL)
        last = client[DB_NAME][COLLECTION_NAME].find_one(
            {"ticker": ticker}, sort=[("date", -1)]
        )
        client.close()
        return last["date"] if last else START_DATE
    except Exception:
        return START_DATE

def fetch_ticker_data(ticker, index):
    start_date = get_last_date(ticker)
    try:
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty:
            logger.warning(f"No data for {ticker}")
            return None
        logger.info(f"Fetched {ticker} — {len(df)} rows")

        # Rate limiting
        if (index + 1) % 10 == 0:
            logger.info("Cooling down 10s...")
            time.sleep(10)
        else:
            time.sleep(random.uniform(0.5, 1.5))

        return df
    except Exception as e:
        logger.error(f"Failed {ticker}: {e}")
        return None