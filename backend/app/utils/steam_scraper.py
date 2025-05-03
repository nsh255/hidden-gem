import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class SteamScraper:
    """Clase para scrapear juegos indies de Steam directamente de la página web"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://store.steampowered.com/",
            "Connection": "keep-alive"
        })
        # Configurar la base de URLs más actualizada
        self.base_url = "https://store.steampowered.com"
        # Tags a incluir (siempre debe tener Indie)
        self.include_tags = ["Indie"]
        # Tags a excluir
        self.exclude_tags = ["Sexual Content", "Nudity", "NSFW", "Adult", "Mature"]
        
        # Inicializar cookie para simular una sesión normal de navegador
        self._init_session()
    
    def _init_session(self):
        """Inicializa la sesión con cookies necesarias para navegar por Steam"""
        try:
            # Visitar la página principal para obtener cookies
            self.session.get(self.base_url)
            
            # Configurar cookies básicas que Steam suele esperar
            self.session.cookies.update({
                'birthtime': '786240001',  # Fecha de nacimiento para contenido maduro
                'mature_content': '1',      # Aceptar contenido maduro
                'lastagecheckage': '1-1-1995', # Fecha verificación edad
            })
            
            logger.info("Sesión inicializada con cookies básicas")
            
        except Exception as e:
            logger.error(f"Error inicializando la sesión: {str(e)}")
    
    def get_games_from_browse_page(self, tag="indie", page=1) -> List[Dict[str, Any]]:
        """
        Obtiene lista de juegos desde la página de navegación de Steam
        
        Args:
            tag: Tag principal a buscar (por defecto: indie)
            page: Número de página a scrapear
            
        Returns:
            Lista de diccionarios con información básica de juegos
        """
        games_list = []
        
        try:
            # Construcción de URL actualizada según la estructura actual de Steam
            url = f"{self.base_url}/search/"
            
            params = {
                "term": tag,
                "category1": 998,  # Código para juegos
                "page": page,
                "ignore_preferences": 1
            }
            
            # Añadir retraso aleatorio para parecer tráfico humano
            time.sleep(random.uniform(2.0, 4.0))
            
            logger.info(f"Consultando: {url} con params: {params}")
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Verificar si recibimos contenido HTML válido
            if "text/html" not in response.headers.get("Content-Type", ""):
                logger.error(f"Respuesta no es HTML: {response.headers.get('Content-Type')}")
                return []
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Buscar todos los contenedores de juegos en la estructura actual
            game_containers = soup.select("#search_resultsRows > a")
            
            if not game_containers:
                logger.warning(f"No se encontraron juegos en la página {page} con el tag {tag}")
                logger.warning(f"Selector '#search_resultsRows > a' no encontró resultados")
                return []
            
            logger.info(f"Encontrados {len(game_containers)} contenedores de juegos")
            
            for container in game_containers:
                try:
                    # Extraer ID del juego de la URL
                    app_id = container.get("data-ds-appid")
                    if not app_id:
                        continue
                    
                    # Extraer nombre del juego
                    title_elem = container.select_one(".title")
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    # Extraer precio
                    price_elem = container.select_one(".search_price")
                    price_text = price_elem.text.strip() if price_elem else ""
                    
                    # Verificar si tiene tags indie (los extraeremos en detalle después)
                    games_list.append({
                        "app_id": app_id,
                        "nombre": title,
                        "url": container.get("href", ""),
                        "precio_texto": price_text
                    })
                    
                except Exception as e:
                    logger.error(f"Error procesando un juego en la lista: {str(e)}")
            
            logger.info(f"Extraídos {len(games_list)} juegos de la página {page} con el tag {tag}")
            return games_list
            
        except Exception as e:
            logger.error(f"Error scrapeando la página {page} del tag {tag}: {str(e)}")
            return []
    
    def get_game_details(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de un juego scrapeando su página
        
        Args:
            app_id: ID del juego en Steam
            
        Returns:
            Diccionario con detalles del juego o None si hay error
        """
        try:
            # Retraso para evitar bloqueos
            time.sleep(random.uniform(2.0, 4.0))
            
            url = f"{self.base_url}/app/{app_id}/"
            
            logger.info(f"Consultando detalles del juego ID: {app_id} en {url}")
            
            response = self.session.get(url)
            if response.status_code != 200:
                logger.error(f"Error al obtener página del juego {app_id}: Código {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extraer nombre del juego
            title_elem = soup.select_one(".apphub_AppName")
            title = title_elem.text.strip() if title_elem else "Unknown"
            
            # Obtener todos los tags/categorías
            tags = []
            tag_elements = soup.select(".app_tag")
            
            if not tag_elements:
                logger.warning(f"No se encontraron tags para el juego {title} (ID: {app_id})")
            
            for tag_elem in tag_elements:
                tag_text = tag_elem.text.strip()
                tags.append(tag_text)
            
            logger.info(f"Tags encontrados para {title}: {tags}")
            
            # Verificar si tiene los tags requeridos (debe ser Indie)
            has_required_tags = any(include_tag.lower() in [t.lower() for t in tags] for include_tag in self.include_tags)
            
            if not has_required_tags:
                logger.info(f"El juego {title} (ID: {app_id}) no es indie, se omite")
                return None
            
            # Verificar si tiene tags excluidos
            has_excluded_tags = any(any(exclude_tag.lower() in t.lower() for exclude_tag in self.exclude_tags) for t in tags)
            
            if has_excluded_tags:
                logger.info(f"El juego {title} (ID: {app_id}) tiene contenido excluido, se omite")
                return None
            
            # Extraer descripción
            desc_elem = soup.select_one(".game_description_snippet")
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Extraer imagen principal
            img_elem = soup.select_one(".game_header_image_full") or soup.select_one(".game_header_image")
            image_url = img_elem.get("src") if img_elem else ""
            
            # Extraer precio
            price_elem = soup.select_one(".game_purchase_price") or soup.select_one(".discount_final_price")
            price_text = price_elem.text.strip() if price_elem else "Free"
            
            # Convertir precio a número
            price = 0.0
            if price_text != "Free":
                # Eliminar símbolos de moneda y convertir a float
                price_match = re.search(r'(\d+[.,]?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', '.'))
            
            # Generar géneros (usamos los tags como géneros)
            genres = [tag for tag in tags if tag not in self.exclude_tags][:5]  # Limitar a 5 géneros
            
            # Asegurar que los tipos de datos sean correctos para la base de datos
            result = {
                "nombre": str(title)[:255],  # Limitar longitud para la base de datos
                "generos": [str(g)[:50] for g in genres][:10],  # Limitar cantidad y longitud
                "precio": float(price),
                "descripcion": str(description)[:1000],  # Limitar longitud
                "tags": [str(t)[:50] for t in tags][:20],  # Limitar cantidad y longitud
                "imagen_principal": str(image_url)[:500]  # Limitar longitud
            }
            
            logger.info(f"Obtenidos detalles completos para el juego '{title}' (ID: {app_id})")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles del juego {app_id}: {str(e)}")
            return None
    
    def scrape_bulk_indie_games(self, min_new_games: int = 100, existing_names=None) -> Dict[str, Any]:
        """
        Scrapea juegos indies de Steam de forma masiva asegurando un mínimo de juegos nuevos
        
        Args:
            min_new_games: Número mínimo de juegos NUEVOS a añadir (por defecto: 100)
            existing_names: Lista de nombres de juegos que ya existen en la base de datos
            
        Returns:
            Diccionario con resultados del scraping
        """
        results = {
            "total_consultados": 0,
            "juegos_validos": 0,
            "juegos_duplicados": 0,
            "juegos_excluidos": 0,
            "errores": 0
        }
        
        # Si no se proporciona lista de nombres existentes, inicializar como vacía
        if existing_names is None:
            existing_names = []
        
        # Search terms para buscar juegos indies
        search_terms = ["indie", "indie game", "indie roguelike", "indie adventure", "indie rpg", "indie platformer"]
        valid_games = []
        
        logger.info(f"Iniciando scraping masivo, objetivo: {min_new_games} juegos indies NUEVOS")
        
        # Iterar por cada término de búsqueda
        for term in search_terms:
            page = 1
            max_pages = 30  # Aumentar el máximo de páginas por búsqueda para tener más posibilidades de encontrar nuevos juegos
            
            while results["juegos_validos"] < min_new_games and page <= max_pages:
                # Obtener lista de juegos de la página actual
                games_list = self.get_games_from_browse_page(tag=term, page=page)
                
                if not games_list:
                    logger.info(f"No hay más juegos para el término '{term}' o se alcanzó el final de resultados")
                    break
                
                results["total_consultados"] += len(games_list)
                page += 1
                
                # Procesar cada juego
                for game in games_list:
                    try:
                        app_id = game.get("app_id")
                        if not app_id:
                            continue
                        
                        # Verificar primero si el nombre ya existe para evitar procesamiento innecesario
                        if game.get("nombre") in existing_names:
                            results["juegos_duplicados"] += 1
                            continue
                        
                        # Obtener detalles completos
                        game_details = self.get_game_details(app_id)
                        
                        if game_details:
                            # Verificar si el nombre ya existe en la base de datos
                            if game_details["nombre"] in existing_names:
                                results["juegos_duplicados"] += 1
                                continue
                                
                            valid_games.append(game_details)
                            existing_names.append(game_details["nombre"])  # Añadir a la lista de nombres existentes
                            results["juegos_validos"] += 1
                            
                            if results["juegos_validos"] % 10 == 0:
                                logger.info(f"Progreso: {results['juegos_validos']}/{min_new_games} juegos nuevos encontrados")
                            
                            if results["juegos_validos"] >= min_new_games:
                                logger.info(f"Alcanzado el objetivo de {min_new_games} juegos nuevos. Finalizando.")
                                break
                        else:
                            results["juegos_excluidos"] += 1
                    
                    except Exception as e:
                        logger.error(f"Error procesando juego: {str(e)}")
                        results["errores"] += 1
                
                # Si ya tenemos suficientes juegos, salir del bucle de páginas
                if results["juegos_validos"] >= min_new_games:
                    break
            
            # Si ya tenemos suficientes juegos, salir del bucle de términos
            if results["juegos_validos"] >= min_new_games:
                break
        
        logger.info(f"Scraping completado: {results['juegos_validos']} juegos nuevos de {results['total_consultados']} consultados")
        
        return {
            "results": valid_games,
            "stats": results
        }

# Instancia global
steam_scraper = SteamScraper()
