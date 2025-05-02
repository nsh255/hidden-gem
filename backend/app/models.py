from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from .database import Base

# Tabla de relación entre Usuario y JuegosFavoritos
usuario_juegos_favoritos = Table(
    'usuario_juegos_favoritos',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id')),
    Column('juego_favorito_id', Integer, ForeignKey('juegos_favoritos.id'))
)

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nick = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    contraseña = Column(String)
    precio_max = Column(Float)
    
    # Relación con juegos favoritos
    juegos_favoritos = relationship("JuegosFavoritosDeUsuarioQueProvienenDeRawg", 
                                   secondary=usuario_juegos_favoritos,
                                   back_populates="usuarios")

class JuegosScrapeadoDeSteamParaRecomendaiones(Base):
    __tablename__ = "juegos_steam"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    generos = Column(ARRAY(String))
    precio = Column(Float)
    descripcion = Column(Text)
    tags = Column(ARRAY(String))
    imagen_principal = Column(String)

class JuegosFavoritosDeUsuarioQueProvienenDeRawg(Base):
    __tablename__ = "juegos_favoritos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    imagen = Column(String)
    descripcion = Column(Text)
    generos = Column(ARRAY(String))
    tags = Column(ARRAY(String))
    
    # Relación con usuarios
    usuarios = relationship("Usuario", 
                           secondary=usuario_juegos_favoritos,
                           back_populates="juegos_favoritos")
