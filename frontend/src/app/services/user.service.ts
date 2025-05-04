import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
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
    const userId = this.authService.getCurrentUserId();
    return this.http.post('/api/rawg/add-to-favorites', { user_id: userId, game_id: gameId });
  }
  
  /**
   * Alias para addGameToFavorites para mantener consistencia de nomenclatura
   */
  addFavorite(gameId: number): Observable<any> {
    return this.addGameToFavorites(gameId);
  }
  
  /**
   * Remueve un juego de los favoritos del usuario
   * @param gameId ID del juego a remover de favoritos
   * @returns Observable con la respuesta del servidor
   */
  removeGameFromFavorites(gameId: number): Observable<any> {
    const userId = this.authService.getCurrentUserId();
    return this.http.delete('/api/favorite-games/remove-favorite', {
      body: { usuario_id: userId, juego_id: gameId }
    });
  }
  
  /**
   * Alias para removeGameFromFavorites para mantener consistencia de nomenclatura
   */
  removeFavorite(gameId: number): Observable<any> {
    return this.removeGameFromFavorites(gameId);
  }
  
  /**
   * Verifica si un juego está en los favoritos del usuario
   * @param gameId ID del juego a verificar
   * @returns Observable con la respuesta del servidor
   */
  checkIfGameIsFavorite(gameId: number): Observable<boolean> {
    const userId = this.authService.getCurrentUserId();
    // Esta funcionalidad parece que no existe, tendríamos que implementarla comparando
    // con la lista completa de favoritos
    return this.getFavoriteGames().pipe(
      map(favorites => favorites.some(fav => fav.id === gameId))
    );
  }

  /**
   * Obtiene todos los juegos favoritos del usuario actual
   * @returns Observable con la lista de juegos favoritos
   */
  getFavoriteGames(): Observable<any[]> {
    const userId = this.authService.getCurrentUserId();
    return this.http.get<any[]>(`/api/favorite-games/user/${userId}`);
  }
  
  /**
   * Alias para getFavoriteGames para mantener consistencia de nomenclatura
   */
  getFavorites(): Observable<any[]> {
    return this.getFavoriteGames();
  }
}
