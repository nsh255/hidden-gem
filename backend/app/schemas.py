from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# Esquemas para usuarios
class UsuarioBase(BaseModel):
    nick: str
    email: str
    precio_max: float = 20.0

class UsuarioCreate(UsuarioBase):
    contraseña: str

class Usuario(UsuarioBase):
    id: int
    
    class Config:
        orm_mode = True

# Esquemas para juegos de Steam
class JuegoSteamBase(BaseModel):
    nombre: str
    generos: List[str] 
    precio: float
    descripcion: str
    tags: List[str]
    imagen_principal: str

class JuegoSteamCreate(JuegoSteamBase):
    pass

class JuegoSteam(JuegoSteamBase):
    id: int
    
    class Config:
        orm_mode = True

# Esquemas para juegos favoritos
class JuegoFavoritoBase(BaseModel):
    nombre: str
    imagen: str
    descripcion: str
    generos: List[str]
    tags: List[str]

class JuegoFavoritoCreate(JuegoFavoritoBase):
    pass

class JuegoFavorito(JuegoFavoritoBase):
    id: int
    
    class Config:
        orm_mode = True

# Esquema para añadir favoritos
class FavoritoAdd(BaseModel):
    usuario_id: int
    juego_id: int

# Schema para juegos recomendados
class JuegoRecomendado(BaseModel):
    """
    Información de un juego recomendado con su puntuación de relevancia
    """
    id: int
    nombre: str
    generos: List[str]
    precio: float
    descripcion: str
    imagen_principal: str
    puntuacion: float = Field(..., description="Puntuación de relevancia basada en las preferencias del usuario (mayor = más relevante)")
    
    class Config:
        orm_mode = True

# Esquemas para autenticación
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    nick: str
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    token_type: str
    user: Dict[str, Any]

# Esquemas para cambio de contraseña
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Esquema para reseteo de contraseña
class PasswordReset(BaseModel):
    token: str
    new_password: str

# Esquema para email
class EmailSchema(BaseModel):
    email: EmailStr

# Esquema para actualización de usuario
class UsuarioUpdate(BaseModel):
    nick: Optional[str] = None
    email: Optional[EmailStr] = None
    precio_max: Optional[float] = None

# Esquema para creación de reseña de juego
class GameReviewCreate(BaseModel):
    rating: float
    content: str

# Esquema para reseña de juego
class GameReview(BaseModel):
    id: int
    user_id: int
    user_name: str
    game_id: int
    rating: float
    content: str
    created_at: str

# Esquemas para reseñas de juegos
class ReviewBase(BaseModel):
    """Esquema base para reseñas de juegos"""
    rating: float = Field(..., ge=1.0, le=5.0, description="Puntuación del juego (1-5)")
    content: str = Field(..., min_length=3, max_length=1000, description="Contenido de la reseña")

class ReviewCreate(ReviewBase):
    """Esquema para crear una nueva reseña"""
    pass

class Review(ReviewBase):
    """Esquema para mostrar reseñas"""
    id: int
    user_id: int
    user_name: str
    game_id: int

    created_at: datetime
    class Config:
        from_attributes = True  # antes era orm_mode = True

# Define the structure for game results in paginated response
class GameResult(BaseModel):
    id: int
    name: str
    background_image: Optional[str] = None
    released: Optional[str] = None
    rating: Optional[float] = 0
    genres: List[Dict[str, Any]] = []
    price: Optional[float] = None
    
    class Config:
        from_attributes = True  # This was formerly known as orm_mode in Pydantic v1

# Paginated games response schema
class PaginatedGames(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[GameResult] = []
    
    class Config:
        from_attributes = True
