from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from fastapi import Depends

# Cargar variables de entorno
load_dotenv()

# Leer la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # URL de fallback para desarrollo (no recomendado para producción)
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hiddengem"
    print(f"ADVERTENCIA: Variable DATABASE_URL no encontrada. Usando valor por defecto: {DATABASE_URL}")

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase Base para los modelos
Base = declarative_base()

# Función para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        