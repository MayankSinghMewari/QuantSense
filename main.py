import time
from pipeline.fetch import fetch_ticker_data
from pipeline.clean import clean_ticker_data
from pipeline.store import save_ticker_to_db
from logger import logger
from config import ALL_TICKERS

def run_pipeline(tickers):
    logger.info(f"=== QuantSense Pipeline Started — {len(tickers)} tickers ===")
    start_time  = time.time()
    success, failed = [], []

    for index, ticker in enumerate(tickers):
        try:
            raw   = fetch_ticker_data(ticker, index)
            clean = clean_ticker_data(ticker, raw)
            if clean is not None:
                save_ticker_to_db(ticker, clean)
                success.append(ticker)
            else:
                failed.append(ticker)
        except Exception as e:
            logger.error(f"Pipeline failed for {ticker}: {e}")
            failed.append(ticker)

    elapsed = round(time.time() - start_time, 2)
    logger.info(f"=== Pipeline Complete in {elapsed}s ===")
    logger.info(f"Success: {len(success)} | Failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed tickers: {failed}")

if __name__ == "__main__":
    try:
        run_pipeline(ALL_TICKERS)
    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user.")