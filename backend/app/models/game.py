from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    genres = Column(Text)  # Géneros como texto separado por comas
    tags = Column(Text)    # Tags como texto separado por comas
    url = Column(String, unique=True)
    description = Column(Text, nullable=True)
    is_indie = Column(Boolean, default=True)
    source = Column(String)  # "rawg" o "steam"
    
    # Relación bidireccional con User
    favorited_by = relationship(
        "User",
        secondary="user_favorite_games",
        back_populates="favorite_games"
    )
