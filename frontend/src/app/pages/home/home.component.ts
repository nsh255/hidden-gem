import { Component, HostListener, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { GameService, GameSummary } from '../../services/game.service';
import { RecommendationService, RecommendedGame } from '../../services/recommendation.service';
import { AuthService } from '../../services/auth.service';
import { catchError, finalize, filter } from 'rxjs/operators';
import { of, Subscription } from 'rxjs';
import { GameSearchComponent } from '../../components/game-search/game-search.component';

// Interfaz para los datos crudos de juegos que vienen de la API
interface RawGameData {
  id?: number;
  name?: string;
  background_image?: string;
  released?: string;
  rating?: number;
  genres?: Array<{id: number, name: string}>;
  price?: number;
  [key: string]: any; // Para cualquier otra propiedad que pueda tener
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, GameSearchComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit, OnDestroy {
  // Arrays de juegos
  popularGames: GameSummary[] = [];
  randomGames: GameSummary[] = [];
  isLoadingRandomGames: boolean = false;
  randomGamesPage: number = 1;

  // Estado de carga
  isLoadingPopular: boolean = false;
  errorPopular: string | null = null;

  // Estado de autenticación
  isAuthenticated: boolean = false;

  // Búsqueda
  searchResults: GameSummary[] = [];
  isSearching: boolean = false;
  searchError: string | null = null;

  // Nuevas propiedades para juegos por género
  genresList: string[] = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Puzzle', 'Platformer', 'Roguelike', 'Survival'];
  gamesByGenre: { [genre: string]: any[] } = {};
  loadingGenres: { [genre: string]: boolean } = {};

  // Track router navigation
  private routeSubscription: Subscription | null = null;
  private lastVisit: number = 0;

  constructor(
    private gameService: GameService,
    private recommendationService: RecommendationService,
    private router: Router,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    this.isAuthenticated = this.authService.isLoggedIn();
    
    // Set last visit timestamp
    this.lastVisit = Date.now();
    
    // Subscribe to router events to detect when returning to home
    this.routeSubscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      // Only refresh if returning to home from another route
      if ((event.url === '/' || event.url === '/home') && this.lastVisit > 0) {
        console.log('Returning to home page, refreshing genre games');
        this.refreshAllGenreGames();
      }
      // Update last visit timestamp
      this.lastVisit = Date.now();
    });
    
    // Solo cargamos juegos por género si el usuario está autenticado
    if (this.isAuthenticated) {
      this.loadGamesByGenres();
    }
    
    this.loadPopularGames();
    this.loadRandomGames();
  }
  
  ngOnDestroy(): void {
    // Cleanup subscription to prevent memory leaks
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
      this.routeSubscription = null;
    }
  }

  /**
   * Fuerza la recarga de todos los juegos por género
   */
  refreshAllGenreGames(): void {
    if (this.isAuthenticated) {
      // Reset data and force reload
      this.gamesByGenre = {};
      this.loadGamesByGenres(true);
    }
  }

  /**
   * Carga juegos para cada género en la lista
   * @param forceRefresh Si es true, fuerza la recarga ignorando la caché
   */
  loadGamesByGenres(forceRefresh: boolean = false): void {
    this.genresList.forEach(genre => {
      this.loadGamesByGenre(genre, forceRefresh);
    });
  }

  /**
   * Carga juegos aleatorios para un género específico
   * @param genre Género de juegos a cargar
   * @param forceRefresh Si es true, fuerza la recarga ignorando la caché
   */
  loadGamesByGenre(genre: string, forceRefresh: boolean = false): void {
    this.loadingGenres[genre] = true;
    
    // Generate a timestamp to force new data from the server
    const timestamp = forceRefresh ? Date.now() : undefined;
    
    this.recommendationService.getRecommendationsByGenres([genre], undefined, 3, timestamp)
      .pipe(
        catchError(error => {
          console.error(`Error cargando juegos del género ${genre}:`, error);
          return of([]);
        }),
        finalize(() => {
          this.loadingGenres[genre] = false;
        })
      )
      .subscribe(games => {
        this.gamesByGenre[genre] = games;
      });
  }

  /**
   * Navega al detalle del juego
   * @param gameId ID del juego a ver
   * @param game Objeto del juego para determinar si es de Steam
   */
  navigateToGameDetail(gameId: number, game?: any): void {
    // Determine if the game is from Steam based on its structure
    const isSteamGame = game && (game.nombre !== undefined || game.imagen_principal !== undefined);
    
    console.log('Navigating to game detail:', gameId, isSteamGame ? '(Steam game)' : '(RAWG game)');
    
    if (isSteamGame) {
      // Use the Steam game endpoint
      this.router.navigate(['/steam-game', gameId]);
    } else {
      // Use the standard RAWG game endpoint
      this.router.navigate(['/game', gameId]);
    }
  }

  /**
   * Determina si se debe mostrar el rating de un juego
   * No mostramos el rating para juegos de Steam
   */
  shouldShowRating(game: any): boolean {
    // Si es un juego de Steam, no se muestra el rating
    return !this.isFromSteam(game) && !!game.rating;
  }

  /**
   * Verifica si un juego proviene de Steam
   */
  isFromSteam(game: any): boolean {
    // Verificar si tiene properties específicas de la estructura de Steam
    return (game.nombre !== undefined || game.imagen_principal !== undefined);
  }

  /**
   * Obtiene los géneros de un juego, independientemente de su estructura
   */
  getGameGenres(game: any): string[] {
    if (game.genres) {
      // Si es un juego de RAWG
      return game.genres.map((g: any) => typeof g === 'string' ? g : g.name);
    } else if (game.generos) {
      // Si es un juego de Steam
      return game.generos;
    }
    return [];
  }

  loadPopularGames(): void {
    this.isLoadingPopular = true;
    this.errorPopular = null;
    
    // Obtener juegos en tendencia como populares
    this.gameService.getTrendingGames(1, 9)
      .pipe(
        catchError(error => {
          this.errorPopular = 'Error al cargar juegos populares.';
          console.error('Error cargando juegos populares:', error);
          return of({ count: 0, results: [] });
        }),
        finalize(() => {
          this.isLoadingPopular = false;
        })
      )
      .subscribe(response => {
        if (response && response.results) {
          // Mapear los resultados al formato esperado por la UI
          this.popularGames = response.results.map((game: RawGameData) => ({
            id: game.id || 0,
            name: game.name || 'Juego sin nombre',
            background_image: game.background_image || 'assets/images/placeholder.jpg',
            released: game.released || '',
            rating: typeof game.rating === 'number' ? game.rating : 0,
            genres: Array.isArray(game.genres) ? game.genres : [],
            price: typeof game.price === 'number' ? game.price : 19.99
          }));
        } else {
          this.popularGames = [];
          this.errorPopular = 'No se pudieron cargar juegos populares.';
        }
      });
  }

  formatPrice(price: number | null | undefined, isFromRawg: boolean): string | null {
    if (isFromRawg || price === undefined) return null; // Hide price for RAWG games or undefined values
    return price === null || price === 0 ? 'Free to play' : `$${price.toFixed(2)}`;
  }

  loadRandomGames(): void {
    if (this.isLoadingRandomGames) return;

    this.isLoadingRandomGames = true;
    
    // Add a random parameter to ensure we get different games each time
    this.gameService.getRandomGamesWithPage(this.randomGamesPage, 10)
      .subscribe({
        next: (response) => {
          if (response && response.results && response.results.length > 0) {
            this.randomGames = [...this.randomGames, ...response.results];
            this.randomGamesPage++;
          } else {
            console.log('No more random games available');
          }
          this.isLoadingRandomGames = false;
        },
        error: (error) => {
          console.error('Error loading random games:', error);
          this.isLoadingRandomGames = false;
        }
      });
  }

  @HostListener('window:scroll', [])
  onScroll(): void {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 500) {
      this.loadRandomGames(); // Load more random games when near the bottom
    }
  }

  /**
   * Maneja la búsqueda de juegos
   * @param query Texto de búsqueda
   */
  searchGames(query: string): void {
    if (!query.trim()) {
      this.searchResults = [];
      return;
    }

    this.isSearching = true;
    this.searchError = null;

    this.gameService.searchGames(query)
      .subscribe({
        next: (results) => {
          this.searchResults = results;
          this.isSearching = false;
        },
        error: (error) => {
          console.error('Error al buscar juegos:', error);
          this.searchError = 'No se pudieron cargar los resultados de búsqueda.';
          this.isSearching = false;
        }
      });
  }
}
