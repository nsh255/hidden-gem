from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener SECRET_KEY desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "desarrollosecreto"
    print("ADVERTENCIA: SECRET_KEY no encontrada en .env, usando clave insegura por defecto")

# Configuración para el algoritmo de encriptación
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash seguro para una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un JWT token con los datos proporcionados y una fecha de expiración
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
