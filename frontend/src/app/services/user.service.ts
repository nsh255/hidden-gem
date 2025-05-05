import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl; // Should point to your backend, e.g., 'http://localhost:8000'
  private favoriteApiUrl = '/api/favorite-games';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  /**
   * Obtiene información del perfil del usuario
   * @returns Observable con los datos del usuario
   */
  getUserProfile(): Observable<any> {
    return this.http.get(`${this.apiUrl}/users/me`);
  }

  /**
   * Actualiza el perfil del usuario
   * @param userData Datos a actualizar (nick, precio_max)
   * @returns Observable con la respuesta
   */
  updateUserProfile(userData: { nick?: string; precio_max?: number }): Observable<any> {
    console.debug('Updating user profile with data:', userData);
    
    // Use the AuthService to get the token consistently
    const token = this.authService.getToken();
    
    if (!token) {
      console.error('No authentication token found');
      return throwError(() => new Error('User not authenticated'));
    }
    
    // Create headers with the authorization token
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
    
    return this.http.patch(`${this.apiUrl}/users/me`, userData, { headers }).pipe(
      tap(response => {
        console.debug('Profile update successful, updating local data');
        // Update user data in AuthService
        this.authService.updateUserData(userData);
      }),
      catchError(error => {
        console.error('Error updating user profile:', error);
        if (error.status === 401) {
          return throwError(() => new Error('Sesión expirada. Por favor, inicia sesión nuevamente.'));
        }
        return throwError(() => new Error('Error al actualizar el perfil'));
      })
    );
  }

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
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      return throwError(() => new Error('User not authenticated'));
    }
    
    // Use the favoriteApiUrl variable that already includes /api prefix
    return this.http.post(`${this.apiUrl}/api/favorite-games/add-favorite`, {
      usuario_id: userId,
      juego_id: gameId
    });
  }
  
  /**
   * Añade un juego de Steam a los favoritos del usuario actual
   * @param gameId ID del juego de Steam
   * @param gameData Datos completos del juego Steam para guardar
   * @returns Observable con la respuesta del servidor
   */
  addSteamGameToFavorites(gameId: number, gameData: any): Observable<any> {
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      return throwError(() => new Error('User not authenticated'));
    }
    
    // Create a model compatible with our database structure
    const steamGameData = {
      usuario_id: userId,
      juego_id: gameId,
      // Include game data so backend doesn't need to fetch from RAWG
      game_data: {
        id: gameId,
        nombre: gameData.name,
        imagen: gameData.imageUrl,
        descripcion: gameData.description || '',
        generos: gameData.genres || [],
        tags: []
      },
      is_steam_game: true
    };
    
    // Use a special endpoint or parameter to indicate this is a Steam game
    return this.http.post(`${this.apiUrl}/api/favorite-games/add-steam-favorite`, steamGameData);
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
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      return throwError(() => new Error('User not authenticated'));
    }
    
    // Use the favoriteApiUrl variable that already includes /api prefix
    return this.http.delete(`${this.apiUrl}/api/favorite-games/remove-favorite`, {
      body: {
        usuario_id: userId,
        juego_id: gameId
      }
    });
  }
  
  /**
   * Verifica si un juego está en los favoritos del usuario
   * @param gameId ID del juego a verificar
   * @returns Observable con la respuesta del servidor
   */
  checkIfGameIsFavorite(gameId: number): Observable<boolean> {
    const userId = this.authService.getCurrentUserId();
    
    // Si no hay usuario autenticado, no puede ser favorito
    if (!userId) {
      return of(false);
    }
    
    // Implementación mejorada: hacemos una petición específica para verificar si es favorito
    return this.http.get<boolean>(`${this.apiUrl}/api/favorite-games/check/${userId}/${gameId}`).pipe(
      catchError(error => {
        console.error('Error al verificar estado de favorito:', error);
        
        // Si hay error (como que el endpoint no existe), intentamos con el método alternativo
        return this.getFavoriteGames().pipe(
          map(favorites => favorites.some(fav => fav.id === gameId)),
          catchError(() => of(false))
        );
      })
    );
  }

  /**
   * Obtiene todos los juegos favoritos del usuario actual
   * @returns Observable con la lista de juegos favoritos
   */
  getFavoriteGames(): Observable<any[]> {
    const userId = this.authService.getCurrentUserId();
    if (!userId) return new Observable(observer => observer.next([]));
    
    return this.http.get<any[]>(`${this.apiUrl}/api/favorite-games/user/${userId}`);
  }
  
  /**
   * Alias para getFavoriteGames para mantener consistencia de nomenclatura
   */
  getFavorites(): Observable<any[]> {
    return this.getFavoriteGames();
  }
}
