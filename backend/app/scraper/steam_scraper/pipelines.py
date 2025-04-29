import json
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.game import Game

class SteamScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Limpieza básica de datos
        if adapter.get('name'):
            adapter['name'] = adapter['name'].strip()
            
        return item

class PostgreSQLPipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        session = self.Session()
        
        try:
            # Verifica si el juego ya existe
            existing_game = session.query(Game).filter_by(url=adapter.get('url')).first()
            
            if existing_game:
                # Actualiza el juego existente
                existing_game.name = adapter.get('name')
                existing_game.price = adapter.get('price')
                existing_game.genres = adapter.get('genres')
                existing_game.tags = adapter.get('tags')
            else:
                # Crea un nuevo juego
                game = Game(
                    name=adapter.get('name'),
                    price=adapter.get('price'),
                    genres=adapter.get('genres'),
                    tags=adapter.get('tags'),
                    url=adapter.get('url')
                )
                session.add(game)
                
            session.commit()
        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error al guardar en la base de datos: {e}")
        finally:
            session.close()
            
        return item

class JsonPipeline:
    def open_spider(self, spider):
        self.file = open('indie_games.json', 'w')
        self.file.write('[\n')
        self._first_item = True
    
    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item))
        if self._first_item:
            self._first_item = False
            self.file.write(line)
        else:
            self.file.write(',\n' + line)
        return item
