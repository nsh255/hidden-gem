import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RecommendationService } from '../../services/recommendation.service';
import { AuthService } from '../../services/auth.service';
import { RouterModule, Router } from '@angular/router';

@Component({
  selector: 'app-ai-recommendations',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './ai-recommendations.component.html',
  styleUrl: './ai-recommendations.component.scss'
})
export class AiRecommendationsComponent implements OnInit {
  recommendations: any[] = [];
  isLoading = false;
  error: string | null = null;

  constructor(
    private recommendationService: RecommendationService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const userId = this.authService.getCurrentUserId();
    if (!userId) {
      this.error = 'Debes iniciar sesión para ver recomendaciones IA.';
      return;
    }
    this.isLoading = true;
    this.recommendationService.getSteamAIRecommendations(userId)
      .subscribe({
        next: (games) => {
          this.recommendations = games;
          this.isLoading = false;
        },
        error: () => {
          this.error = 'No se pudieron obtener recomendaciones IA.';
          this.isLoading = false;
        }
      });
  }

  navigateToGameDetail(gameId: number, game?: any): void {
    // Always treat as Steam game for AI recommendations
    this.router.navigate(['/steam-game', gameId]);
  }
}
