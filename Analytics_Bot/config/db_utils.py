from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT", "5432")
    url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url)