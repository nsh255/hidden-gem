BOT_NAME = 'steam_scraper'

SPIDER_MODULES = ['app.scraper.steam_scraper.spiders']
NEWSPIDER_MODULE = 'app.scraper.steam_scraper.spiders'

# Configuración para evitar bloqueos
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# No respetar robots.txt para obtener más datos
ROBOTSTXT_OBEY = False

# Aumentamos ligeramente las solicitudes concurrentes para acelerar el scraper
CONCURRENT_REQUESTS = 3  # Aumentado de 2 a 3

# Reducimos el delay entre solicitudes para acelerar el scraping, pero manteniéndolo
# en un nivel razonable para evitar bloqueos
DOWNLOAD_DELAY = 2  # Reducido de 3 a 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Sin límite de profundidad para que explore más páginas
DEPTH_LIMIT = 0

# Mayor timeout para solicitudes
DOWNLOAD_TIMEOUT = 60

# Habilitación de pipelines
ITEM_PIPELINES = {
    'app.scraper.steam_scraper.pipelines.SteamScraperPipeline': 300,
    'app.scraper.steam_scraper.pipelines.PostgreSQLPipeline': 400,
    'app.scraper.steam_scraper.pipelines.JsonPipeline': 500,
}

# Configuración del throttling automático ajustada
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0  # Aumentado ligeramente
AUTOTHROTTLE_DEBUG = True

# Habilitar cookies para mantener la sesión
COOKIES_ENABLED = True

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
    'Referer': 'https://store.steampowered.com/',
}

# Configuraciones para reintentos
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

# Nivel de logging para más información
LOG_LEVEL = 'INFO'

# Almacenar en cache respuestas HTTP para reducir solicitudes
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 172800  # 48 horas (aumentado de 24 a 48 horas)
HTTPCACHE_DIR = 'httpcache'
