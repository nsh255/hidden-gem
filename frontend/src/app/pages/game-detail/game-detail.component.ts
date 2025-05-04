import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Location } from '@angular/common';
import { GameService, GameDetails } from '../../services/game.service';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service'; // Add AuthService import
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
  isAuthenticated: boolean = false; // Add authentication state
  currentSimilarPage: number = 1;
  hasMoreSimilarGames: boolean = false;
  isLoadingSimilarGames: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private location: Location,
    private gameService: GameService,
    private userService: UserService,
    private authService: AuthService // Inject AuthService
  ) { }

  ngOnInit(): void {
    // Check authentication status
    this.isAuthenticated = this.authService.isLoggedIn();

    // Obtener el ID del juego de la URL
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if (idParam) {
        this.gameId = parseInt(idParam, 10);
        this.fetchGameDetails(idParam);
        // Only check favorite status if user is authenticated
        if (this.isAuthenticated) {
          this.checkFavoriteStatus(this.gameId);
        }
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

    // Determine if we're fetching a Steam game based on the route
    const isSteamGame = this.router.url.includes('/steam-game/');
    
    // Choose the appropriate service method based on the game type
    const gameObservable = isSteamGame ? 
      this.gameService.getSteamGameById(parseInt(gameId)) : 
      this.gameService.getGameById(gameId);

    gameObservable.pipe(
      catchError(error => {
        console.error('Error al obtener detalles del juego:', error);
        
        // Mensaje de error personalizado basado en el tipo de error
        if (error.status === 400 && error.error?.detail?.includes('contenido inapropiado')) {
          this.errorMessage = 'Este juego no está disponible debido a restricciones de contenido.';
        } else if (error.status === 404) {
          this.errorMessage = 'No se encontró el juego solicitado. Es posible que no exista o haya sido eliminado.';
        } else {
          this.errorMessage = 'No se pudieron cargar los detalles del juego. Por favor, inténtalo de nuevo.';
        }
        
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
   * Carga juegos similares (aleatorios por género) desde la API
   */
  loadSimilarGames(page: number = 1): void {
    if (!this.gameId || !this.gameData) return;
    
    this.isLoadingSimilarGames = true;
    
    // Extraer géneros del juego actual
    const gameGenres = this.gameData.genres?.map(g => g.name) || [];
    
    // Si no hay géneros, no podemos mostrar juegos similares
    if (gameGenres.length === 0) {
      this.isLoadingSimilarGames = false;
      return;
    }
    
    // Determinar el número de juegos por página
    const gamesPerPage = 4;
    
    // Usar el servicio para obtener juegos aleatorios por géneros
    this.gameService.getRandomGamesByGenres(gameGenres, gamesPerPage)
      .pipe(
        catchError(error => {
          console.error('Error al cargar juegos similares:', error);
          this.isLoadingSimilarGames = false;
          return of([]);
        })
      )
      .subscribe(similarGamesData => {
        console.log('Juegos similares (aleatorios por género):', similarGamesData);
        
        // Convertir los datos de la API al formato que espera la interfaz SimilarGame
        this.similarGames = similarGamesData.map(game => ({
          id: game.id,
          name: game.nombre || game.name,
          imageUrl: game.imagen_principal || game.background_image,
          genres: game.generos || (game.genres?.map((g: any) => typeof g === 'string' ? g : g.name) || [])
        }));
        
        // Simular que siempre hay más juegos disponibles para poder cambiar de página
        this.hasMoreSimilarGames = true;
        
        this.currentSimilarPage = page;
        this.isLoadingSimilarGames = false;
      });
  }

  /**
   * Navega entre páginas de juegos similares (genera nuevos juegos aleatorios)
   */
  navigateSimilarGames(direction: 'prev' | 'next'): void {
    let newPage = this.currentSimilarPage;
    
    if (direction === 'prev' && this.currentSimilarPage > 1) {
      newPage = this.currentSimilarPage - 1;
    } else if (direction === 'next') {
      newPage = this.currentSimilarPage + 1;
    } else {
      return; // No hacer nada si no se puede navegar en esa dirección
    }
    
    this.loadSimilarGames(newPage);
  }

  /**
   * Verifica si el juego actual está en favoritos
   */
  checkFavoriteStatus(gameId: number): void {
    if (!this.isAuthenticated) return;
    
    this.userService.checkIfGameIsFavorite(gameId)
      .pipe(
        catchError(error => {
          console.error('Error al verificar estado de favorito:', error);
          return of(false);
        })
      )
      .subscribe(isFavorite => {
        this.isFavorite = isFavorite;
      });
  }

  /**
   * Añade el juego actual a favoritos
   */
  addToFavorites(): void {
    if (!this.gameId || !this.isAuthenticated) return;
    
    this.isAddingToFavorites = true;
    this.favoriteActionMessage = null;

    // Get current user ID from the auth service
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      this.favoriteActionMessage = 'Debes iniciar sesión para añadir favoritos';
      this.favoriteActionSuccess = false;
      this.isAddingToFavorites = false;
      return;
    }

    this.userService.addFavorite(this.gameId)
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
   * Quita el juego actual de favoritos
   */
  removeFromFavorites(): void {
    if (!this.gameId || !this.isAuthenticated) return;
    
    this.isAddingToFavorites = true; // Reutilizamos la variable de estado
    this.favoriteActionMessage = null;

    // Get current user ID from the auth service
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      this.favoriteActionMessage = 'Debes iniciar sesión para gestionar favoritos';
      this.favoriteActionSuccess = false;
      this.isAddingToFavorites = false;
      return;
    }

    this.userService.removeFavorite(this.gameId)
      .pipe(
        catchError(error => {
          console.error('Error al quitar de favoritos:', error);
          this.favoriteActionMessage = 'Error al quitar de favoritos. Por favor, inténtalo de nuevo.';
          this.favoriteActionSuccess = false;
          this.isAddingToFavorites = false;
          return of(null);
        })
      )
      .subscribe(response => {
        this.isFavorite = false;
        this.favoriteActionMessage = 'Juego eliminado de favoritos';
        this.favoriteActionSuccess = true;
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
      this.removeFromFavorites();
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
