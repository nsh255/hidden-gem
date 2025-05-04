import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';router';
import { UserService } from '../../services/user.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

// Interfaz para el juego favorito
interface FavoriteGame {
  id: number;
  name: string;
  imageUrl: string;
  genres: string[];
}

@Component({
  selector: 'app-favorites',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './favorites.component.html',
  styleUrl: './favorites.component.scss'
})
export class FavoritesComponent implements OnInit {
  favoriteGames: FavoriteGame[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  isRemoving: { [key: number]: boolean } = {}; // Para rastrear qué juego se está eliminando

  constructor(private userService: UserService, private router: Router) { }vate router: Router) { }

  ngOnInit(): void {
    this.loadFavoriteGames();
  }

  /**
   * Carga los juegos favoritos del usuario
   */
  loadFavoriteGames(): void {
    this.isLoading = true;
    this.errorMessage = null;

    // Llamamos al nuevo método getFavorites para obtener los favoritos con datos completos de RAWG
    this.userService.getFavorites()
      .pipe(
        catchError(error => {
          console.error('Error al cargar juegos favoritos:', error);
          this.errorMessage = 'No se pudieron cargar tus juegos favoritos. Por favor, inténtalo de nuevo.';
          this.isLoading = false;
          return of([]);
        })
      )
      .subscribe(games => {
        this.favoriteGames = games;
        this.isLoading = false;
      });
  }

  /**
   * Elimina un juego de favoritos
   * @param gameId ID del juego a eliminar
   * @param event Evento del DOM para prevenir propagación
   */
  removeFromFavorites(gameId: number, event: Event): void {
    // Prevenir que el clic se propague a la tarjeta
    event.stopPropagation();
    
    // Marcar el juego como "eliminando"
    this.isRemoving[gameId] = true;

    // Usar el nuevo método del servicio para eliminar de favoritos
    this.userService.removeFavorite(gameId)
      .pipe(
        catchError(error => {
          console.error('Error al eliminar de favoritos:', error);
          this.isRemoving[gameId] = false;
          alert('Error al eliminar de favoritos. Por favor, inténtalo de nuevo.');
          return of(null);
        })
      )
      .subscribe(() => {
        // Eliminar el juego de la lista local para actualizar la UI sin recargar
        this.favoriteGames = this.favoriteGames.filter(game => game.id !== gameId);
        delete this.isRemoving[gameId];
      });
  }

  /**
   * Navega al detalle del juego
   * @param gameId ID del juego a ver
   */
  navigateToGameDetail(gameId: number): void {
    // Esta funcionalidad se implementaría con el Router
    console.log(`Navegar a detalle del juego ${gameId}`);
  }
}
