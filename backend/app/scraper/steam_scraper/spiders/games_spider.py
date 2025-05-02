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
    
    # Ampliamos las categorías de inicio para incluir más subgéneros y nichos de indie
    start_urls = [
        "https://store.steampowered.com/tags/en/Indie/",
        "https://store.steampowered.com/tags/en/Indie%20Adventure/",
        "https://store.steampowered.com/tags/en/Indie%20Puzzle/",
        "https://store.steampowered.com/tags/en/Indie%20Platformer/",
        # Añadimos más categorías para aumentar la cobertura
        "https://store.steampowered.com/tags/en/2D/",
        "https://store.steampowered.com/tags/en/Pixel%20Graphics/",
        "https://store.steampowered.com/tags/en/Roguelike/",
        "https://store.steampowered.com/tags/en/Visual%20Novel/",
        "https://store.steampowered.com/tags/en/Casual/",
        "https://store.steampowered.com/tags/en/Game%20Development/",
        # Nuevas categorías para obtener más juegos
        "https://store.steampowered.com/tags/en/Action%20Indie/",
        "https://store.steampowered.com/tags/en/Metroidvania/",
        "https://store.steampowered.com/tags/en/Bullet%20Hell/",
        "https://store.steampowered.com/tags/en/Singleplayer/",
        "https://store.steampowered.com/tags/en/Simulation/",
        "https://store.steampowered.com/tags/en/Early%20Access/",
    ]
    
    # Número máximo de intentos para las solicitudes fallidas
    max_retry_times = 5
    
    # Aumentamos el número máximo de páginas a recorrer por categoría
    max_pages = 400  # Aumentado de 200 a 400 para obtener más juegos
    
    def __init__(self, *args, **kwargs):
        super(GamesSpider, self).__init__(*args, **kwargs)
        self.games_count = 0
        # Convertimos explícitamente el valor a entero y aumentamos el valor predeterminado
        self.max_games = int(kwargs.get('max_games', 2000))  # Aumentado de 500 a 2000
        self.logger.info(f"Configurado para scrapear hasta {self.max_games} juegos indie")
        # Inicializamos conjunto para evitar duplicados
        self.processed_urls = set()
        
        # Lista de grandes editores que NO son indies
        self.major_publishers = [
            'electronic arts', 'ea', 'ubisoft', 'activision', 'blizzard', 'activision blizzard',
            'take-two', '2k games', 'bethesda', 'microsoft', 'xbox game studios', 
            'sony', 'playstation studios', 'nintendo', 'square enix', 'bandai namco',
            'capcom', 'sega', 'konami', 'paradox interactive', 'devolver digital',
            'thq nordic', 'warner bros', 'wb games', 'focus home interactive', 'focus entertainment',
            'deep silver', 'epic games', 'riot games', 'valve', '505 games'
        ]
    
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
            '2D': '3871',
            'Pixel Graphics': '3859',
            'Roguelike': '1716',
            'Visual Novel': '3798',
            'Casual': '597',
            'Game Development': '1702',
            'Action Indie': '492,19',
            'Metroidvania': '1628',
            'Bullet Hell': '4885',
            'Singleplayer': '4182',
            'Simulation': '599',
            'Early Access': '493',
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
        
        # Evitamos procesar URLs duplicadas
        if response.url in self.processed_urls:
            self.logger.debug(f"URL ya procesada, omitiendo: {response.url}")
            return
        self.processed_urls.add(response.url)
        
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
        
        # Extraer desarrollador y editor para verificar si es indie
        developers = response.css('div.dev_row:contains("Developer:") a::text, div.details_block a[href*="developer"]::text').getall()
        publishers = response.css('div.dev_row:contains("Publisher:") a::text, div.details_block a[href*="publisher"]::text').getall()
        
        # Guardar esta información en el item
        game_item['developers'] = [dev.strip() for dev in developers] if developers else []
        game_item['publishers'] = [pub.strip() for pub in publishers] if publishers else []
        
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
            
            # NUEVO: Filtrar juegos con contenido sexual
            if any(tag.strip() == "Contenido sexual" for tag in tags):
                self.logger.info(f"Omitiendo juego con contenido sexual: {game_item.get('name', 'Unknown')}")
                return None
        else:
            self.logger.debug(f"No se encontraron etiquetas para {game_item['name']}")
            game_item['tags'] = []
        
        # CRITERIOS MEJORADOS PARA IDENTIFICAR JUEGOS INDIE
        
        # 1. Verificar si proviene de una categoría explícitamente indie
        from_indie_category = is_from_indie_category or category == 'Indie' or 'Indie' in category
        
        # 2. Verificar etiquetas y géneros
        has_indie_tag = 'Indie' in game_item.get('tags', [])
        has_indie_genre = 'Indie' in game_item.get('genres', [])
        
        # 3. Verificar keywords en tags - Ampliamos esta lista para ser más inclusivos
        indie_keywords = ['indie', 'solo developer', 'small team', 'pixel', 'retro', 'roguelike', 
                          'handcrafted', 'experimental', 'artistic', 'minimalist', 'procedural',
                          'game jam', 'crowdfunded', 'kickstarter', 'early access', 'development',
                          'low poly', 'voxel', 'unique', 'stylized', 'atmospheric', 'casual', 
                          'hand-drawn', '2d', 'metroidvania', 'roguelite', 'single developer']
        
        has_indie_keywords = any(indie_keyword in str(tag).lower() for tag in game_item.get('tags', []) 
                               for indie_keyword in indie_keywords)
        
        # 4. Verificar que NO sea de grandes editores
        is_from_major_publisher = False
        for publisher in game_item.get('publishers', []):
            if publisher.lower() in self.major_publishers:
                is_from_major_publisher = True
                break
        
        for developer in game_item.get('developers', []):
            if developer.lower() in self.major_publishers:
                is_from_major_publisher = True
                break
        
        # Evaluación final: un juego es indie si cumple al menos con algunos criterios y no es de un gran editor
        # Hacemos la evaluación un poco más inclusiva
        is_indie = (
            # Al menos uno de estos criterios debe cumplirse
            (from_indie_category or has_indie_tag or has_indie_genre or has_indie_keywords) and
            # Y no debe ser de un gran editor
            not is_from_major_publisher
        )
        
        # Registramos en el log el motivo de la evaluación
        if is_indie:
            self.logger.info(f"Juego: '{game_item['name']}' clasificado como INDIE porque: " +
                            (f"Categoría indie: {from_indie_category}, " if from_indie_category else "") +
                            (f"Tag indie: {has_indie_tag}, " if has_indie_tag else "") +
                            (f"Género indie: {has_indie_genre}, " if has_indie_genre else "") +
                            (f"Keywords indie: {has_indie_keywords}" if has_indie_keywords else ""))
        else:
            reasons = []
            if is_from_major_publisher:
                publishers_found = game_item.get('publishers', [])
                developers_found = game_item.get('developers', [])
                reasons.append(f"Es de un gran publisher/developer: Publishers={publishers_found}, Developers={developers_found}")
            if not (from_indie_category or has_indie_tag or has_indie_genre or has_indie_keywords):
                reasons.append("No tiene suficientes indicadores de ser indie")
            
            self.logger.debug(f"Juego: '{game_item['name']}' NO clasificado como indie. Motivo: {', '.join(reasons)}")
        
        game_item['is_indie'] = is_indie
        
        # Si alcanzamos el límite de juegos, nos detenemos
        if self.games_count >= self.max_games:
            self.logger.info(f"Alcanzado el límite de {self.max_games} juegos. Deteniendo.")
            return
        
        # Solo si consideramos que es un juego indie lo contamos
        if is_indie:
            self.games_count += 1
            self.logger.info(f"Juegos indie procesados: {self.games_count}/{self.max_games}")
            yield game_item
        else:
            self.logger.debug(f"Juego no considerado indie, omitiendo: {game_item['name']}")
    
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
