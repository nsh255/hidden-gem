from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from ..database import get_db
from .. import models, schemas
from ..config import settings
from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Usar el mismo contexto de encriptación que en users.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    """Verifica si la contraseña en texto plano coincide con la hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash de la contraseña proporcionada."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT con los datos proporcionados."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión y obtener un token JWT.
    
    - **username**: El email o nick del usuario
    - **password**: La contraseña del usuario
    
    Retorna un token JWT si las credenciales son correctas.
    """
    # Buscar usuario por email o nick
    user = db.query(models.Usuario).filter(
        (models.Usuario.email == form_data.username) | 
        (models.Usuario.nick == form_data.username)
    ).first()
    
    # Verificar usuario y contraseña
    if not user or not verify_password(form_data.password, user.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Devolver token y datos básicos del usuario
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nick": user.nick,
            "email": user.email
        }
    }

@router.post("/login-json")
def login_json(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """
    Endpoint alternativo para iniciar sesión con JSON en lugar de form-data.
    
    - **email**: El email del usuario
    - **password**: La contraseña del usuario
    
    Retorna un token JWT si las credenciales son correctas.
    """
    # Buscar usuario por email o nick
    user = db.query(models.Usuario).filter(
        (models.Usuario.email == credentials.email) | 
        (models.Usuario.nick == credentials.email)
    ).first()
    
    # Verificar usuario y contraseña
    if not user or not verify_password(credentials.password, user.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Devolver token y datos básicos del usuario
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nick": user.nick,
            "email": user.email
        }
    }

@router.post("/register", response_model=schemas.AuthResponse)
def register(
    user_data: schemas.UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario y genera un token JWT.
    
    - **nick**: Nombre de usuario
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    Retorna un token JWT y los datos básicos del usuario registrado.
    """
    # Verificar si el usuario ya existe
    db_user_nick = db.query(models.Usuario).filter(models.Usuario.nick == user_data.nick).first()
    if db_user_nick:
        raise HTTPException(status_code=400, detail="Nick ya registrado")
    
    db_user_email = db.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear nuevo usuario con contraseña encriptada
    hashed_password = get_password_hash(user_data.password)
    db_user = models.Usuario(
        nick=user_data.nick, 
        email=user_data.email, 
        contraseña=hashed_password, 
        precio_max=20.0  # Valor por defecto
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    # Devolver token y datos básicos del usuario
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "nick": db_user.nick,
            "email": db_user.email
        }
    }
