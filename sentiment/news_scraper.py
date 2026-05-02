import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from logger import logger

# Free RSS feeds — no API key needed
RSS_FEEDS = {
    "moneycontrol"   : "https://www.moneycontrol.com/rss/business.xml",
    "economic_times" : "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "economic_times2": "https://economictimes.indiatimes.com/rssfeeds/1358550121.cms",
    "livemint"       : "https://www.livemint.com/rss/markets",
    "business_std"   : "https://www.business-standard.com/rss/markets-106.rss",
    "ndtv_profit"    : "https://feeds.feedburner.com/ndtvprofit-latest",
    "hindu_business"  : "https://www.thehindubusinessline.com/markets/stock-markets/?service=rss",
    "financial_exp"   : "https://www.financialexpress.com/market/feed/",
    "zee_business"    : "https://www.zeebiz.com/rss/markets.xml",
    "cnbc_tv18"       : "https://www.cnbctv18.com/commonfeeds/v1/eng/rss/market.xml",
    "investing_india" : "https://in.investing.com/rss/news.rss",
    "reuters_business": "https://feeds.reuters.com/reuters/businessNews",
    "bloomberg_india" : "https://feeds.bloomberg.com/markets/news.rss",
    "yahoo_finance"   : "https://finance.yahoo.com/news/rssindex",
    "seeking_alpha"   : "https://seekingalpha.com/feed.xml",
    "market_watch"    : "https://feeds.marketwatch.com/marketwatch/topstories/",
}

def fetch_rss_news(ticker_name, days_back=7):
    """
    Fetch news headlines from RSS feeds related to a stock.
    ticker_name: company name e.g. 'HDFC Bank', 'Infosys'
    """
    all_articles = []
    cutoff_date  = datetime.now() - timedelta(days=days_back)

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title   = entry.get("title", "")
                summary = entry.get("summary", "")
                text    = f"{title} {summary}".lower()

                # Only keep articles mentioning the stock
                # Split into keywords and check any match
                keywords = [w.lower() for w in ticker_name.split() if len(w) > 2]
                if any(k in text for k in keywords):
                    all_articles.append({
                        "ticker"    : ticker_name,
                        "source"    : source,
                        "title"     : title,
                        "summary"   : summary[:500],
                        "fetched_at": datetime.now()
                    })

        except Exception as e:
            logger.error(f"RSS fetch error ({source}): {e}")

    logger.info(f"Found {len(all_articles)} articles for {ticker_name}")
    return all_articles


# Mapping ticker symbols to company names for search
TICKER_TO_NAME = {
    "HDFCBANK.NS"  : "HDFC Bank",
    "ICICIBANK.NS" : "ICICI Bank",
    "SBIN.NS"      : "SBI",
    "KOTAKBANK.NS" : "Kotak Bank",
    "AXISBANK.NS"  : "Axis Bank",
    "TCS.NS"       : "TCS",
    "INFY.NS"      : "Infosys",
    "WIPRO.NS"     : "Wipro",
    "HCLTECH.NS"   : "HCL Tech",
    "TECHM.NS"     : "Tech Mahindra",
    "RELIANCE.NS"  : "Reliance",
    "TATAMOTORS.NS": "Tata Motors",
    "MARUTI.NS"    : "Maruti",
    "SUNPHARMA.NS" : "Sun Pharma",
    "DRREDDY.NS"   : "Dr Reddy",
    "ZOMATO.NS"    : "Zomato",
    "PAYTM.NS"     : "Paytm",
    "ADANIPORTS.NS": "Adani Ports",
    "LT.NS"        : "Larsen Toubro",
    "BAJFINANCE.NS": "Bajaj Finance",
}