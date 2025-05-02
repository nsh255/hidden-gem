from app.database import engine, Base
from app.models.game import Game
from app.models.user import User

# Importar todos los modelos aquí

def init_db():
    Base.metadata.create_all(bind=engine)
    