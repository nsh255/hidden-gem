import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

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

@Injectable({
  providedIn: 'root'
})
export class GameService {
  
  constructor(private http: HttpClient) { }
  
  /**
   * Obtiene los detalles de un juego específico por su ID
   * @param id ID del juego a consultar
   * @returns Observable con los detalles del juego
   */
  getGameById(id: string): Observable<GameDetails> {
    return this.http.get<GameDetails>(`/api/rawg/game/${id}`);
  }

  /**
   * Obtiene una lista de juegos con paginación
   * @param page Número de página
   * @param pageSize Tamaño de la página
   * @returns Observable con la respuesta paginada de juegos
   */
  getGames(page: number = 1, pageSize: number = 12): Observable<PaginatedGamesResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    return this.http.get<PaginatedGamesResponse>('/api/games', { params });
  }

  /**
   * Busca juegos por texto
   * @param query Texto de búsqueda
   * @returns Observable con la lista de juegos encontrados
   */
  searchGames(query: string): Observable<GameSummary[]> {
    const params = new HttpParams().set('query', query);
    return this.http.get<GameSummary[]>('/api/rawg/search', { params });
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
   * @param gameId ID del juego para el que se buscan similares
   * @param limit Número máximo de juegos a devolver
   * @returns Observable con la lista de juegos similares
   */
  getSimilarGames(gameId: number, limit: number = 4): Observable<GameSummary[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<GameSummary[]>(`/api/games/${gameId}/similar`, { params });
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
  getTrendingGames(page: number = 1, pageSize: number = 20): Observable<any> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    return this.http.get<any>('/api/rawg/trending', { params });
  }

  /**
   * Obtiene juegos aleatorios
   * @param count Número de juegos a obtener
   * @returns Observable con la lista de juegos aleatorios
   */
  getRandomGames(count: number = 10): Observable<any> {
    const params = new HttpParams().set('count', count.toString());
    return this.http.get<any>('/api/rawg/random', { params });
  }
}
