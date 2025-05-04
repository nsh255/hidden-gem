import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { GameService, GameSummary } from '../../services/game.service';
import { RecommendationService, RecommendedGame } from '../../services/recommendation.service';
import { catchError, finalize } from 'rxjs/operators';
import { of } from 'rxjs';

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
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  // Reemplazamos los arreglos hardcodeados con arreglos vacíos
  recommendedGames: GameSummary[] = [];
  popularGames: GameSummary[] = [];

  // Propiedades para las recomendaciones de la API
  recommendedByGenres: RecommendedGame[] = [];
  isLoading: boolean = false;
  isLoadingPopular: boolean = false;
  isLoadingRecommended: boolean = false;
  errorMessage: string | null = null;
  errorPopular: string | null = null;
  errorRecommended: string | null = null;

  // Géneros predeterminados para las recomendaciones
  defaultGenres: string[] = ['Action', 'RPG'];

  constructor(
    private gameService: GameService,
    private recommendationService: RecommendationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Cargar datos reales desde los servicios
    this.loadRecommendedGames();
    this.loadPopularGames();
    
    // Cargar recomendaciones por géneros desde la API
    this.loadRecommendationsByGenres(this.defaultGenres);
  }

  // Método para cargar recomendaciones basadas en géneros
  loadRecommendationsByGenres(genres: string[], maxPrice?: number): void {
    this.isLoading = true;
    this.errorMessage = null;
    
    this.recommendationService.getRecommendationsByGenres(genres, maxPrice)
      .pipe(
        catchError(error => {
          this.errorMessage = 'Error al cargar recomendaciones. Por favor, inténtalo de nuevo.';
          console.error('Error cargando recomendaciones:', error);
          return of([]);
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe(games => {
        this.recommendedByGenres = games;
      });
  }

  /**
   * Navega al detalle del juego
   * @param gameId ID del juego a ver
   */
  navigateToGameDetail(gameId: number): void {
    this.router.navigate(['/game', gameId]);
  }

  // Método para cargar juegos recomendados
  loadRecommendedGames(): void {
    this.isLoadingRecommended = true;
    this.errorRecommended = null;
    
    // Obtener juegos aleatorios como recomendados
    this.gameService.getRandomGames(4)
      .pipe(
        catchError(error => {
          this.errorRecommended = 'Error al cargar juegos recomendados.';
          console.error('Error cargando juegos recomendados:', error);
          return of({ count: 0, results: [] });
        }),
        finalize(() => {
          this.isLoadingRecommended = false;
        })
      )
      .subscribe(response => {
        if (response && response.results) {
          // Mapear los resultados al formato esperado por la UI
          this.recommendedGames = response.results.map((game: RawGameData) => ({
            id: game.id || 0,
            name: game.name || 'Juego sin nombre',
            background_image: game.background_image || 'assets/images/placeholder.jpg',
            released: game.released || '',
            rating: typeof game.rating === 'number' ? game.rating : 0,
            genres: Array.isArray(game.genres) ? game.genres : [],
            price: typeof game.price === 'number' ? game.price : 19.99
          }));
        } else {
          this.recommendedGames = [];
          this.errorRecommended = 'No se pudieron cargar juegos recomendados.';
        }
      });
  }

  loadPopularGames(): void {
    this.isLoadingPopular = true;
    this.errorPopular = null;
    
    // Obtener juegos en tendencia como populares
    this.gameService.getTrendingGames(1, 4)
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
}
