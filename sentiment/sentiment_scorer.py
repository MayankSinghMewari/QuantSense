from transformers import pipeline
from logger import logger

# Load FinBERT — finance specific sentiment model
# Downloads automatically first time (~500MB)
_sentiment_pipeline = None

def get_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info("Loading FinBERT model (first time may take 2-3 mins)...")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            max_length=512,
            truncation=True
        )
        logger.info("FinBERT loaded!")
    return _sentiment_pipeline


def score_text(text):
    """
    Score a single text.
    Returns: {"label": "positive/negative/neutral", "score": 0.95}
    """
    try:
        pipe   = get_pipeline()
        result = pipe(text[:512])[0]
        return {
            "label": result["label"],
            "score": round(result["score"], 4)
        }
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        return {"label": "neutral", "score": 0.5}


def score_articles(articles):
    """
    Score a list of articles and add sentiment fields.
    """
    scored = []
    for article in articles:
        text  = f"{article.get('title','')} {article.get('summary','')}"
        sentiment = score_text(text)

        article["sentiment_label"] = sentiment["label"]
        article["sentiment_score"] = sentiment["score"]

        # Convert to numeric: positive=1, neutral=0, negative=-1
        label_map = {"positive": 1, "neutral": 0, "negative": -1}
        article["sentiment_numeric"] = label_map.get(sentiment["label"], 0)

        scored.append(article)

    return scored


def get_aggregate_sentiment(articles):
    """
    Get overall sentiment score for a stock from multiple articles.
    Returns a single score between -1 and 1.
    """
    if not articles:
        return 0.0

    scored = score_articles(articles)
    total  = sum(a["sentiment_numeric"] for a in scored)
    return round(total / len(scored), 4)