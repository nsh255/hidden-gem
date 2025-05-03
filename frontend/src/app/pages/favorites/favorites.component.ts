import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
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

  constructor(private userService: UserService) { }

  ngOnInit(): void {
    this.loadFavoriteGames();
  }

  /**
   * Carga los juegos favoritos del usuario
   */
  loadFavoriteGames(): void {
    this.isLoading = true;
    this.errorMessage = null;

    // En una implementación real, aquí llamaríamos al servicio para obtener los favoritos
    // Por ahora, simularemos datos para la vista
    
    setTimeout(() => {
      // Datos de ejemplo - estos vendrían del servicio en una implementación real
      this.favoriteGames = [
        {
          id: 1,
          name: 'Hollow Knight',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/367520/header.jpg',
          genres: ['Metroidvania', 'Souls-like', 'Plataformas']
        },
        {
          id: 2,
          name: 'Stardew Valley',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg',
          genres: ['Simulación', 'RPG', 'Pixel Art']
        },
        {
          id: 3,
          name: 'Hades',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg',
          genres: ['Roguelike', 'Acción', 'Dungeon Crawler']
        },
        {
          id: 4,
          name: 'Celeste',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/504230/header.jpg',
          genres: ['Plataformas', 'Pixel Art', 'Difícil']
        }
      ];
      this.isLoading = false;
    }, 1000);

    // Implementación real (comentada)
    /*
    this.userService.getFavoriteGames()
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
    */
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

    // Simulamos la eliminación con un timeout
    setTimeout(() => {
      // Lógica para eliminar de favoritos (simulada)
      this.favoriteGames = this.favoriteGames.filter(game => game.id !== gameId);
      delete this.isRemoving[gameId];
    }, 800);

    // Implementación real (comentada)
    /*
    this.userService.removeGameFromFavorites(gameId)
      .pipe(
        catchError(error => {
          console.error('Error al eliminar de favoritos:', error);
          this.isRemoving[gameId] = false;
          alert('Error al eliminar de favoritos. Por favor, inténtalo de nuevo.');
          return of(null);
        })
      )
      .subscribe(response => {
        if (response) {
          // Eliminar el juego de la lista local
          this.favoriteGames = this.favoriteGames.filter(game => game.id !== gameId);
        }
        delete this.isRemoving[gameId];
      });
    */
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
