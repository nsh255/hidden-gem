# Hidden Gem API - Documentación del Backend

## Descripción General

Hidden Gem es una API para recomendaciones de juegos indie. Esta API permite:
* Gestionar usuarios y sus preferencias de juegos
* Acceder a juegos de Steam para recomendaciones
* Permitir a los usuarios marcar sus juegos favoritos
* Interactuar con la API de RAWG para descubrir nuevos juegos
* Obtener recomendaciones personalizadas basadas en preferencias

## Requisitos Técnicos

* Python 3.8+
* FastAPI
* PostgreSQL
* Dependencias adicionales listadas en `requirements.txt`

## Configuración

La aplicación utiliza variables de entorno para la configuración:

## Arquitectura del Backend

El backend está construido con FastAPI y PostgreSQL:

- **FastAPI**: Framework web de alto rendimiento para APIs
- **PostgreSQL**: Base de datos relacional
- **SQLAlchemy**: ORM para interacción con la base de datos
- **Pydantic**: Validación de datos y serialización
- **Docker**: Contenedorización para desarrollo y despliegue

La API está organizada en módulos temáticos y todos los endpoints están disponibles bajo el prefijo `/api`.

## Modelos de Datos

### Usuario

```python
{
    "id": int,
    "nick": string,
    "email": string,
    "precio_max": float,
    "juegos_favoritos": [JuegoFavorito]
}
```

### JuegoSteam (Juegos scrapeados de Steam)

```python
{
    "id": int,
    "nombre": string,
    "generos": [string],
    "precio": float,
    "descripcion": string,
    "tags": [string],
    "imagen_principal": string
}
```

### JuegoFavorito (Juegos de RAWG marcados como favoritos)

```python
{
    "id": int,
    "nombre": string,
    "imagen": string,
    "descripcion": string,
    "generos": [string],
    "tags": [string],
    "usuarios": [Usuario]
}
```

## Endpoints API

Todos los endpoints están disponibles bajo el prefijo `/api`.

### Autenticación

#### Login (Form)
- **URL**: `/api/auth/login`
- **Método**: `POST`
- **Descripción**: Inicia sesión de usuario usando form-data (OAuth2)
- **Forma del Body**:
  ```
  username: string (email o nick del usuario)
  password: string
  ```
