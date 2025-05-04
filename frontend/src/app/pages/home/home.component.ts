import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { GameService } from '../../services/game.service';
import { RecommendationService, RecommendedGame } from '../../services/recommendation.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

// Interfaz para los juegos (preliminar)
interface GamePreview {
  id: number;
  name: string;
  imageUrl: string;
  genres: string[];
  price: number;
  rating: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  // Datos de muestra para juegos recomendados
  recommendedGames: GamePreview[] = [
    {
      id: 1,
      name: 'Hollow Knight',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/367520/header.jpg',
      genres: ['Metroidvania', 'Souls-like', 'Plataformas'],
      price: 14.99,
      rating: '9.5'
    },
    {
      id: 2,
      name: 'Stardew Valley',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg',
      genres: ['Simulación', 'RPG', 'Pixel Art'],
      price: 14.99,
      rating: '9.8'
    },
    {
      id: 3,
      name: 'Hades',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg',
      genres: ['Roguelike', 'Acción', 'Dungeon Crawler'],
      price: 24.99,
      rating: '9.7'
    },
    {
      id: 4,
      name: 'Cuphead',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/268910/header.jpg',
      genres: ['Plataformas', 'Difícil', 'Cooperativo'],
      price: 19.99,
      rating: '9.3'
    }
  ];

  // Datos de muestra para juegos populares
  popularGames: GamePreview[] = [
    {
      id: 5,
      name: 'Celeste',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/504230/header.jpg',
      genres: ['Plataformas', 'Pixel Art', 'Difícil'],
      price: 19.99,
      rating: '9.6'
    },
    {
      id: 6,
      name: 'Dead Cells',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/588650/header.jpg',
      genres: ['Roguelike', 'Metroidvania', 'Acción'],
      price: 24.99,
      rating: '9.4'
    },
    {
      id: 7,
      name: 'Undertale',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/391540/header.jpg',
      genres: ['RPG', 'Pixel Art', 'Historia'],
      price: 9.99,
      rating: '9.7'
    },
    {
      id: 8,
      name: 'Among Us',
      imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/945360/header.jpg',
      genres: ['Multijugador', 'Social', 'Deducción'],
      price: 4.99,
      rating: '9.2'
    }
  ];

  // Nuevas propiedades para manejar las recomendaciones del API
  recommendedByGenres: RecommendedGame[] = [];
  isLoading: boolean = false;
  errorMessage: string | null = null;

  // Géneros predeterminados para las recomendaciones
  defaultGenres: string[] = ['Action', 'RPG'];

  constructor(
    private gameService: GameService,
    private recommendationService: RecommendationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Cargar datos de muestra
    this.loadRecommendedGames();
    this.loadPopularGames();
    
    // Cargar recomendaciones del API (comentado para no realizar peticiones reales por ahora)
    // this.loadRecommendationsByGenres(['Platformer', 'Metroidvania'], 20);

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
          this.isLoading = false;
          return of([]);
        })
      )
      .subscribe(games => {
        this.recommendedByGenres = games;
        this.isLoading = false;
      });
  }

  /**
   * Navega al detalle del juego
   * @param gameId ID del juego a ver
   */
  navigateToGameDetail(gameId: number): void {
    this.router.navigate(['/game', gameId]);
  }

  // Métodos para cargar los juegos de muestra
  private loadRecommendedGames(): void {
    // Aquí se llamará al servicio de recomendaciones
    // Por ahora usamos datos de muestra
    console.log('Cargando juegos recomendados');
  }

  private loadPopularGames(): void {
    // Aquí se llamará al servicio para obtener juegos populares
    // Por ahora usamos datos de muestra
    console.log('Cargando juegos populares');
  }
}
