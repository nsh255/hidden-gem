import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { RecommendationService, RecommendedGame } from '../../services/recommendation.service';
import { catchError, finalize } from 'rxjs/operators';
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
  
  // Variables para paginación y carga infinita
  currentPage: number = 1;
  pageSize: number = 8;
  loadingMore: boolean = false;
  allLoaded: boolean = false;
  seenGameIds: Set<number> = new Set();
  
  // Géneros predeterminados para las recomendaciones
  defaultGenres: string[] = ['Action', 'RPG', 'Adventure', 'Indie'];

  constructor(
    private recommendationService: RecommendationService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadPersonalizedRecommendations();
  }

  /**
   * Detecta el scroll para cargar más recomendaciones
   */
  @HostListener('window:scroll', [])
  onScroll(): void {
    // Calcular si estamos cerca del final de la página
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY;
    const scrollThreshold = 200; // píxeles antes del final para activar carga
    
    // Si estamos cerca del final, cargar más recomendaciones
    if (
      !this.isLoading && 
      !this.loadingMore && 
      !this.allLoaded && 
      !this.noFavoritesMessage && 
      !this.errorMessage && 
      windowHeight + scrollTop >= documentHeight - scrollThreshold
    ) {
      this.loadMoreRecommendations();
    }
  }

  /**
   * Carga las recomendaciones personalizadas para el usuario actual
   */
  loadPersonalizedRecommendations(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.noFavoritesMessage = false;
    this.seenGameIds.clear();
    
    this.recommendationService.getPersonalized(this.currentPage, this.pageSize)
      .pipe(
        catchError(error => {
          console.error('Error al cargar recomendaciones personalizadas:', error);
          
          // Verificar si el error es por falta de juegos favoritos
          if (error.status === 400 && error.message?.includes('favoritos')) {
            this.noFavoritesMessage = true;
          } else if (error.status === 401) {
            // Problema de autenticación
            this.errorMessage = 'Debes iniciar sesión para ver recomendaciones personalizadas.';
          } else {
            this.errorMessage = error.message || 'No se pudieron cargar las recomendaciones. Por favor, inténtalo de nuevo.';
          }
          
          this.isLoading = false;
          return of([]);
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe(games => {
        // Guardar los juegos y sus IDs
        this.recommendedGames = games;
        games.forEach(game => this.seenGameIds.add(game.id));
        
        // Comprobar si hay más juegos para cargar
        this.allLoaded = games.length < this.pageSize;
        
        console.log(`Cargadas ${games.length} recomendaciones iniciales.`);
      });
  }

  /**
   * Carga más recomendaciones al hacer scroll
   */
  loadMoreRecommendations(): void {
    if (this.loadingMore || this.allLoaded) return;
    
    this.loadingMore = true;
    console.log(`Cargando más recomendaciones (página ${this.currentPage + 1})...`);
    
    this.recommendationService.getPersonalized(this.currentPage + 1, this.pageSize)
      .pipe(
        catchError(error => {
          console.error('Error al cargar más recomendaciones:', error);
          this.loadingMore = false;
          // Marcar como que se han cargado todas las recomendaciones para evitar más intentos
          this.allLoaded = true;
          return of([]);
        }),
        finalize(() => {
          this.loadingMore = false;
        })
      )
      .subscribe(games => {
        // Filtrar juegos para evitar repeticiones
        const newGames = games.filter(game => !this.seenGameIds.has(game.id));
        
        // Añadir los nuevos juegos y actualizar el conjunto de IDs
        this.recommendedGames = [...this.recommendedGames, ...newGames];
        newGames.forEach(game => this.seenGameIds.add(game.id));
        
        // Actualizar paginación
        this.currentPage++;
        this.loadingMore = false;
        
        // Comprobar si hay más juegos para cargar
        this.allLoaded = games.length < this.pageSize;
        
        console.log(`Añadidos ${newGames.length} nuevos juegos a las recomendaciones.`);
        
        // Si no se cargaron nuevos juegos pero aún hay posibilidad de más, intentar con la siguiente página
        if (newGames.length === 0 && !this.allLoaded) {
          console.log('No se encontraron nuevos juegos, probando con la siguiente página');
          this.loadMoreRecommendations();
        }
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
