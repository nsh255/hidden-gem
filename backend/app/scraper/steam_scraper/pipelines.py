import json
import os
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func, or_
from app.database import engine
from app.models.game import Game
import logging

logger = logging.getLogger(__name__)

class SteamScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Limpieza básica de datos
        if adapter.get('name'):
            adapter['name'] = adapter['name'].strip()
        
        # Verificación adicional - solo procesar juegos indie
        is_indie = adapter.get('is_indie', False)
        if not is_indie:
            spider.logger.info(f"Pipeline: Saltando juego no indie: {adapter.get('name')}")
            return None
            
        return item

class PostgreSQLPipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.items_processed = 0
        self.items_added = 0
        self.items_updated = 0
        self.errors = 0
    
    def open_spider(self, spider):
        self.session = self.Session()
        logger.info("Pipeline PostgreSQL inicializada")
    
    def close_spider(self, spider):
        try:
            self.session.commit()
            logger.info(f"Commit final realizado para los últimos {self.items_processed % 100} juegos")
            # Eliminar juegos con contenido sexual
            games_with_sexual_content = self.session.query(Game).filter(
                func.array_to_string(Game.tags, ',').ilike('%Contenido sexual%')
            ).all()
            
            if games_with_sexual_content:
                sexual_count = len(games_with_sexual_content)
                logger.info(f"Eliminando {sexual_count} juegos con contenido sexual...")
                
                for game in games_with_sexual_content:
                    self.session.delete(game)
                
                self.session.commit()
                logger.info(f"Se han eliminado {sexual_count} juegos con contenido sexual")
            else:
                logger.info("No se encontraron juegos con contenido sexual para eliminar")
            
            # Obtener y mostrar el número total de juegos en la base de datos
            total_games = self.session.query(func.count(Game.id)).scalar()
            logger.info(f"Total de juegos en la base de datos: {total_games}")
            
            # Cerrar la sesión
            self.session.close()
            
            logger.info(f"Pipeline PostgreSQL finalizada. Estadísticas: "
                      f"Procesados: {self.items_processed}, "
                      f"Añadidos: {self.items_added}, "
                      f"Actualizados: {self.items_updated}, "
                      f"Errores: {self.errors}")
        except Exception as e:
            logger.error(f"Error al finalizar el pipeline: {str(e)}")
            self.session.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Verificación adicional - solo procesar juegos indie
        is_indie = adapter.get('is_indie', False)
        if not is_indie:
            return None
        
        # Verificar si el juego tiene contenido sexual
        tags = adapter.get('tags', [])
        if "Contenido sexual" in tags:
            spider.logger.info(f"Saltando juego con contenido sexual: {adapter.get('name')}")
            return None
        
        self.items_processed += 1
        
        # Mensaje cada 100 juegos procesados
        if self.items_processed % 100 == 0:
            logger.info(f"Procesados {self.items_processed} juegos. "
                        f"Añadidos: {self.items_added}, "
                        f"Actualizados: {self.items_updated}, "
                        f"Errores: {self.errors}")
        
        try:
            # Verifica si el juego ya existe por URL o app_id
            app_id = adapter.get('app_id')
            url = adapter.get('url')
            
            existing_game = None
            if app_id:
                # Primero buscamos por app_id (más preciso)
                existing_game = self.session.query(Game).filter(
                    Game.url.contains(f"/app/{app_id}")
                ).first()
            
            if not existing_game and url:
                # Si no encontramos por app_id, buscamos por URL exacta
                existing_game = self.session.query(Game).filter_by(url=url).first()
            
            if not existing_game and adapter.get('name'):
                # Como último recurso, buscamos por nombre exacto
                existing_game = self.session.query(Game).filter_by(title=adapter.get('name')).first()
            
            # Prepara los datos para el modelo asegurando que is_indie sea True
            game_data = {
                'title': adapter.get('name'),
                'price': adapter.get('price'),
                'genres': adapter.get('genres'),
                'tags': adapter.get('tags'),
                'url': adapter.get('url'),
                'description': adapter.get('description', ''),
                'is_indie': True,  # Forzamos a True ya que solo guardamos juegos indie
                'developers': adapter.get('developers', []),
                'publishers': adapter.get('publishers', []),  # Añadimos publishers
                'app_id': adapter.get('app_id'),
                'source': adapter.get('source', 'steam')
            }
            
            if existing_game:
                # Actualiza el juego existente con los nuevos datos
                for key, value in game_data.items():
                    if value is not None:  # Solo actualiza si hay valor
                        setattr(existing_game, key, value)
                self.items_updated += 1
                logger.debug(f"Actualizado juego existente: {adapter.get('name')}")
            else:
                # Crea un nuevo juego
                game = Game(**game_data)
                self.session.add(game)
                self.items_added += 1
                logger.debug(f"Añadido nuevo juego: {adapter.get('name')}")
                
            # Guardamos cada 100 juegos para evitar transacciones muy largas
            if self.items_processed % 100 == 0:
                self.session.commit()
                logger.info(f"Commit realizado después de {self.items_processed} juegos")
        
        except IntegrityError as e:
            self.session.rollback()
            self.errors += 1
            logger.error(f"Error de integridad al guardar {adapter.get('name')}: {str(e)}")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.errors += 1
            logger.error(f"Error de SQLAlchemy al guardar {adapter.get('name')}: {str(e)}")
        except Exception as e:
            self.session.rollback()
            self.errors += 1
            logger.error(f"Error desconocido al guardar {adapter.get('name')}: {str(e)}")
        
        return item

class JsonPipeline:
    def open_spider(self, spider):
        self.output_path = os.path.join(os.getcwd(), 'scraped_games.json')
        self.file = open(self.output_path, 'w', encoding='utf-8')
        spider.logger.info(f"Guardando resultados en: {self.output_path}")
        self.file.write('[\n')
        self._first_item = True
    
    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
        spider.logger.info(f"Archivo JSON cerrado: {self.output_path}")
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        if self._first_item:
            self._first_item = False
            self.file.write(line)
        else:
            self.file.write(',\n' + line)
        return item
