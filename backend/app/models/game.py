from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True)
    app_id = Column(String, unique=True)
    price = Column(Float)
    description = Column(Text)
    is_indie = Column(Boolean, default=True)
    source = Column(String, default="steam")
    
    # Estas pueden ser columnas de tipo lista o JSON dependiendo de tu configuración
    genres = Column(ARRAY(String), default=[])
    tags = Column(ARRAY(String), default=[])
    developers = Column(ARRAY(String), default=[])
    publishers = Column(ARRAY(String), default=[])  # Nuevo campo añadido
    
    # Relaciones con otras tablas podrían ir aquí
    favorited_by = relationship(
        "User",
        secondary="user_favorite_games",
        back_populates="favorite_games"
    )
