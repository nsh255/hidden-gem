#!/usr/bin/env python
"""
Script para ejecutar el scraper de Steam enfocado en juegos indie.
Diseñado para correr en Docker.
"""
import os
import sys
import time
import logging
import argparse
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from app.scraper.steam_scraper.spiders.games_spider import GamesSpider

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_spider(max_games=2000):  # Aumentado de 1000 a 2000
    """Ejecuta el spider de Steam enfocado en juegos indie"""
    logger.info(f"Iniciando scraper de juegos indie con límite de {max_games} juegos")
    logger.info(f"Fecha y hora de inicio: {datetime.now()}")
    
    try:
        # Obtener configuración del proyecto
        settings = get_project_settings()
        
        # Configurar parámetros adicionales
        if os.environ.get('DATABASE_URL'):
            logger.info(f"Usando DATABASE_URL del entorno: {os.environ.get('DATABASE_URL')}")
        
        # Ejecutar el crawler
        process = CrawlerProcess(settings)
        process.crawl(GamesSpider, max_games=max_games)
        process.start()
        
        logger.info(f"Scraper de juegos indie completado exitosamente: {datetime.now()}")
        return True
    except Exception as e:
        logger.error(f"Error al ejecutar el scraper: {str(e)}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Ejecutar scraper de juegos indie de Steam')
    parser.add_argument('--max-games', type=int, default=int(os.environ.get('MAX_GAMES', 2000)),  # Aumentado a 2000
                        help='Número máximo de juegos a scrapear')
    parser.add_argument('--now', action='store_true', default=True, 
                        help='Ejecutar inmediatamente (por defecto)')
    
    args = parser.parse_args()
    
    # Siempre ejecutamos inmediatamente ya que la programación se hará con Docker/cron
    logger.info(f"Ejecutando scraper de juegos indie con límite de {args.max_games} juegos")
    run_spider(args.max_games)

if __name__ == "__main__":
    main()
