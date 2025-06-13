# Documentación de la Base de Datos de Hidden Gem

Este documento proporciona una descripción detallada de la estructura de la base de datos utilizada en el proyecto Hidden Gem, incluyendo los modelos, relaciones y consideraciones de diseño.

## Visión General

Hidden Gem utiliza una base de datos PostgreSQL para almacenar información sobre usuarios, juegos, recomendaciones y preferencias. La estructura está diseñada para soportar un sistema de recomendación de videojuegos indie basado en preferencias de usuario.

## Configuración de Conexión

La conexión a la base de datos se configura en `app/config.py` utilizando variables de entorno o valores predeterminados:

```python
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
```

## Modelos Principales

### Usuario

Almacena información sobre los usuarios registrados en la plataforma.

| Campo      | Tipo      | Descripción                               |
|------------|-----------|-------------------------------------------|
| id         | Integer   | Identificador único (clave primaria)      |
| nick       | String    | Nombre de usuario único                   |
| email      | String    | Correo electrónico único                  |
| contraseña | String    | Contraseña hasheada con bcrypt            |
| precio_max | Float     | Precio máximo para recomendaciones        |
| creado_en  | DateTime  | Fecha y hora de registro                  |

### JuegosFavoritosDeUsuarioQueProvienenDeRawg

Almacena juegos favoritos de los usuarios obtenidos de la API de RAWG.

| Campo       | Tipo      | Descripción                               |
|-------------|-----------|-------------------------------------------|
| id          | Integer   | Identificador único (clave primaria)      |
| nombre      | String    | Nombre del juego                          |
| imagen      | String    | URL de la imagen del juego                |
| descripcion | Text      | Descripción del juego                     |
| generos     | ARRAY     | Lista de géneros del juego                |
| tags        | ARRAY     | Lista de etiquetas del juego              |

### JuegosScrapeadoDeSteamParaRecomendaiones

Almacena juegos obtenidos mediante scraping de Steam para recomendaciones.

| Campo            | Tipo      | Descripción                               |
|------------------|-----------|-------------------------------------------|
| id               | Integer   | Identificador único (clave primaria)      |
| nombre           | String    | Nombre del juego                          |
| url_steam        | String    | URL del juego en Steam                    |
| imagen_principal | String    | URL de la imagen principal                |
| precio           | Float     | Precio del juego                          |
| descripcion      | Text      | Descripción del juego                     |
| tags             | ARRAY     | Lista de etiquetas del juego              |
| generos          | ARRAY     | Lista de géneros del juego                |
| fecha_agregado   | DateTime  | Fecha en que se añadió a la base de datos |
| contenido_adulto | Boolean   | Indica si contiene contenido para adultos |

## Relaciones

### Usuario - Juegos Favoritos

Relación muchos a muchos entre usuarios y juegos favoritos.

```
Usuario <-> JuegosFavoritosDeUsuarioQueProvienenDeRawg
```

Esta relación se implementa mediante una tabla de unión que permite a cada usuario tener múltiples juegos favoritos, y a cada juego ser favorito de múltiples usuarios.

## Diagrama Entidad-Relación

```
+----------------+       +------------------------+
|    Usuario     |       | JuegosFavoritosDeUs.. |
+----------------+       +------------------------+
| id             +-------+ id                    |
| nick           |       | nombre                |
| email          |       | imagen                |
| contraseña     |       | descripcion           |
| precio_max     |       | generos               |
| creado_en      |       | tags                  |
+----------------+       +------------------------+
        |
        |
        v
+-------------------------+
| JuegosScrapeadoDeSte.. |
+-------------------------+
| id                     |
| nombre                 |
| url_steam              |
| imagen_principal       |
| precio                 |
| descripcion            |
| tags                   |
| generos                |
| fecha_agregado         |
| contenido_adulto       |
+-------------------------+
```

## Inicialización de la Base de Datos

La base de datos se inicializa en `app/main.py` utilizando SQLAlchemy:

```python
Base.metadata.create_all(bind=engine)
```

Este comando crea todas las tablas definidas en los modelos si no existen.

## Sesiones de Base de Datos

Las sesiones de base de datos se gestionan mediante un generador de dependencias en `app/database.py`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Este generador se utiliza en los endpoints para obtener una sesión de base de datos y asegurar que se cierre correctamente después de cada solicitud.

## Consideraciones para Desarrollo y Producción

### Migraciones

Para proyectos en producción, se recomienda utilizar Alembic para gestionar migraciones de esquema:

```bash
# Inicializar Alembic
alembic init alembic

# Crear una nueva migración
alembic revision --autogenerate -m "descripción de cambios"

# Aplicar migraciones
alembic upgrade head
```

### Índices

Para mejorar el rendimiento, se recomienda añadir índices a campos frecuentemente consultados:

- Índice en `Usuario.email` y `Usuario.nick` para búsquedas rápidas durante la autenticación
- Índice en `JuegosScrapeadoDeSteamParaRecomendaiones.nombre` para búsquedas por nombre

### Respaldo y Recuperación

Se recomienda configurar respaldos regulares de la base de datos:

```bash
# Respaldo
pg_dump -U postgres -d hiddengem > backup.sql

# Recuperación
psql -U postgres -d hiddengem < backup.sql
```

## Ejemplos de Consultas Comunes

### Obtener Juegos Favoritos de un Usuario

```python
user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
favorite_games = user.juegos_favoritos
```

### Buscar Juegos por Género

```python
games = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones)
matches = [game for game in games.all() if any(genre.lower() in game_genre.lower() for game_genre in game.generos)]
```

### Añadir un Juego a Favoritos

```python
user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter_by(id=game_id).first()
user.juegos_favoritos.append(game)
db.commit()
```