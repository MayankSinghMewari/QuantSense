from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from config import MONGO_URL, DB_NAME, STOCKS
from signals.signal_engine import get_signal, get_all_signals
from logger import logger

app = FastAPI(
    title="QuantSense API",
    description="AI-powered stock signal platform",
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "QuantSense API is running!", "version": "1.0.0"}


@app.get("/price-history/{ticker}")
def get_history(ticker: str, days: int = 90):
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME]["stock_prices"]
        records    = list(collection.find(
            {"ticker": ticker.upper()},
            {"_id": 0, "date": 1, "close": 1, "ma_20": 1, "ma_50": 1,
             "bb_upper": 1, "bb_lower": 1, "volume": 1, "rsi": 1}
        ).sort("date", -1).limit(days))
        client.close()
        records.reverse()
        for r in records:
            if hasattr(r.get('date'), 'strftime'):
                r['date'] = r['date'].strftime('%d %b')
        return {"ticker": ticker, "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signal/{ticker}")
def get_ticker_signal(ticker: str):
    """Get latest signal for a single ticker."""
    signal = get_signal(ticker.upper())
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal not found for {ticker}")
    return signal


@app.get("/signals/all")
def get_all():
    """Get signals for all tracked stocks."""
    signals = get_all_signals(STOCKS[:10])
    return {"count": len(signals), "signals": signals}


@app.get("/signals/top/buy")
def top_buy_signals():
    """Get top BUY signals sorted by confidence."""
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME]["signals"]
        results    = list(collection.find(
            {"signal": "BUY"},
            {"_id": 0}
        ).sort("confidence", -1).limit(10))
        client.close()
        return {"count": len(results), "signals": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/top/sell")
def top_sell_signals():
    """Get top SELL signals sorted by confidence."""
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME]["signals"]
        results    = list(collection.find(
            {"signal": "SELL"},
            {"_id": 0}
        ).sort("confidence", -1).limit(10))
        client.close()
        return {"count": len(results), "signals": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    """Get latest sentiment for a ticker."""
    try:
        client     = MongoClient(MONGO_URL)
        collection = client[DB_NAME]["sentiment_scores"]
        result     = collection.find_one(
            {"ticker": ticker.upper()},
            {"_id": 0},
            sort=[("fetched_at", -1)]
        )
        client.close()
        if not result:
            raise HTTPException(status_code=404, detail="No sentiment data found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

