import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { GameService, RecommendedGame } from '../../services/game.service';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './recommendations.component.html',
  styleUrl: './recommendations.component.scss'
})
export class RecommendationsComponent implements OnInit {
  recommendedGames: RecommendedGame[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  noFavoritesMessage: boolean = false;
  
  // Géneros predeterminados para las recomendaciones
  defaultGenres: string[] = ['Action', 'RPG', 'Adventure', 'Indie'];

  constructor(
    private gameService: GameService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadPersonalizedRecommendations();
  }

  /**
   * Carga las recomendaciones personalizadas para el usuario actual
   */
  loadPersonalizedRecommendations(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.noFavoritesMessage = false;
    
    this.gameService.getPersonalized()
      .pipe(
        catchError(error => {
          console.error('Error al cargar recomendaciones personalizadas:', error);
          
          // Verificar si el error es por falta de juegos favoritos
          if (error.status === 400 && error.error?.detail?.includes('favoritos')) {
            this.noFavoritesMessage = true;
          } else {
            this.errorMessage = 'No se pudieron cargar las recomendaciones. Por favor, inténtalo de nuevo.';
          }
          
          this.isLoading = false;
          return of([]);
        })
      )
      .subscribe(games => {
        this.recommendedGames = games;
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
}
