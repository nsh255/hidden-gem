import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  
  constructor(private http: HttpClient) { }
  
  /**
   * Añade un juego a los favoritos del usuario actual
   * @param gameId ID del juego a añadir a favoritos
   * @returns Observable con la respuesta del servidor
   */
  addGameToFavorites(gameId: number): Observable<any> {
    return this.http.post('/api/rawg/add-to-favorites', { game_id: gameId });
  }
  
  /**
   * Remueve un juego de los favoritos del usuario
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
    return this.http.get<boolean>(`/api/favorite-games/check/${gameId}`);
  }
}
