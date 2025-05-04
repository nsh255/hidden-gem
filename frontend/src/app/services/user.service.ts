import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  
  constructor(private http: HttpClient, private authService: AuthService) { }
  
  /**
   * Añade un juego a los favoritos del usuario actual
   * @param gameId ID del juego a añadir a favoritos
   * @returns Observable con la respuesta del servidor
   */
  addGameToFavorites(gameId: number): Observable<any> {
    // Mantenemos este método para compatibilidad con código existente
    return this.http.post('/api/rawg/add-to-favorites', { game_id: gameId });
  }
  
  /**
   * Añade un juego a favoritos usando el nuevo endpoint
   * @param gameId ID del juego a añadir a favoritos
   * @returns Observable con la respuesta del servidor
   */
  addFavorite(gameId: number): Observable<any> {
    return this.http.post('/api/users/favorites', { game_id: gameId });
  }
  
  /**
   * @deprecated Use removeFavorite instead
   * Remueve un juego de los favoritos del usuario (endpoint antiguo)
   * @param gameId ID del juego a remover de favoritos
   * @returns Observable con la respuesta del servidor
   */
  removeGameFromFavorites(gameId: number): Observable<any> {
    return this.http.delete('/api/favorite-games/remove-favorite', {
      body: { juego_id: gameId }
    });
  }
  
  /**
   * Verifica si un juego está en los favoritos del usuario
   * @param gameId ID del juego a verificar
   * @returns Observable con la respuesta del servidor
   */
  checkIfGameIsFavorite(gameId: number): Observable<boolean> {
    return this.http.get<boolean>(`/api/users/favorites/check/${gameId}`);
  }

  /**
   * @deprecated Use getFavorites instead
   * Obtiene todos los juegos favoritos del usuario actual (endpoint antiguo)
   * @returns Observable con la lista de juegos favoritos
   */
  getFavoriteGames(): Observable<any[]> {
    return this.http.get<any[]>('/api/favorite-games/current-user');
  }

  /**
   * Obtiene los juegos favoritos del usuario actual con datos completos
   * @returns Observable con la lista de juegos favoritos procesados
   */
  getFavorites(): Observable<any[]> {
    return this.http.get<any[]>('/api/users/favorites');
  }

  /**
   * Elimina un juego de los favoritos del usuario
   * @param gameId ID del juego a eliminar de favoritos
   * @returns Observable con la respuesta del servidor
   */
  removeFavorite(gameId: number): Observable<any> {
    return this.http.delete(`/api/users/favorites/${gameId}`);
  }
}
