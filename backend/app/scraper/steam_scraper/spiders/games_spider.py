import scrapy
import json
from scrapy.http import Request
from ..items import GameItem

class GamesSpider(scrapy.Spider):
    name = "games_spider"
    allowed_domains = ["store.steampowered.com"]
    start_urls = ["https://store.steampowered.com/tags/en/Indie/"]
    
    def parse(self, response):
        # Extrae los juegos de la primera página
        games = response.css('div.store_capsule')
        for game in games:
            game_url = game.css('a::attr(href)').get()
            if game_url:
                yield Request(url=game_url, callback=self.parse_game)
        
        # Obtén el parámetro start para la siguiente página
        start = 50  # Steam muestra ~50 juegos por página
        
        # Genera solicitudes para las siguientes páginas (máximo 10 páginas)
        for offset in range(start, 500, 50):
            next_page_url = f"https://store.steampowered.com/search/results?query&start={offset}&count=50&dynamic_data=&sort_by=_ASC&tags=492&snr=1_7_7_230_7&infinite=1"
            yield Request(url=next_page_url, callback=self.parse_json_results)
    
    def parse_json_results(self, response):
        try:
            data = json.loads(response.text)
            if 'results_html' in data:
                # Crear un objeto response con el HTML devuelto por AJAX
                html_response = scrapy.http.HtmlResponse(
                    url=response.url,
                    body=data['results_html'].encode('utf-8'),
                    encoding='utf-8'
                )
                
                games = html_response.css('a.search_result_row')
                for game in games:
                    game_url = game.css('::attr(href)').get()
                    if game_url:
                        yield Request(url=game_url, callback=self.parse_game)
        except json.JSONDecodeError:
            self.logger.error(f"Error decodificando JSON de {response.url}")
    
    def parse_game(self, response):
        # Ignora páginas de verificación de edad
        if "agecheck" in response.url:
            return
        
        game_item = GameItem()
        
        # Extrae los datos básicos
        game_item['name'] = response.css('div.apphub_AppName::text').get()
        game_item['url'] = response.url
        
        # Extrae el precio (puede tener diferentes formatos)
        price = response.css('div.game_purchase_price::text, div.discount_final_price::text').get()
        if price:
            price = price.strip()
            if "Free" in price or "free" in price:
                game_item['price'] = "Gratuito"
            else:
                game_item['price'] = price
        else:
            game_item['price'] = "No disponible"
        
        # Extrae los géneros
        genres = response.css('div.details_block a[href*="/genre/"]::text').getall()
        if genres:
            game_item['genres'] = [genre.strip() for genre in genres]
        else:
            game_item['genres'] = []
        
        # Extrae etiquetas
        tags = response.css('a.app_tag::text').getall()
        if tags:
            game_item['tags'] = [tag.strip() for tag in tags]
        else:
            game_item['tags'] = []
        
        yield game_item
