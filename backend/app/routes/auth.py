from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.models.user import User
from app.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta

router = APIRouter()

# Esquema OAuth2 para autenticación con token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema
    """
    # Verificar si el email ya existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
        
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        nickname=user.nickname,
        max_price=user.max_price
    )
    
    # Guardar en base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login")
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve un token JWT
    """
    # Buscar usuario por email
    user = db.query(User).filter(User.email == form_data.email).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token de acceso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "nickname": user.nickname, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "nickname": user.nickname
    }
