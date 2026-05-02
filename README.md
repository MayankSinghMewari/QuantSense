# QuantSense
An end-to-end AI-powered stock analysis plateform that monitors markets, news and social sentiment in real-time to generate intelligent Buying/ selling/  holding signals across short, min and long term horizons. build on a production grade cloud infrastructure.


<div align="center">

# 🚀 QuantSense
### AI-Powered Stock Market Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.x-green?style=for-the-badge&logo=mongodb)](https://mongodb.com)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge)]()

> An end-to-end cloud-native financial intelligence platform that monitors markets, news and social sentiment in real-time to generate intelligent Buy/Sell/Hold signals across short, mid and long-term horizons.

</div>

---

## 🧠 What is QuantSense?

QuantSense is a full-stack AI trading signal platform built on production-grade cloud infrastructure. It continuously monitors **100+ Indian & US stocks**, processes market data, scrapes financial news and social sentiment, and delivers high-confidence trading signals with risk scores.

---

## ⚙️ Architecture
Data Sources → Pipeline → ML Engine → Signal Generator → FastAPI → React Dashboard
yfinance      Fetch       LSTM         Buy/Sell/Hold     REST      SaaS Product
NSE India     Clean       XGBoost      Confidence %      Auth      Stripe Billing
News/Reddit   Store       FinBERT      Risk Score        Rate      Grafana Monitor
MongoDB     NLP Sentiment                  Limit

---

## 🗺️ Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Data Pipeline & Cloud Infra | ✅ Complete |
| 2 | ML Model Development | ✅ Complete |
| 3 | Sentiment Engine & News Crawler | ✅ Complete |
| 4 | Signal Engine & Trade Logic | ✅ Complete |
| 5 | DevOps, Containers & CI/CD | 🔄 In Progress |
| 6 | Dashboard, API & Product Launch | ⏳ Upcoming |

---

## 🛠️ Tech Stack

### Cloud & DevOps
- **AWS** — EC2, S3, Lambda, EKS, CloudWatch
- **Docker & Kubernetes** — containerisation & orchestration
- **Terraform** — infrastructure as code
- **GitHub Actions** — CI/CD pipeline

### Backend & Data
- **Python 3.12** — core language
- **FastAPI** — REST API backend
- **MongoDB** — stock data storage
- **Pandas** — data processing

### AI & ML
- **LSTM** — price prediction
- **XGBoost** — signal classification
- **FinBERT** — financial sentiment NLP

### Frontend
- **React** — interactive dashboard
- **Recharts** — data visualisation

---

## 📁 Project Structure
quantsense/
├── pipeline/
│   ├── fetch.py        # pull stock data from APIs
│   ├── clean.py        # clean & add indicators
│   └── store.py        # save to MongoDB
├── data/
│   └── raw/            # local CSV storage
├── logs/               # pipeline logs
├── config.py           # stock list & settings
├── logger.py           # logging setup
├── main.py             # pipeline entry point
└── requirements.txt

---

## 🚀 Getting Started

```bash
# clone the repo
git clone https://github.com/MayankSinghMewari/QuantSense.git
cd QuantSense

# install dependencies
pip install -r requirements.txt

# set up environment
cp .env.example .env
# add your credentials to .env

# run the pipeline
python main.py
```

---

## 📊 Stocks Covered

100 Indian stocks across sectors including Banking, IT, Energy, Pharma, Defence, FMCG, Auto, Fintech and more — covering Nifty 50, Midcap and Smallcap segments.

---

## 👨‍💻 Author

**Mayank Singh Mewari**  
Cloud & DevOps Engineer | AI Enthusiast  
[![GitHub](https://img.shields.io/badge/GitHub-MayankSinghMewari-black?style=flat&logo=github)](https://github.com/MayankSinghMewari)

---

<div align="center">
⭐ Star this repo if you find it useful!
</div>

--- 
