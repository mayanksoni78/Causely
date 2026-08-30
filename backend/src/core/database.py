import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')

if database_url:
    # Use production DB URL directly (e.g. Supabase, Neon)
    db_url = database_url
else:
    # Construct local DB URL safely without string concatenation
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = int(os.getenv('POSTGRES_PORT', 5433))
    db_name = os.getenv('POSTGRES_DB', 'Ai_Incident')
    
    db_url = URL.create(
        drivername='postgresql',
        username=user,
        password=password,
        host=host,
        port=port,
        database=db_name
    )

engine = create_engine(
    db_url,
    pool_pre_ping=True,      # Verify connections before usage
    pool_recycle=3600,       # Prevent stale connections
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
