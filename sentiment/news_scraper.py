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
    "RELIANCE.NS"  : "Reliance Industries",
    "ONGC.NS"      : "ONGC",
    "POWERGRID.NS" : "Power Grid",
    "NTPC.NS"      : "NTPC",
    "BPCL.NS"      : "BPCL",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "ITC.NS"       : "ITC",
    "NESTLEIND.NS" : "Nestle India",
    "BRITANNIA.NS" : "Britannia",
    "DABUR.NS"     : "Dabur",
    "MARUTI.NS"    : "Maruti Suzuki",
    "EICHERMOT.NS" : "Eicher Motors",
    "HEROMOTOCO.NS": "Hero MotoCorp",
    "SUNPHARMA.NS" : "Sun Pharma",
    "DRREDDY.NS"   : "Dr Reddys",
    "CIPLA.NS"     : "Cipla",
    "DIVISLAB.NS"  : "Divis Lab",
    "APOLLOHOSP.NS": "Apollo Hospitals",
    "MPHASIS.NS"   : "Mphasis",
    "LTIM.NS"      : "LTIMindtree",
    "PERSISTENT.NS": "Persistent Systems",
    "COFORGE.NS"   : "Coforge",
    "TATAELXSI.NS" : "Tata Elxsi",
    "BAJAJFINSV.NS": "Bajaj Finserv",
    "MUTHOOTFIN.NS": "Muthoot Finance",
    "CHOLAFIN.NS"  : "Chola Finance",
    "MANAPPURAM.NS": "Manappuram",
    "SBILIFE.NS"   : "SBI Life",
    "MOTHERSON.NS" : "Motherson",
    "BALKRISIND.NS": "Balkrishna Industries",
    "BHARATFORG.NS": "Bharat Forge",
    "ESCORTS.NS"   : "Escorts Kubota",
    "TIINDIA.NS"   : "Tube Investments",
    "LT.NS"        : "Larsen Toubro",
    "ADANIPORTS.NS": "Adani Ports",
    "IRCTC.NS"     : "IRCTC",
    "BEL.NS"       : "Bharat Electronics",
    "HAL.NS"       : "HAL",
    "PIDILITIND.NS": "Pidilite",
    "AARTIIND.NS"  : "Aarti Industries",
    "DEEPAKNTR.NS" : "Deepak Nitrite",
    "TATACHEM.NS"  : "Tata Chemicals",
    "GNFC.NS"      : "GNFC",
    "DLF.NS"       : "DLF",
    "GODREJPROP.NS": "Godrej Properties",
    "ULTRACEMCO.NS": "Ultratech Cement",
    "AMBUJACEM.NS" : "Ambuja Cement",
    "SHREECEM.NS"  : "Shree Cement",
    "TRENT.NS"     : "Trent",
    "DMART.NS"     : "DMart",
    "NYKAA.NS"     : "Nykaa",
    "TITAN.NS"     : "Titan",
    "JUBLFOOD.NS"  : "Jubilant FoodWorks",
    "DATAPATTNS.NS": "Data Patterns",
    "COCHINSHIP.NS": "Cochin Shipyard",
    "MAZDOCK.NS"   : "Mazagon Dock",
    "ADANIGREEN.NS": "Adani Green",
    "TATAPOWER.NS" : "Tata Power",
    "CESC.NS"      : "CESC",
    "SJVN.NS"      : "SJVN",
    "NHPC.NS"      : "NHPC",
    "PAYTM.NS"     : "Paytm",
    "POLICYBZR.NS" : "PolicyBazaar",
    "NAUKRI.NS"    : "Info Edge Naukri",
    "INDIAMART.NS" : "IndiaMART",
    "NAVINFLUOR.NS": "Navin Fluorine",
    "FINEORG.NS"   : "Fine Organics",
    "VINATIORGA.NS": "Vinati Organics",
    "SUDARSCHEM.NS": "Sudarshan Chemical",
    "BANKBARODA.NS": "Bank of Baroda",
    "CANBK.NS"     : "Canara Bank",
    "FEDERALBNK.NS": "Federal Bank",
    "AUBANK.NS"    : "AU Small Finance",
    "IDFCFIRSTB.NS": "IDFC First Bank",
    "MAXHEALTH.NS" : "Max Healthcare",
    "FORTIS.NS"    : "Fortis Healthcare",
    "METROPOLIS.NS": "Metropolis",
    "THYROCARE.NS" : "Thyrocare",
    "DELHIVERY.NS" : "Delhivery",
    "BLUEDART.NS"  : "Blue Dart",
    "INDIGO.NS"    : "IndiGo",
    "IRFC.NS"      : "IRFC",
    "HDFCLIFE.NS"  : "HDFC Life",
    "ICICIPRULI.NS": "ICICI Prudential",
    "ICICIGI.NS"   : "ICICI Lombard",
    "LTTS.NS"      : "LTI Technology Services",
}