from pymongo import MongoClient, UpdateOne
from datetime import datetime
from config import MONGO_URL, DB_NAME
from sentiment.news_scraper import fetch_rss_news, TICKER_TO_NAME
from sentiment.sentiment_scorer import score_articles, get_aggregate_sentiment
from logger import logger


def run_sentiment_pipeline(tickers=None):
    """
    Full pipeline: fetch news → score sentiment → store in MongoDB
    """
    client     = MongoClient(MONGO_URL)
    db         = client[DB_NAME]
    collection = db["sentiment_scores"]

    # Create index
    collection.create_index([("ticker", 1), ("fetched_at", -1)])

    if tickers is None:
        tickers = list(TICKER_TO_NAME.keys())

    logger.info(f"=== Sentiment Pipeline Started — {len(tickers)} tickers ===")

    for ticker in tickers:
        company_name = TICKER_TO_NAME.get(ticker)
        if not company_name:
            logger.warning(f"No company name mapping for {ticker}")
            continue

        try:
            # 1. Fetch news
            articles = fetch_rss_news(company_name, days_back=7)

            if not articles:
                logger.warning(f"No news found for {ticker}")
                # Store neutral score so pipeline doesn't break
                collection.insert_one({
                    "ticker"             : ticker,
                    "company"            : company_name,
                    "aggregate_sentiment": 0.0,
                    "article_count"      : 0,
                    "fetched_at"         : datetime.now()
                })
                continue

            # 2. Score sentiment
            scored_articles = score_articles(articles)
            aggregate       = get_aggregate_sentiment(articles)

            # 3. Store aggregate score
            collection.insert_one({
                "ticker"             : ticker,
                "company"            : company_name,
                "aggregate_sentiment": aggregate,
                "article_count"      : len(scored_articles),
                "articles"           : scored_articles[:5],  # store top 5
                "fetched_at"         : datetime.now()
            })

            logger.info(f"{ticker} sentiment: {aggregate} ({len(scored_articles)} articles)")

        except Exception as e:
            logger.error(f"Sentiment pipeline failed for {ticker}: {e}")

    client.close()
    logger.info("=== Sentiment Pipeline Complete ===")


def get_latest_sentiment(ticker):
    """
    Get the most recent sentiment score for a ticker.
    Used by signal engine in Phase 4.
    """
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME]["sentiment_scores"]
        result     = collection.find_one(
            {"ticker": ticker},
            sort=[("fetched_at", -1)]
        )
        client.close()
        return result["aggregate_sentiment"] if result else 0.0
    except Exception:
        return 0.0