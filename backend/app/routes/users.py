from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from ..config import settings

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Configuración JWT (importada desde auth.py)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user_nick = db.query(models.Usuario).filter(models.Usuario.nick == user.nick).first()
    if db_user_nick:
        raise HTTPException(status_code=400, detail="Nick ya registrado")
    
    db_user_email = db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear nuevo usuario con contraseña encriptada
    hashed_password = get_password_hash(user.contraseña)
    db_user = models.Usuario(
        nick=user.nick, 
        email=user.email, 
        contraseña=hashed_password, 
        precio_max=user.precio_max
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.Usuario])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.Usuario).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.Usuario)
def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtiene los datos del usuario autenticado actualmente.
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
        
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.patch("/me", response_model=schemas.Usuario)
def update_current_user(
    user_data: schemas.UsuarioUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos del usuario autenticado actualmente.
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
        
        # Actualizar campos editables
        user_data_dict = user_data.dict(exclude_unset=True)
        for key, value in user_data_dict.items():
            if key != "contraseña":  # Excluir contraseña
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.get("/{user_id}", response_model=schemas.Usuario)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/{user_id}", response_model=schemas.Usuario)
def update_user(user_id: int, user_data: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    """
    Actualiza los datos de un usuario por su ID.
    No requiere contraseña para actualizaciones simples de perfil.
    """
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar solo los campos proporcionados
    user_data_dict = user_data.dict(exclude_unset=True)
    for key, value in user_data_dict.items():
        if key != "contraseña":  # No actualizamos la contraseña por este método
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    return None
