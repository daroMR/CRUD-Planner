import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import absoluto (funciona en Docker con PYTHONPATH=/app)
from models import Base

# Leer la URL de la base de datos desde la variable de entorno DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

# Si es SQLite, agregar connect_args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
