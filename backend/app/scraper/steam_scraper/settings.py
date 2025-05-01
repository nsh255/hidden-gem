BOT_NAME = 'steam_scraper'

SPIDER_MODULES = ['app.scraper.steam_scraper.spiders']
NEWSPIDER_MODULE = 'app.scraper.steam_scraper.spiders'

# Configuraciones para evitar bloqueos
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Respeta robots.txt (puede cambiarse a False si es necesario)
ROBOTSTXT_OBEY = True

# Configuración para limitar el número de solicitudes concurrentes
CONCURRENT_REQUESTS = 4

# Delay entre solicitudes para evitar ser bloqueado
DOWNLOAD_DELAY = 1

# Habilitación de pipelines
ITEM_PIPELINES = {
    'app.scraper.steam_scraper.pipelines.SteamScraperPipeline': 300,
    # Descomenta uno de los siguientes según necesites
    # 'app.scraper.steam_scraper.pipelines.PostgreSQLPipeline': 400,
    # 'app.scraper.steam_scraper.pipelines.JsonPipeline': 500,
}

# Configuración del throttling automático
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Headers adicionales para simular un navegador real
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}
