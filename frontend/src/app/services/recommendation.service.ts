import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
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
  
  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private gameService: GameService
  ) { }
  
  /**
   * Obtiene recomendaciones de juegos basadas en géneros específicos
   * @param genres Lista de géneros para filtrar
   * @param maxPrice Precio máximo (opcional)
   * @param limit Número máximo de resultados (opcional, por defecto 10)
   * @returns Observable con la lista de juegos recomendados
   */
  getRecommendationsByGenres(
    genres: string[], 
    maxPrice?: number, 
    limit: number = 10
  ): Observable<RecommendedGame[]> {
    let params = new HttpParams();
    
    genres.forEach(genre => {
      params = params.append('genres', genre);
    });
    
    if (maxPrice !== undefined) {
      params = params.append('max_price', maxPrice.toString());
    }
    
    params = params.append('limit', limit.toString());
    
    return this.http.get<RecommendedGame[]>('/api/recommendations/by-genres', { params });
  }

  /**
   * Obtiene recomendaciones personalizadas para el usuario actual
   * Este endpoint no existe realmente, así que simulamos con juegos aleatorios
   * @returns Observable con la lista de juegos recomendados personalizados
   */
  getPersonalized(): Observable<RecommendedGame[]> {
    // Como no existe un endpoint real, usamos juegos aleatorios como sustituto
    return this.gameService.getRandomGames(5).pipe(
      map(response => this.mapToRecommendedGames(response.results)),
      catchError(error => {
        console.error('Error obteniendo recomendaciones:', error);
        return of([]);
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
      nombre: game.name,
      generos: game.genres?.map((g: { name: any; }) => g.name) || [],
      precio: game.price || 19.99,  // RAWG no proporciona precios, asignamos uno por defecto
      descripcion: game.description_raw || '',
      imagen_principal: game.background_image || '',
      puntuacion: game.rating / 10 || 0.7  // Convertimos de escala 0-5 a 0-1
    }));
  }
}
