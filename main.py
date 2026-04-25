from pipeline.fetch import fetch_all
from pipeline.clean import clean_all
from pipeline.store import save_to_db
from logger import logger

def run():
    logger.info("=== QuantSense Pipeline Started ===")

    logger.info("--- Step 1: Fetching Data ---")
    fetch_all()

    logger.info("--- Step 2: Cleaning Data ---")
    all_data = clean_all()

    logger.info("--- Step 3: Saving to Database ---")
    save_to_db(all_data)

    logger.info("=== Pipeline Complete ===")

if __name__ == "__main__":
    run()