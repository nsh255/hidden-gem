from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

# Usuario schemas
class UsuarioBase(BaseModel):
    nick: str
    email: EmailStr
    precio_max: float

class UsuarioCreate(UsuarioBase):
    contraseña: str

class Usuario(UsuarioBase):
    id: int
    
    class Config:
        orm_mode = True

# JuegosScrapeadoDeSteamParaRecomendaiones schemas
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

# JuegosFavoritosDeUsuarioQueProvienenDeRawg schemas
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

# Schema para añadir juego favorito a un usuario
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

class UserLogin(BaseModel):
    email: str
    password: str
