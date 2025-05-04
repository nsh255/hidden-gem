import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RecommendedGame } from './game.service';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class RecommendationService {
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
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
   * @returns Observable con la lista de juegos recomendados personalizados
   */
  getPersonalized(): Observable<RecommendedGame[]> {
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      throw new Error('Usuario no autenticado');
    }
    return this.http.get<RecommendedGame[]>(`/api/recommendations/for-user/${userId}`);
  }
}
