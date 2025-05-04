import os
from pydantic_settings import BaseSettings  # Importar desde pydantic_settings en lugar de pydantic
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables del archivo .env si existe
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración
class Settings(BaseSettings):
    PROJECT_NAME: str = "Hidden Gem API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Credenciales de la base de datos
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "hiddengem")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Clave secreta para JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "un_secreto_muy_seguro_y_largo_para_firmar_tokens_jwt")
    
    # API key para RAWG
    RAWG_API_KEY: str = os.getenv("RAWG_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
