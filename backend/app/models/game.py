from sqlalchemy import Column, Integer, String, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(String)
    genres = Column(ARRAY(String), default=[])
    tags = Column(ARRAY(String), default=[])
    url = Column(String, unique=True)
    description = Column(Text, nullable=True)
