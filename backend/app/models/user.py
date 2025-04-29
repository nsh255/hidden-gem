from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Tabla de asociación para la relación many-to-many entre User y Game
user_favorite_games = Table(
    'user_favorite_games',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('game_id', Integer, ForeignKey('games.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    nickname = Column(String)
    profile_pic = Column(String, nullable=True)
    max_price = Column(Float)
    
    # Relación many-to-many con Game
    favorite_games = relationship(
        "Game",
        secondary=user_favorite_games,
        back_populates="favorited_by"
    )
