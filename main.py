import time
from pipeline.fetch import fetch_ticker_data
from pipeline.clean import clean_ticker_data
from pipeline.store import save_ticker_to_db
from logger import logger
from config import ALL_TICKERS, STOCKS

def run_pipeline():
    logger.info(f"=== QuantSense Pipeline Started — {len(ALL_TICKERS)} tickers ===")
    start_time  = time.time()
    success, failed = [], []

    for index, ticker in enumerate(ALL_TICKERS):
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
    logger.info(f"Pipeline Complete in {elapsed}s | Success: {len(success)} | Failed: {len(failed)}")
    if failed:
        logger.warning(f"Failed: {failed}")


def run_training():
    from models.train_xgboost import train_all as xgb_train_all
    from models.train_lstm    import train_all as lstm_train_all

    logger.info("=== Phase 2: Training Models ===")
    logger.info("--- Training XGBoost ---")
    xgb_train_all()

    logger.info("--- Training LSTM ---")
    lstm_train_all()


def run_backtest():
    from models.backtest import backtest_all
    logger.info("=== Phase 2: Backtesting ===")
    backtest_all()


if __name__ == "__main__":
    import sys

    # Usage:
    # py -3.12 main.py pipeline  → run data pipeline
    # py -3.12 main.py train     → train ML models
    # py -3.12 main.py backtest  → run backtest
    # py -3.12 main.py all       → run everything

    mode = sys.argv[1] if len(sys.argv) > 1 else "pipeline"

    try:
        if mode == "pipeline":
            run_pipeline()
        elif mode == "train":
            run_training()
        elif mode == "backtest":
            run_backtest()
        elif mode == "all":
            run_pipeline()
            run_training()
            run_backtest()
        else:
            logger.error(f"Unknown mode: {mode}. Use: pipeline | train | backtest | all")

    except KeyboardInterrupt:
        logger.info("Stopped by user.")