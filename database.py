from sqlalchemy import create_engine, Column, BigInteger, String, Numeric, Date, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Database Configuration (via Environment Variables)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', '')
DB_PORT = os.getenv('DB_PORT', '5432')

# SQLAlchemy URL — handle passwordless local connections
if DB_PASS:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(Text)
    value = Column(Numeric(15, 2))
    date = Column(Date)
    authority = Column(Text, index=True)
    company = Column(Text, index=True)
    description = Column(Text)
    url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Note: In a real environment, you might use Alembic for migrations.
# Here we're assuming the scrapper already created the table, but calling this is safe.
Base.metadata.create_all(bind=engine)
