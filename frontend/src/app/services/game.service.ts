import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

// Interfaz para los juegos recomendados
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
export class GameService {
  
  constructor(private http: HttpClient) { }
  
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
    // Preparar los parámetros para la petición
    let params = new HttpParams();
    
    // Añadir géneros (pueden ser múltiples, así que se añaden uno por uno)
    genres.forEach(genre => {
      params = params.append('genres', genre);
    });
    
    // Añadir precio máximo si se proporciona
    if (maxPrice !== undefined) {
      params = params.append('max_price', maxPrice.toString());
    }
    
    // Añadir límite
    params = params.append('limit', limit.toString());
    
    // Realizar la petición GET
    return this.http.get<RecommendedGame[]>('/api/recommendations/by-genres', { params });
  }
}
