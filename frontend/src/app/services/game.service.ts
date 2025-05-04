import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

// Interfaz para la respuesta paginada de juegos
export interface PaginatedGamesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: GameSummary[];
}

// Interfaz para el resumen de un juego (listado)
export interface GameSummary {
  id: number;
  name: string;
  background_image: string;
  released: string;
  rating: number;
  genres: {id: number, name: string}[];
  price?: number;
}

// Interfaz para los detalles de un juego
export interface GameDetails {
  id: number;
  name: string;
  background_image: string;
  description: string;
  released: string;
  rating: number;
  genres: {id: number, name: string}[];
  tags: {id: number, name: string}[];
  platforms: {platform: {id: number, name: string}}[];
  stores: {store: {id: number, name: string, domain: string}}[];
  price?: number;
  screenshots?: {id: number, image: string}[];
  // Otros campos que devuelva la API de RAWG
}

export interface GameReview {
  id: number;
  user_id: number;
  user_name: string; 
  game_id: number;
  rating: number;
  content: string;
  created_at: string;
}

// Interfaz para juegos de Steam
export interface SteamGame {
  id: number;
  nombre: string;
  generos: string[];
  precio: number;
  descripcion: string;
  tags: string[];
  imagen_principal: string;
}

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private apiUrl = '/api/games';
  
  constructor(private http: HttpClient) { }
  
  /**
   * Obtiene los detalles de un juego específico por su ID
   * @param id ID del juego a consultar
   * @returns Observable con los detalles del juego
   */
  getGameById(id: string): Observable<GameDetails> {
    // Intentar primero con RAWG
    return this.http.get<GameDetails>(`/api/rawg/game/${id}`).pipe(
      catchError(error => {
        console.warn(`Error obteniendo el juego de RAWG (ID: ${id})`, error);
        
        // Si falla, intentar obtener el juego de Steam como fallback
        return this.getSteamGameById(parseInt(id)).pipe(
          catchError(steamError => {
            console.error(`Error obteniendo el juego de Steam también (ID: ${id})`, steamError);
            // Reenviar el error original si ambos fallan
            throw error;
          })
        );
      })
    );
  }

  /**
   * Obtiene los detalles de un juego de Steam por su ID
   * @param id ID del juego de Steam
   * @returns Observable con los detalles del juego 
   */
  getSteamGameById(id: number): Observable<GameDetails> {
    console.debug('Fetching Steam game with ID:', id);
    
    return this.http.get<any>(`/api/steam-games/${id}`).pipe(
      map(steamGame => {
        // Convert the Steam game format to GameDetails format
        return {
          id: steamGame.id,
          name: steamGame.nombre,
          background_image: steamGame.imagen_principal,
          description: steamGame.descripcion || '',
          released: '', // Steam doesn't provide this
          rating: 0,    // No rating for Steam games
          genres: steamGame.generos?.map((name: string, index: number) => ({
            id: index + 1, // Generate artificial IDs
            name
          })) || [],
          tags: steamGame.tags?.map((name: string, index: number) => ({
            id: index + 1,
            name
          })) || [],
          platforms: [],
          stores: [],
          price: steamGame.precio
        };
      }),
      catchError(error => {
        console.error('Error fetching Steam game:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Convierte un juego de Steam al formato GameDetails
   * @param steamGame Juego de Steam a convertir
   * @returns El juego en formato GameDetails
   */
  private convertSteamGameToGameDetails(steamGame: SteamGame): GameDetails {
    return {
      id: steamGame.id,
      name: steamGame.nombre,
      background_image: steamGame.imagen_principal,
      description: steamGame.descripcion || '',
      released: '',  // Steam no proporciona esta información
      rating: 0,     // No tenemos rating para juegos de Steam
      genres: steamGame.generos?.map((name, index) => ({
        id: index + 1,  // Generamos IDs artificiales
        name
      })) || [],
      tags: steamGame.tags?.map((name, index) => ({
        id: index + 1,
        name
      })) || [],
      platforms: [],  // No tenemos esta información para juegos de Steam
      stores: [],     // No tenemos esta información para juegos de Steam
      price: steamGame.precio
    };
  }

  /**
   * Obtiene una lista de juegos con paginación
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la respuesta paginada de juegos
   */
  getGames(page: number = 1, pageSize: number = 12): Observable<PaginatedGamesResponse> {
    return this.getSteamGames(page, pageSize).pipe(
      map(steamGames => this.convertSteamGamesToPaginatedResponse(steamGames, page, pageSize)),
      catchError(error => {
        console.error('Error fetching Steam games:', error);
        // Fallback to empty response
        return of({
          count: 0,
          next: null,
          previous: null,
          results: []
        });
      })
    );
  }

  /**
   * Obtiene juegos de Steam
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la lista de juegos de Steam
   */
  private getSteamGames(page: number = 1, pageSize: number = 12): Observable<SteamGame[]> {
    const skip = (page - 1) * pageSize;
    return this.http.get<SteamGame[]>('/api/steam-games/', {
      params: {
        skip: skip.toString(),
        limit: pageSize.toString()
      }
    });
  }

  /**
   * Convierte juegos de Steam al formato paginado esperado por la UI
   */
  private convertSteamGamesToPaginatedResponse(
    steamGames: SteamGame[],
    currentPage: number,
    pageSize: number
  ): PaginatedGamesResponse {
    // Asumimos que hay una página siguiente si tenemos el número exacto de items por página
    const hasNextPage = steamGames.length === pageSize;
    // Asumimos que hay una página anterior si no estamos en la primera página
    const hasPreviousPage = currentPage > 1;

    // Mapear juegos de Steam al formato GameSummary
    const gameSummaries: GameSummary[] = steamGames.map(game => ({
      id: game.id,
      name: game.nombre,
      background_image: game.imagen_principal,
      released: '', // Steam no proporciona esta información, así que la dejamos vacía
      rating: 0, // Podríamos calcular un rating basado en algo si fuera necesario
      genres: game.generos.map((genreName, index) => ({
        id: index + 1, // Generamos IDs artificiales
        name: genreName
      })),
      price: game.precio
    }));

    return {
      count: steamGames.length, // Esto es solo para la página actual, idealmente deberíamos tener un count total
      next: hasNextPage ? `/api/steam-games/?skip=${(currentPage) * pageSize}&limit=${pageSize}` : null,
      previous: hasPreviousPage ? `/api/steam-games/?skip=${(currentPage - 2) * pageSize}&limit=${pageSize}` : null,
      results: gameSummaries
    };
  }

  /**
   * Busca juegos por texto
   * @param query Texto de búsqueda
   * @returns Observable con la lista de juegos encontrados
   */
  searchGames(query: string): Observable<GameSummary[]> {
    const params = new HttpParams().set('query', query);
    return this.http.get<any>('/api/rawg/search', { params }).pipe(
      map(response => {
        if (response && response.results) {
          return response.results;
        }
        return [];
      }),
      catchError(error => {
        console.error('Error searching games:', error);
        return of([]);
      })
    );
  }

  /**
   * Obtiene juegos por género
   * @param genreId ID del género
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la respuesta paginada de juegos
   */
  getGamesByGenre(genreId: number, page: number = 1, pageSize: number = 12): Observable<PaginatedGamesResponse> {
    const params = new HttpParams()
      .set('genre', genreId.toString())
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    return this.http.get<PaginatedGamesResponse>('/api/games', { params });
  }

  /**
   * Obtiene la lista de géneros disponibles
   * @returns Observable con la lista de géneros
   */
  getGenres(): Observable<{id: number, name: string}[]> {
    return this.http.get<{id: number, name: string}[]>('/api/genres');
  }

  /**
   * Obtiene juegos similares a un juego específico
   */
  getSimilarGames(gameId: number, page: number = 1): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${gameId}/similar?page=${page}&limit=4`);
  }

  /**
   * Obtiene los screenshots de un juego
   * @param gameId ID del juego
   * @returns Observable con la lista de URLs de screenshots
   */
  getGameScreenshots(gameId: number): Observable<{id: number, image: string}[]> {
    return this.http.get<{id: number, image: string}[]>(`/api/rawg/game/${gameId}/screenshots`);
  }

  /**
   * Obtiene las reseñas de un juego específico
   * @param gameId ID del juego
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con las reseñas del juego
   */
  getGameReviews(gameId: number, page: number = 1, pageSize: number = 10): Observable<{
    count: number,
    results: GameReview[]
  }> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    return this.http.get<{count: number, results: GameReview[]}>(`/api/games/${gameId}/reviews`, { params });
  }

  /**
   * Publica una reseña para un juego
   * @param gameId ID del juego
   * @param rating Puntuación del 1 al 5
   * @param content Contenido textual de la reseña
   * @returns Observable con la reseña creada
   */
  addGameReview(gameId: number, rating: number, content: string): Observable<GameReview> {
    return this.http.post<GameReview>(`/api/games/${gameId}/reviews`, {
      rating,
      content
    });
  }

  /**
   * Obtiene juegos filtrados por precio y otros criterios
   * @param filters Objeto con los filtros a aplicar
   * @returns Observable con la respuesta paginada de juegos
   */
  getFilteredGames(filters: {
    min_price?: number,
    max_price?: number,
    genres?: number[],
    platforms?: number[],
    sort_by?: string,
    page?: number,
    page_size?: number
  }): Observable<PaginatedGamesResponse> {
    let params = new HttpParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => {
          params = params.append(key, v.toString());
        });
      } else if (value !== undefined) {
        params = params.append(key, value.toString());
      }
    });
    
    return this.http.get<PaginatedGamesResponse>('/api/games/filter', { params });
  }

  /**
   * Obtiene juegos en tendencia
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la lista de juegos en tendencia
   */
  getTrendingGames(page: number, pageSize: number): Observable<{ results: GameSummary[] }> {
    console.log('Fetching trending games, page:', page, 'size:', pageSize);
    return this.http.get<{ results: GameSummary[] }>(`/api/rawg/trending`, {
      params: { page: page.toString(), page_size: pageSize.toString() },
    }).pipe(
      catchError(error => {
        console.error('Error fetching trending games:', error);
        // Return a valid empty response to prevent UI errors
        return of({ results: [] });
      })
    );
  }

  /**
   * Obtiene juegos aleatorios
   * @param count Número de juegos a obtener
   * @returns Observable con la lista de juegos aleatorios
   */
  getRandomGames(count: number = 10): Observable<any> {
    // Add a truly unique identifier to defeat caching
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Log the request for debugging
    console.log(`Fetching random games with unique ID: ${uniqueId}`);
    
    const params = new HttpParams()
      .set('count', count.toString())
      .set('_t', uniqueId);
    
    return this.http.get<any>('/api/rawg/random', { 
      params, 
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      } 
    }).pipe(
      catchError(error => {
        console.error('Error fetching random games:', error);
        return of({ count: 0, results: [] });
      })
    );
  }

  /**
   * Obtiene juegos aleatorios con paginación
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la lista de juegos aleatorios
   */
  getRandomGamesWithPage(page: number, pageSize: number): Observable<{ results: GameSummary[] }> {
    // Create a unique identifier to prevent caching
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return this.http.get<{ results: GameSummary[] }>('/api/rawg/random', {
      params: { 
        count: pageSize.toString(),
        page: page.toString(),
        _t: uniqueId
      },
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      } 
    }).pipe(
      catchError(error => {
        console.error('Error fetching random games with pagination:', error);
        return of({ results: [] });
      })
    );
  }

  /**
   * Obtiene juegos aleatorios filtrados por género
   * @param genre Género de juegos a obtener
   * @param count Número de juegos a obtener
   * @returns Observable con lista de juegos del género especificado
   */
  getRandomGamesByGenre(genre: string, count: number = 3): Observable<any[]> {
    // Crear un identificador único para evitar caché
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Parámetros de la solicitud
    const params = new HttpParams()
      .set('genre', genre)
      .set('count', count.toString())
      .set('random', 'true')
      .set('_t', uniqueId);
    
    // Hacer la solicitud al endpoint
    return this.http.get<any>('/api/games/by-genre', { 
      params, 
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      } 
    }).pipe(
      map(response => {
        if (response && response.results) {
          return response.results;
        }
        return [];
      }),
      catchError(error => {
        console.error(`Error fetching games by genre ${genre}:`, error);
        return of([]);
      })
    );
  }

  /**
   * Obtiene juegos aleatorios filtrados por múltiples géneros
   * @param genres Lista de géneros de juegos a obtener
   * @param count Número de juegos a obtener
   * @returns Observable con lista de juegos de los géneros especificados
   */
  getRandomGamesByGenres(genres: string[], count: number = 5): Observable<any[]> {
    // Crear un identificador único para evitar caché
    const uniqueId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Convertir géneros a parámetros de consulta
    let params = new HttpParams()
      .set('count', count.toString())
      .set('random', 'true')
      .set('_t', uniqueId);
    
    // Añadir cada género como un parámetro separado
    genres.forEach(genre => {
      params = params.append('genres', genre);
    });
    
    // Usar el endpoint de recomendaciones por géneros que ya existe
    return this.http.get<any>('/api/recommendations/by-genres', {
      params,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }).pipe(
      catchError(error => {
        console.error(`Error fetching random games by genres: ${genres.join(', ')}`, error);
        return of([]);
      })
    );
  }
}
