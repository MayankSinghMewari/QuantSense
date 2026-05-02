FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install lightweight packages first
RUN pip install --no-cache-dir --timeout 300 \
    yfinance pandas pymongo python-dotenv \
    scikit-learn xgboost fastapi uvicorn \
    requests beautifulsoup4 feedparser \
    numpy matplotlib

# Install heavy packages separately
RUN pip install --no-cache-dir --timeout 600 \
    tensorflow torch transformers

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "api"]