- **Respuesta**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "nick": "username",
      "email": "user@example.com"
    }
  }
  ```

#### Login JSON
- **URL**: `/api/auth/login-json`
- **Método**: `POST`
- **Descripción**: Alternativa JSON al endpoint de login estándar
- **Cuerpo**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Respuesta**: Igual que en el endpoint `/api/auth/login`

#### Registro
- **URL**: `/api/auth/register`
- **Método**: `POST`
- **Descripción**: Registra un nuevo usuario y devuelve token de autenticación
- **Cuerpo**:
  ```json
  {
    "nick": "username",
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Respuesta**: Igual que en los endpoints de login (token JWT + datos de usuario)

### Gestión de Usuarios

#### Crear Usuario
- **URL**: `/api/users/`
- **Método**: `POST`
- **Descripción**: Registra un nuevo usuario
- **Cuerpo**:
  ```json
  {
    "nick": "username",
    "email": "user@example.com",
    "contraseña": "password123",
    "precio_max": 20.0
  }
  ```
- **Respuesta**: Usuario creado con ID

#### Obtener Usuarios
- **URL**: `/api/users/`
- **Método**: `GET`
- **Descripción**: Obtiene lista de todos los usuarios
- **Parámetros**: `skip` (int, default=0), `limit` (int, default=100)

#### Obtener Usuario por ID
- **URL**: `/api/users/{user_id}`
- **Método**: `GET`
- **Descripción**: Obtiene detalles de un usuario específico

#### Actualizar Usuario
- **URL**: `/api/users/{user_id}`
- **Método**: `PUT`
- **Descripción**: Actualiza información de un usuario
- **Cuerpo**: Igual que al crear usuario

#### Eliminar Usuario
- **URL**: `/api/users/{user_id}`
- **Método**: `DELETE`
- **Descripción**: Elimina un usuario

### Juegos de Steam

#### Obtener Juegos de Steam
- **URL**: `/api/steam-games/`
- **Método**: `GET`
- **Descripción**: Obtiene juegos scraped de Steam
- **Parámetros**: `skip` (int, default=0), `limit` (int, default=100)

#### Obtener Juego de Steam por ID
- **URL**: `/api/steam-games/{game_id}`
- **Método**: `GET`
- **Descripción**: Obtiene detalles de un juego de Steam

#### Crear Juego de Steam
- **URL**: `/api/steam-games/`
- **Método**: `POST`
- **Descripción**: Añade un juego a la base de datos
- **Cuerpo**:
  ```json
  {
    "nombre": "Nombre del Juego",
    "generos": ["Acción", "Aventura"],
    "precio": 15.99,
    "descripcion": "Descripción del juego",
    "tags": ["Indie", "Pixel Art"],
    "imagen_principal": "url_de_la_imagen"
  }
  ```

#### Scrapear Juegos en Masa
- **URL**: `/api/steam-games/scrape-bulk`
- **Método**: `POST`
- **Descripción**: Inicia un proceso de scraping para obtener juegos nuevos de Steam
- **Parámetros**: `min_new_games` (int, default=100) - Número mínimo de juegos NUEVOS a añadir
- **Características**: 
  - Filtra automáticamente juegos que ya existen en la base de datos
  - Asegura que se añadan al menos el número mínimo de juegos nuevos especificado (si es posible)
  - Mantiene un registro de estadísticas sobre el proceso de scraping

#### Contar Juegos de Steam
- **URL**: `/api/steam-games/count`
- **Método**: `GET`
- **Descripción**: Obtiene número de juegos en la base de datos

### Juegos Favoritos

#### Crear Juego Favorito
- **URL**: `/api/favorite-games/`
- **Método**: `POST`
- **Descripción**: Crea un registro de juego favorito
- **Cuerpo**:
  ```json
  {
    "nombre": "Nombre del Juego",
    "imagen": "url_de_la_imagen",
    "descripcion": "Descripción del juego",
    "generos": ["Acción", "Aventura"],
    "tags": ["Indie", "Pixel Art"]
  }
  ```

#### Obtener Juegos Favoritos
- **URL**: `/api/favorite-games/`
- **Método**: `GET`
- **Descripción**: Obtiene lista de todos los juegos favoritos
- **Parámetros**: `skip` (int, default=0), `limit` (int, default=100)

#### Añadir Juego a Favoritos
- **URL**: `/api/favorite-games/add-favorite`
- **Método**: `POST`
- **Descripción**: Añade un juego a los favoritos de un usuario
- **Cuerpo**:
  ```json
  {
    "usuario_id": 1,
    "juego_id": 5
  }
  ```

#### Eliminar Juego de Favoritos
- **URL**: `/api/favorite-games/remove-favorite`
- **Método**: `DELETE`
- **Descripción**: Elimina un juego de los favoritos de un usuario
- **Cuerpo**: Igual que al añadir favorito

#### Obtener Favoritos de Usuario
- **URL**: `/api/favorite-games/user/{user_id}`
- **Método**: `GET`
- **Descripción**: Obtiene todos los juegos favoritos de un usuario

### Integración con RAWG

#### Buscar Juegos en RAWG
- **URL**: `/api/rawg/search`
- **Método**: `GET`
- **Descripción**: Busca juegos en la API de RAWG
- **Parámetros**: `query` (string), `page` (int, default=1), `page_size` (int, default=20)

#### Obtener Detalles de Juego RAWG
- **URL**: `/api/rawg/game/{game_id}`
- **Método**: `GET`
- **Descripción**: Obtiene detalles de un juego específico de RAWG

#### Añadir Juego de RAWG a Favoritos
- **URL**: `/api/rawg/add-to-favorites`
- **Método**: `POST`
- **Descripción**: Añade un juego de RAWG a los favoritos de un usuario
- **Parámetros**: `user_id` (int), `game_id` (int)

#### Obtener Juegos Populares de RAWG
- **URL**: `/api/rawg/trending`
- **Método**: `GET`
- **Descripción**: Obtiene juegos populares o en tendencia de RAWG
- **Parámetros**: `page` (int, default=1), `page_size` (int, default=20), `max_pages` (int, default=1)

#### Obtener Juegos Aleatorios de RAWG
- **URL**: `/api/rawg/random`
- **Método**: `GET`
- **Descripción**: Obtiene una selección aleatoria de juegos de RAWG
- **Parámetros**: `count` (int, default=10)

### Sistema de Recomendaciones

#### Recomendaciones para Usuario
- **URL**: `/api/recommendations/for-user/{user_id}`
- **Método**: `GET`
- **Descripción**: Genera recomendaciones para un usuario específico
- **Parámetros**: `max_price` (float, opcional), `limit` (int, default=10)
- **Respuesta**: Lista de juegos recomendados con puntuación de relevancia

#### Recomendaciones por Géneros
- **URL**: `/api/recommendations/by-genres`
- **Método**: `GET`
- **Descripción**: Genera recomendaciones basadas en géneros específicos
- **Parámetros**: `genres` (array de strings), `max_price` (float, opcional), `limit` (int, default=10)
- **Respuesta**: Lista de juegos recomendados con puntuación de relevancia

## Ejemplos de Uso

### Flujo de Usuario Típico

1. Registrarse o iniciar sesión:
   ```
   POST /api/auth/register
   // o
   POST /api/auth/login-json
   ```

2. Buscar juegos en RAWG:
   ```
   GET /api/rawg/search?query=hollow%20knight
   ```

3. Marcar un juego como favorito:
   ```
   POST /api/rawg/add-to-favorites?user_id=1&game_id=5
   ```

4. Obtener recomendaciones:
   ```
   GET /api/recommendations/for-user/1?max_price=20&limit=5
   ```

### Ejemplo de Respuesta de Recomendación

```json
[
  {
    "id": 123,
    "nombre": "Hollow Knight",
    "generos": ["Platformer", "Metroidvania", "Action"],
    "precio": 14.99,
    "descripcion": "Un juego de aventuras en 2D que tiene lugar en un vasto mundo interconectado.",
    "imagen_principal": "https://example.com/hollow_knight.jpg",
    "puntuacion": 0.85
  },
  {
    "id": 456,
    "nombre": "Celeste",
    "generos": ["Platformer", "Precision", "Story-Rich"],
    "precio": 19.99,
    "descripcion": "Ayuda a Madeline a sobrevivir a su viaje interno escalando la montaña Celeste.",
    "imagen_principal": "https://example.com/celeste.jpg",
    "puntuacion": 0.78
  }
]
```

### Ejemplo de Autenticación

```json
// Solicitud
POST /api/auth/login-json
{
  "email": "user@example.com",
  "password": "password123"
}

// Respuesta
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nick": "username",
    "email": "user@example.com"
  }
}
```

### Ejemplo de Registro

```json
// Solicitud
POST /api/auth/register
{
  "nick": "username",
  "email": "user@example.com",
  "password": "password123"
}

// Respuesta
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nick": "username",
    "email": "user@example.com"
  }
}
```

## Notas para el Frontend

Al diseñar el frontend, considera:

1. Autenticación de usuarios
   - Usar los endpoints de `/api/auth/` para login
   - Almacenar el token JWT en localStorage o cookies seguras
   - Incluir el token en el header `Authorization: Bearer {token}` para endpoints protegidos
2. Pantallas de descubrimiento y búsqueda de juegos 
3. Perfil de usuario con juegos favoritos
4. Sistema de recomendaciones destacado
5. Interfaz para ver detalles de juegos
6. Filtros por géneros, precio y otros atributos
7. Navegación intuitiva entre las diferentes secciones

El frontend debe comunicarse con estos endpoints para proporcionar una experiencia completa de recomendación de juegos indies.
