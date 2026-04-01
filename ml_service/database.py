import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "abandoned_obj_db")

# Create database if it doesn't exist
try:
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    exists = cur.fetchone()
    if not exists:
        print(f"[DB] Creating database {DB_NAME}...")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"[DB_WARNING] Could not check/create database (Is PostgreSQL running and credentials correct?): {e}")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"[DB_ERROR] Failed to connect to Engine: {e}")
    engine = None
    SessionLocal = None

Base = declarative_base()

class ObjectAlert(Base):
    __tablename__ = "object_alerts"

    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(String(50))
    class_name = Column(String(50))
    state = Column(String(50))
    threat_level = Column(String(50))
    confidence = Column(Float)
    stationary_time = Column(Float)
    location_type = Column(String(50))
    crowd_density = Column(Integer)
    owner_id = Column(String(50), nullable=True)
    object_image_base64 = Column(Text, nullable=True)
    person_image_base64 = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    if engine:
        try:
            Base.metadata.create_all(bind=engine)
            print("[DB] Database tables initialized successfully.")
        except Exception as e:
            print(f"[DB_ERROR] Database table creation failed: {e}")

def get_db_session():
    if SessionLocal:
        return SessionLocal()
    return None
