import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_URL = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/quantsense"
