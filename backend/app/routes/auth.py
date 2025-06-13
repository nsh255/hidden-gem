from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
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
    
    Este endpoint acepta credenciales en formato de formulario (username y password)
    y devuelve un token JWT si las credenciales son correctas. El username puede ser
    tanto el email como el nick del usuario.
    
    Args:
        form_data: Formulario con username y password
        db: Sesión de base de datos
        
    Returns:
        Diccionario con token JWT, tipo de token y datos básicos del usuario
        
    Raises:
        HTTPException 401: Si las credenciales son incorrectas
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

@router.post("/verify-token", response_model=dict)
def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))):
    """
    Verifica si un token JWT es válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True}
    except:
        return {"valid": False}

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    data: schemas.PasswordChange,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login")),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario autenticado.
    """
    try:
        # Decodificar el token para obtener el ID del usuario
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Obtener usuario
        user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar la contraseña actual
        if not verify_password(data.current_password, user.contraseña):
            raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
        
        # Cambiar la contraseña
        user.contraseña = get_password_hash(data.new_password)
        db.commit()
        
        return {"message": "Contraseña actualizada con éxito"}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(data: schemas.EmailSchema, db: Session = Depends(get_db)):
    """
    Solicita un restablecimiento de contraseña enviando un email con un token.
    En una implementación real, se enviaría un email con un token.
    """
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.email == data.email).first()
    if not user:
        # Por seguridad, no revelar si el email existe o no
        return {"message": "Si el email existe, se ha enviado un enlace para restablecer la contraseña"}
    
    # En una implementación real, aquí se generaría un token único
    # y se enviaría un email al usuario con un enlace para restablecer la contraseña
    
    # Para simular el proceso, simplemente devolvemos un mensaje de éxito
    return {"message": "Si el email existe, se ha enviado un enlace para restablecer la contraseña"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: schemas.PasswordReset, db: Session = Depends(get_db)):
    """
    Restablece la contraseña utilizando un token de restablecimiento.
    En una implementación real, se verificaría el token.
    """
    # En una implementación real, aquí se verificaría el token
    # y se identificaría al usuario asociado
    
    # Para simular, simplemente devolvemos un mensaje de éxito
    return {"message": "Contraseña restablecida con éxito"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """
    Cierra la sesión del usuario.
    En un sistema real con tokens persistentes, se invalidaría el token.
    Como JWT es stateless, este endpoint es más simbólico.
    """
    # En una implementación con lista negra de tokens,
    # aquí se añadiría el token a una lista negra
    
    return {"message": "Sesión cerrada con éxito"}

@router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))):
    """
    Refresca un token JWT, extendiendo su tiempo de validez.
    """
    try:
        # Decodificar el token actual
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Eliminar la fecha de expiración del payload
        exp = payload.pop("exp", None)
        
        # Crear un nuevo token con los mismos datos pero nueva expiración
        new_token = create_access_token(data=payload)
        
        return {"token": new_token}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/check-email", status_code=status.HTTP_200_OK)
def check_email(email: str, db: Session = Depends(get_db)):
    """
    Verifica si un email ya está registrado.
    """
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    return {"exists": user is not None}
