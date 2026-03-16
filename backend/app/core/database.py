import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Check if we're running on Cloud Run (has INSTANCE_CONNECTION_NAME)
# or locally (uses DATABASE_URL directly)
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

if INSTANCE_CONNECTION_NAME:
    # Running on Cloud Run — use Cloud SQL Connector
    from google.cloud.sql.connector import Connector

    connector = Connector()

    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            db=os.getenv("DB_NAME", "support_ai"),
        )

    engine = create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )

else:
    # Running locally — use DATABASE_URL from .env
    from app.core.config import DATABASE_URL
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()