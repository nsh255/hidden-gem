import scrapy
import json
from scrapy.http import Request
from app.scraper.steam_scraper.items import GameItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
import time
import random
import logging

class GamesSpider(scrapy.Spider):
    name = "games_spider"
    allowed_domains = ["store.steampowered.com"]
    
    # Solo nos enfocamos en juegos indie
    start_urls = [
        "https://store.steampowered.com/tags/en/Indie/",
        # Incluimos subgéneros populares de indie para ampliar cobertura
        "https://store.steampowered.com/tags/en/Indie%20Adventure/",
        "https://store.steampowered.com/tags/en/Indie%20Puzzle/",
        "https://store.steampowered.com/tags/en/Indie%20Platformer/"
    ]
    
    # Número máximo de intentos para las solicitudes fallidas
    max_retry_times = 5
    
    # Aumentamos el número máximo de páginas a recorrer por categoría
    max_pages = 100  # Más páginas para categoría indie
    
    def __init__(self, *args, **kwargs):
        super(GamesSpider, self).__init__(*args, **kwargs)
        self.games_count = 0
        self.max_games = kwargs.get('max_games', 20000)  # Aumentado el límite predeterminado
        self.logger.info(f"Configurado para scrapear hasta {self.max_games} juegos indie")
    
    def start_requests(self):
        self.logger.info("Iniciando spider de Steam para juegos Indie")
        for url in self.start_urls:
            category = url.split('/en/')[1].strip('/')
            self.logger.info(f"Procesando categoría: {category}")
            yield Request(url=url, callback=self.parse, 
                          errback=self.errback_httpbin,
                          meta={'download_timeout': 30, 'category': category})
    
    def parse(self, response):
        category = response.meta.get('category', 'Unknown')
        self.logger.info(f"Procesando página principal de categoría {category}: {response.url}")
        
        # Extrae los juegos de la primera página
        games = response.css('div.store_capsule, a.search_result_row')
        self.logger.info(f"Encontrados {len(games)} juegos en la página principal de {category}")
        
        # Añadimos verificación adicional para asegurar que solo obtenemos indie
        for game in games:
            if self.games_count >= self.max_games:
                self.logger.info(f"Alcanzado límite de {self.max_games} juegos. Deteniendo spider.")
                return
            
            game_url = game.css('a::attr(href), ::attr(href)').get()
            if game_url:
                # Añadimos parámetro indie=1 para indicar que viene de categoría indie
                clean_url = game_url.split('?')[0]
                yield Request(url=clean_url, 
                              callback=self.parse_game,
                              errback=self.errback_httpbin,
                              meta={'download_timeout': 30, 'category': category, 'indie': True})
        
        # Obtén el parámetro start para la siguiente página
        start = 50  # Steam muestra ~50 juegos por página
        
        # Genera solicitudes para las siguientes páginas (ahora hasta max_pages)
        for offset in range(start, self.max_pages * 50, 50):
            if self.games_count >= self.max_games:
                return
                
            # Añade un timestamp para evitar problemas de caché
            timestamp = int(time.time())
            tag_id = self.get_tag_id_for_category(category)  # Método nuevo para obtener el ID de tag
            next_page_url = f"https://store.steampowered.com/search/results?query&start={offset}&count=50&dynamic_data=&sort_by=_ASC&tags={tag_id}&snr=1_7_7_230_7&infinite=1&_={timestamp}"
            
            # Añadimos un retraso aleatorio entre solicitudes para evitar bloqueos
            delay = random.uniform(1.0, 3.0)
            self.logger.info(f"Esperando {delay:.2f}s antes de solicitar página {offset//50 + 1} de {category}")
            
            yield Request(url=next_page_url, 
                          callback=self.parse_json_results,
                          errback=self.errback_httpbin,
                          meta={'download_timeout': 30, 'category': category},
                          dont_filter=True)  # Importante para evitar filtrado de URLs similares
    
    def get_tag_id_for_category(self, category):
        # Mapeo específico para categorías indie
        tag_mapping = {
            'Indie': '492',
            'Indie Adventure': '492,21',
            'Indie Puzzle': '492,1664',
            'Indie Platformer': '492,1625',
            'Unknown': '492'  # Por defecto indie
        }
        return tag_mapping.get(category, '492')
    
    def parse_json_results(self, response):
        category = response.meta.get('category', 'Unknown')
        try:
            self.logger.info(f"Procesando resultados JSON de categoría {category}: {response.url}")
            data = json.loads(response.text)
            if 'results_html' in data:
                # Crear un objeto response con el HTML devuelto por AJAX
                html_response = scrapy.http.HtmlResponse(
                    url=response.url,
                    body=data['results_html'].encode('utf-8'),
                    encoding='utf-8'
                )
                
                games = html_response.css('a.search_result_row')
                self.logger.info(f"Encontrados {len(games)} juegos en resultados JSON de {category}")
                
                for game in games:
                    if self.games_count >= self.max_games:
                        return
                        
                    game_url = game.css('::attr(href)').get()
                    if game_url:
                        # Añadimos delay aleatorio variable
                        delay = random.uniform(0.2, 0.8)  # delay corto entre solicitudes de juegos individuales
                        time.sleep(delay)
                        
                        yield Request(url=game_url, 
                                     callback=self.parse_game,
                                     errback=self.errback_httpbin,
                                     meta={'download_timeout': 30, 'category': category})
        except json.JSONDecodeError:
            self.logger.error(f"Error decodificando JSON de {response.url}")
            self.logger.debug(f"Contenido recibido: {response.text[:200]}...")
    
    def parse_game(self, response):
        category = response.meta.get('category', 'Unknown')
        is_from_indie_category = response.meta.get('indie', False)
        
        # Ignora páginas de verificación de edad
        if "agecheck" in response.url:
            self.logger.info(f"Omitiendo verificación de edad: {response.url}")
            # Intenta acceder directamente a la página del juego saltando la verificación
            app_id = response.url.split('/app/')[1].split('/')[0] if '/app/' in response.url else None
            if app_id:
                # Construimos la URL directa con parámetros para omitir verificación de edad
                direct_url = f"https://store.steampowered.com/app/{app_id}/?birthtime=189324001"
                yield Request(url=direct_url, 
                             callback=self.parse_game,
                             errback=self.errback_httpbin,
                             meta={'download_timeout': 30, 'category': category})
            return
        
        self.logger.info(f"Procesando juego de categoría {category}: {response.url}")
        game_item = GameItem()
        
        # Extrae los datos básicos con selectores mejorados y alternativas
        name = response.css('div.apphub_AppName::text, div#appHubAppName::text, span.game_area_name::text').get()
        if name:
            game_item['name'] = name.strip()
            self.logger.info(f"Juego encontrado: {name.strip()}")
        else:
            self.logger.warning(f"No se pudo extraer el nombre del juego de {response.url}")
            return
            
        game_item['url'] = response.url
        
        # Extraer app_id del juego
        app_id = None
        if '/app/' in response.url:
            app_id = response.url.split('/app/')[1].split('/')[0]
            game_item['app_id'] = app_id
        
        # Extrae el precio (puede tener diferentes formatos)
        price = response.css('div.game_purchase_price::text, div.discount_final_price::text, div.game_area_purchase_game_wrapper .price::text').get()
        if price:
            price = price.strip()
            if "Free" in price or "free" in price:
                game_item['price'] = 0.0
            else:
                # Intenta convertir el precio a un número flotante
                try:
                    # Elimina símbolos de moneda y espacios
                    price = price.replace('$', '').replace('€', '').replace(',', '.').strip()
                    game_item['price'] = float(price)
                except ValueError:
                    self.logger.warning(f"No se pudo convertir el precio '{price}' para {game_item['name']}")
                    game_item['price'] = None
        else:
            self.logger.debug(f"No se encontró precio para {game_item['name']}")
            game_item['price'] = None
        
        # Extrae la descripción
        description = response.css('div.game_description_snippet::text').get() or ""
        game_item['description'] = description.strip()
        
        # Extrae los géneros
        genres = response.css('div.details_block a[href*="/genre/"]::text, div.game_details_content a[href*="/genre/"]::text, div.glance_tags a[href*="/genre/"]::text').getall()
        if genres:
            game_item['genres'] = [genre.strip() for genre in genres]
        else:
            self.logger.debug(f"No se encontraron géneros para {game_item['name']}")
            game_item['genres'] = []
        
        # Extrae etiquetas - mejoramos los selectores
        tags = response.css('a.app_tag::text, div.glance_tags a::text').getall()
        if tags:
            game_item['tags'] = [tag.strip() for tag in tags]
        else:
            self.logger.debug(f"No se encontraron etiquetas para {game_item['name']}")
            game_item['tags'] = []
        
        # Determinar si el juego es indie basándonos en múltiples criterios
        is_indie = (
            is_from_indie_category or  # Si viene de categoría indie
            'Indie' in game_item['tags'] or  # Si tiene tag "Indie"
            'Indie' in game_item['genres'] or  # Si tiene género "Indie"
            any(indie_keyword in str(tag).lower() for tag in game_item['tags'] 
                for indie_keyword in ['indie', 'solo developer', 'small team'])  # Palabras clave
        )
        
        # Si no es indie, no continuamos procesando este juego
        if not is_indie:
            self.logger.info(f"Saltando juego no indie: {game_item['name']}")
            return
        
        # Marcar explícitamente como indie
        game_item['is_indie'] = True
        
        # Extrae valoraciones
        review_summary = response.css('span.game_review_summary::text').get()
        game_item['rating_text'] = review_summary.strip() if review_summary else None
        
        # Marcar origen
        game_item['source'] = 'steam'
        
        self.logger.info(f"Datos extraídos exitosamente para juego indie: {game_item['name']}")
        self.games_count += 1
        self.logger.info(f"Juegos indie procesados: {self.games_count}/{self.max_games}")
        
        yield game_item
    
    def errback_httpbin(self, failure):
        # Log de diferentes tipos de errores HTTP
        self.logger.error(f"Error en la solicitud: {failure.request.url}")
        
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f"Error HTTP {response.status} en: {response.url}")
            
            # Reintentar en caso de 403 (Forbidden) o 429 (Too Many Requests)
            if response.status in [403, 429, 500, 502, 503, 504]:
                retry_count = failure.request.meta.get('retry_count', 0) + 1
                if retry_count <= self.max_retry_times:
                    # Esperar más tiempo antes de reintentar
                    wait_time = 5 + random.randint(5, 15) * retry_count
                    self.logger.info(f"Reintentando solicitud a {failure.request.url} en {wait_time}s (intento {retry_count})")
                    time.sleep(wait_time)
                    
                    # Crear una nueva solicitud con contador de reintentos
                    request = failure.request.copy()
                    request.meta['retry_count'] = retry_count
                    request.dont_filter = True
                    yield request
                    
        elif failure.check(DNSLookupError):
            self.logger.error(f"Error DNS en: {failure.request.url}")
        elif failure.check(TimeoutError, TCPTimedOutError):
            self.logger.error(f"Timeout en: {failure.request.url}")
            
            # Reintentar en caso de timeout
            retry_count = failure.request.meta.get('retry_count', 0) + 1
            if retry_count <= self.max_retry_times:
                wait_time = 3 + random.randint(1, 5)
                self.logger.info(f"Reintentando solicitud por timeout a {failure.request.url} en {wait_time}s (intento {retry_count})")
                time.sleep(wait_time)
                
                request = failure.request.copy()
                request.meta['retry_count'] = retry_count
                request.dont_filter = True
                yield request
        else:
            self.logger.error(f"Error desconocido en: {failure.request.url}")
