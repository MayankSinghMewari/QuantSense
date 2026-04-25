import os
from pymongo import MongoClient
from dotenv import load_dotenv
from logger import logger

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")

def save_to_db(all_data):
    try:
        client = MongoClient(MONGO_URL)
        db = client["quantsense"]
        collection = db["stock_prices"]

        for ticker, df in all_data.items():
            df_save = df.reset_index()
            df_save.columns = [c.lower() for c in df_save.columns]
            
            # convert to dict records for MongoDB
            records = df_save.to_dict("records")
            
            collection.insert_many(records)
            logger.info(f"Stored {ticker} — {len(records)} records")

        logger.info("All data saved to MongoDB!")

    except Exception as e:
        logger.error(f"MongoDB error — {e}")