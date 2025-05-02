# HiddenGem API

## Introducción

La API de HiddenGem está diseñada para ayudar a los amantes de los videojuegos a descubrir joyas escondidas y títulos indie de alta calidad que podrían haber pasado desapercibidos. Nuestra plataforma utiliza una combinación de web scraping, integración con APIs externas y algoritmos de recomendación para ofrecer sugerencias personalizadas.

## Autenticación

La API utiliza autenticación basada en tokens JWT (JSON Web Tokens). Para acceder a la mayoría de los endpoints, necesitarás:

1. Registrarte para obtener una cuenta
2. Iniciar sesión para obtener un token
3. Incluir el token en el encabezado de autorización de tus solicitudes

Ejemplo:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Flujo de trabajo típico

1. **Registro e inicio de sesión**: Crea una cuenta y obtén un token de autenticación
2. **Exploración de juegos**: Navega por nuestra base de datos de juegos o busca juegos específicos
3. **Obtención de recomendaciones**: Recibe sugerencias personalizadas basadas en tus preferencias
4. **Descubrimiento de joyas escondidas**: Encuentra juegos bien valorados pero poco conocidos

## Limitaciones de tasa

Para garantizar la calidad del servicio, aplicamos los siguientes límites:

- 100 solicitudes por minuto para usuarios autenticados
- 10 solicitudes por minuto para usuarios no autenticados

## Modo Administrador

Para propósitos de desarrollo y pruebas, hemos habilitado endpoints administrativos que no requieren autenticación:

- `/api/admin/games`: Acceso a la base de datos de juegos sin autenticación
- `/api/admin/scraper`: Control del scraper sin restricciones
- `/api/admin/recommendations/random`: Sistema de recomendación aleatorio
- `/api/admin/rawg`: Acceso a la integración con RAWG API sin autenticación

Estos endpoints están destinados únicamente para pruebas internas y no deben usarse en entornos de producción.

## Notas sobre el scraper

El endpoint de scraping está diseñado para actualizar nuestra base de datos y no debe ser llamado frecuentemente. Su uso está restringido principalmente a procesos internos.

La información recopilada por el scraper incluye:
- Datos básicos del juego (título, precio, descripción)
- Categorías (géneros, tags)
- Información de desarrollo (desarrolladores, publishers)
- Identificadores (app_id, URLs)

## Integración con RAWG

Nuestra plataforma se integra con la API de RAWG para proporcionar información detallada sobre videojuegos. Los datos obtenidos se formatean para adaptarse a nuestro modelo de datos.
