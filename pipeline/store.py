import os
from pymongo import MongoClient, UpdateOne
from config import MONGO_URL, DB_NAME, COLLECTION_NAME
from logger import logger

def save_ticker_to_db(ticker, df):
    if df is None or df.empty:
        return
    try:
        client    = MongoClient(MONGO_URL)
        collection = client[DB_NAME][COLLECTION_NAME]

        collection.create_index([("ticker", 1), ("date", 1)], unique=True)

        df_save         = df.reset_index()
        df_save.columns = [c.lower().replace(" ", "_") for c in df_save.columns]
        df_save["ticker"] = ticker

        ops = [
            UpdateOne(
                {"ticker": r["ticker"], "date": r["date"]},
                {"$set": r},
                upsert=True
            ) for r in df_save.to_dict("records")
        ]

        if ops:
            result = collection.bulk_write(ops)
            logger.info(f"Stored {ticker}: {result.upserted_count} new, {result.modified_count} updated.")

        client.close()
    except Exception as e:
        logger.error(f"Storage error {ticker}: {e}")