import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables del archivo .env si existe
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración
class Settings:
    PROJECT_NAME: str = "Hidden Gem API"
    PROJECT_VERSION: str = "1.0.0"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "postgres")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "hiddengem")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    RAWG_API_KEY: str = os.getenv("RAWG_API_KEY", "")

settings = Settings()
