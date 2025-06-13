# Autenticación en la API de Hidden Gem

Este documento describe el sistema de autenticación utilizado en la API de Hidden Gem.

## Visión General

Hidden Gem utiliza autenticación basada en tokens JWT (JSON Web Tokens) para proteger los endpoints de la API. Este enfoque proporciona una solución stateless que funciona bien para APIs RESTful.

## Flujo de Autenticación

1. **Registro de Usuario**: El usuario se registra proporcionando email, nombre de usuario y contraseña
2. **Inicio de Sesión**: El usuario proporciona sus credenciales y recibe un token JWT
3. **Acceso a Recursos Protegidos**: El usuario incluye el token en el encabezado Authorization para acceder a endpoints protegidos

## Endpoints de Autenticación

### Registro

```
POST /api/auth/register
```

**Cuerpo de la solicitud:**
```json
{
  "nick": "usuario_ejemplo",
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

**Respuesta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nick": "usuario_ejemplo",
    "email": "usuario@ejemplo.com"
  }
}
```

### Inicio de Sesión (JSON)

```
POST /api/auth/login-json
```

**Cuerpo de la solicitud:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

**Respuesta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nick": "usuario_ejemplo",
    "email": "usuario@ejemplo.com"
  }
}
```

### Inicio de Sesión (Form)

```
POST /api/auth/login
```

**Cuerpo de la solicitud (form-data):**
```
username: usuario@ejemplo.com
password: contraseña_segura
```

**Respuesta:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nick": "usuario_ejemplo",
    "email": "usuario@ejemplo.com"
  }
}
```

## Estructura del Token JWT

Los tokens JWT generados contienen la siguiente información:

- **sub**: Email del usuario (subject)
- **user_id**: ID del usuario en la base de datos
- **exp**: Timestamp de expiración del token

## Uso del Token

Para acceder a endpoints protegidos, incluye el token en el encabezado de autorización:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Seguridad

- Las contraseñas se almacenan hasheadas utilizando bcrypt
- Los tokens JWT están firmados con una clave secreta configurada en las variables de entorno
- Los tokens tienen una duración limitada (30 minutos por defecto)
- Se utiliza HTTPS para todas las comunicaciones en producción

## Ejemplo de Código Cliente

### JavaScript (Fetch API)

```javascript
// Iniciar sesión
async function login(email, password) {
  const response = await fetch('https://api.hidden-gem.com/api/auth/login-json', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
}

// Hacer una solicitud autenticada
async function getFavorites(userId) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(`https://api.hidden-gem.com/api/favorite-games/user/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
}
```

## Recomendaciones

1. **Siempre utiliza HTTPS** en entornos de producción
2. **Almacena tokens de forma segura** en el cliente (HttpOnly cookies para aplicaciones web)
3. **Implementa un sistema de renovación de tokens** para sesiones más largas
4. **Valida siempre los tokens** en el servidor antes de permitir el acceso a recursos protegidos