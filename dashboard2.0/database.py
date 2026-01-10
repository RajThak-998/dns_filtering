from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = DATABASE_URL = "postgresql+psycopg://dns_user:dns_pass@localhost:5432/dns_filtering"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)