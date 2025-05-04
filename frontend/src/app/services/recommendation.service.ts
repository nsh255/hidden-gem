import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, map, retry } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { GameService } from './game.service';

// Mover la interfaz aquí para evitar dependencias circulares
export interface RecommendedGame {
  id: number;
  nombre: string;
  generos: string[];
  precio: number;
  descripcion: string;
  imagen_principal: string;
  puntuacion: number;
}

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {
  private apiUrl = '/api/recommendations';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private gameService: GameService
  ) { }
  
  /**
   * Obtiene recomendaciones de juegos basadas en géneros específicos
   * @param genres Lista de géneros para filtrar
   * @param excludeIds IDs de juegos a excluir
   * @param limit Número máximo de resultados
   * @param timestamp Timestamp para evitar caché (opcional)
   * @returns Observable con la lista de juegos recomendados
   */
  getRecommendationsByGenres(
    genres: string[], 
    excludeIds?: number[],
    limit?: number,
    timestamp?: number
  ): Observable<RecommendedGame[]> {
    let params = new HttpParams();
    
    genres.forEach(genre => {
      params = params.append('genres', genre);
    });
    
    if (excludeIds && excludeIds.length > 0) {
      excludeIds.forEach(id => {
        params = params.append('exclude', id.toString());
      });
    }
    
    if (limit) {
      params = params.set('limit', limit.toString());
    }
    
    if (timestamp) {
      params = params.set('_t', timestamp.toString());
    } else {
      params = params.set('_t', Date.now().toString());
    }
    
    return this.http.get<RecommendedGame[]>(`${this.apiUrl}/by-genres`, { params })
      .pipe(
        catchError(error => {
          console.error('Error obteniendo recomendaciones por géneros:', error);
          return throwError(() => error);
        })
      );
  }

  /**
   * Obtiene recomendaciones personalizadas para el usuario actual
   * @param page Número de página (inicia en 1)
   * @param pageSize Tamaño de la página
   * @returns Observable con la lista de juegos recomendados
   */
  getPersonalized(page: number = 1, pageSize: number = 10): Observable<RecommendedGame[]> {
    // Construir los parámetros de consulta
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', pageSize.toString());
      
    // Añadir un timestamp para evitar caché
    if (page > 1) {
      params = params.set('_t', Date.now().toString());
    }
    
    return this.http.get<RecommendedGame[]>(`${this.apiUrl}/personalized`, { params })
      .pipe(
        // Retry once in case of network issues
        retry(1),
        catchError((error: HttpErrorResponse) => {
          console.error('Error obteniendo recomendaciones personalizadas:', error);
          
          let errorMessage = 'Error al obtener recomendaciones.';
          
          // Manejar casos específicos
          if (error.status === 401) {
            errorMessage = 'Necesitas iniciar sesión para ver recomendaciones personalizadas.';
          } else if (error.status === 400) {
            if (error.error?.detail?.includes('favoritos')) {
              errorMessage = 'Necesitas añadir juegos a favoritos para obtener recomendaciones.';
            }
          } else if (error.status === 500) {
            errorMessage = 'Error del servidor al procesar recomendaciones. Por favor, inténtalo más tarde.';
          }
          
          // Propagar error con mensaje amigable
          return throwError(() => ({ status: error.status, message: errorMessage, error }));
        })
      );
  }

  /**
   * Obtiene recomendaciones populares
   * @param limit Número máximo de recomendaciones
   * @returns Observable con lista de juegos recomendados
   */
  getPopular(limit: number = 10): Observable<RecommendedGame[]> {
    return this.gameService.getTrendingGames(1, limit).pipe(
      map(response => this.mapToRecommendedGames(response.results)),
      catchError(error => {
        console.error('Error obteniendo juegos populares:', error);
        return of([]);
      })
    );
  }

  /**
   * Obtiene recomendaciones similares a un juego específico
   * @param gameId ID del juego base para las recomendaciones
   * @param limit Número máximo de recomendaciones
   * @returns Observable con lista de juegos recomendados
   */
  getSimilarToGame(gameId: number, limit: number = 5): Observable<RecommendedGame[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<RecommendedGame[]>(`/api/recommendations/similar-to/${gameId}`, { params });
  }

  /**
   * Obtiene recomendaciones basadas en tendencias actuales
   * @param limit Número máximo de recomendaciones
   * @returns Observable con lista de juegos recomendados
   */
  getTrending(limit: number = 10): Observable<RecommendedGame[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<RecommendedGame[]>('/api/recommendations/trending', { params });
  }

  /**
   * Mapea resultados de RAWG a formato RecommendedGame
   * @private
   */
  private mapToRecommendedGames(games: any[]): RecommendedGame[] {
    return games.map(game => ({
      id: game.id,
      nombre: game.name || game.nombre,
      generos: game.genres?.map((g: { name: any; }) => g.name) || game.generos || [],
      precio: game.price || game.precio || 19.99,
      descripcion: game.description_raw || game.descripcion || '',
      imagen_principal: game.background_image || game.imagen_principal || '',
      puntuacion: (game.rating ? game.rating / 10 : 0.7)  // Convertimos de escala 0-5 a 0-1
    }));
  }
}
