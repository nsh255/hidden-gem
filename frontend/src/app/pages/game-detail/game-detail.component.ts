import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Location } from '@angular/common';
import { GameService, GameDetails } from '../../services/game.service';
import { UserService } from '../../services/user.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

// Interfaz para el detalle del juego (se usará eventualmente con el servicio)
interface GameDetail {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
  genres: string[];
  releaseDate: Date;
  price: number;
  rating: string;
  storeUrl?: string;
  screenshots?: string[];
}

// Interfaz para juegos similares
interface SimilarGame {
  id: number;
  name: string;
  imageUrl: string;
  genres: string[];
}

@Component({
  selector: 'app-game-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './game-detail.component.html',
  styleUrl: './game-detail.component.scss'
})
export class GameDetailComponent implements OnInit {
  gameId: number | null = null;
  game: GameDetail | null = null;
  gameData: GameDetails | null = null;
  similarGames: SimilarGame[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  isFavorite: boolean = false;
  isAddingToFavorites: boolean = false;
  favoriteActionMessage: string | null = null;
  favoriteActionSuccess: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private location: Location,
    private gameService: GameService,
    private userService: UserService
  ) { }

  ngOnInit(): void {
    // Obtener el ID del juego de la URL
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if (idParam) {
        this.gameId = parseInt(idParam, 10);
        this.fetchGameDetails(idParam);
      } else {
        this.errorMessage = 'No se pudo encontrar el ID del juego.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Obtiene los detalles del juego desde la API
   * @param gameId ID del juego a consultar
   */
  fetchGameDetails(gameId: string): void {
    this.isLoading = true;
    this.errorMessage = null;

    this.gameService.getGameById(gameId)
      .pipe(
        catchError(error => {
          console.error('Error al obtener detalles del juego:', error);
          this.errorMessage = 'No se pudieron cargar los detalles del juego. Por favor, inténtalo de nuevo.';
          this.isLoading = false;
          return of(null);
        })
      )
      .subscribe(data => {
        if (data) {
          this.gameData = data;
          // Convertir datos de la API al formato que espera nuestra interfaz
          this.mapApiDataToGameDetail(data);
          // También podríamos cargar juegos similares aquí basados en géneros
          this.loadSimilarGames();
        }
        this.isLoading = false;
      });
  }

  /**
   * Convierte los datos de la API al formato que espera nuestra interfaz
   */
  mapApiDataToGameDetail(data: GameDetails): void {
    this.game = {
      id: data.id,
      name: data.name,
      imageUrl: data.background_image,
      description: data.description,
      genres: data.genres?.map(g => g.name) || [],
      releaseDate: new Date(data.released),
      price: data.price || 0,
      rating: data.rating ? data.rating.toFixed(1) : 'N/A',
      storeUrl: data.stores?.length ? `https://${data.stores[0].store.domain}` : undefined,
      screenshots: data.screenshots?.map(s => s.image) || []
    };
  }

  /**
   * Carga juegos similares (simulado por ahora)
   */
  loadSimilarGames(): void {
    // Simulación de carga
    setTimeout(() => {
      // Para el ejemplo, usamos datos simulados
      this.similarGames = [
        {
          id: 1,
          name: 'Celeste',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/504230/header.jpg',
          genres: ['Plataformas', 'Indie', 'Difícil']
        },
        {
          id: 2,
          name: 'Dead Cells',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/588650/header.jpg',
          genres: ['Roguelike', 'Metroidvania', 'Acción']
        },
        {
          id: 3,
          name: 'Hades',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg',
          genres: ['Roguelike', 'Acción', 'Indie']
        }
      ];
    }, 500);
  }

  /**
   * Añade el juego actual a favoritos
   */
  addToFavorites(): void {
    if (!this.gameId) return;
    
    this.isAddingToFavorites = true;
    this.favoriteActionMessage = null;

    this.userService.addGameToFavorites(this.gameId)
      .pipe(
        catchError(error => {
          console.error('Error al añadir a favoritos:', error);
          this.favoriteActionMessage = 'Error al añadir a favoritos. Por favor, inténtalo de nuevo.';
          this.favoriteActionSuccess = false;
          this.isAddingToFavorites = false;
          return of(null);
        })
      )
      .subscribe(response => {
        if (response) {
          this.isFavorite = true;
          this.favoriteActionMessage = '¡Juego añadido a favoritos!';
          this.favoriteActionSuccess = true;
        }
        this.isAddingToFavorites = false;
        
        // Auto-ocultar el mensaje después de 3 segundos
        setTimeout(() => {
          this.favoriteActionMessage = null;
        }, 3000);
      });
  }

  /**
   * Toggle para añadir/quitar de favoritos
   */
  toggleFavorite(): void {
    if (this.isFavorite) {
      // Lógica para quitar de favoritos (para implementar más adelante)
      console.log('Quitar de favoritos no implementado aún');
    } else {
      this.addToFavorites();
    }
  }

  /**
   * Navegar a la página anterior
   */
  goBack(): void {
    this.location.back();
  }

  /**
   * Navegar a otro juego
   */
  navigateToGame(gameId: number): void {
    // Navegar a otro juego, recargando el componente
    this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
      this.router.navigate(['/game', gameId]);
    });
  }
}
