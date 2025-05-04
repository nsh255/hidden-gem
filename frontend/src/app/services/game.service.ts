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

  /**
   * Obtiene recomendaciones personalizadas para el usuario actual
   * @returns Observable con la lista de juegos recomendados personalizados
   */
  getPersonalized(): Observable<RecommendedGame[]> {
    return this.http.get<RecommendedGame[]>('/recommendations/personalized');
  }

  /**
   * Obtiene los detalles de un juego específico por su ID
   * @param id ID del juego a consultar
   * @returns Observable con los detalles del juego
   */
  getGameById(id: string): Observable<GameDetails> {
    return this.http.get<GameDetails>(`/api/rawg/game/${id}`);
  }
}
