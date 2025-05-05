import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { HttpClientModule } from '@angular/common/http';
import { GameService, PaginatedGamesResponse, GameSummary } from '../../services/game.service';

@Component({
  selector: 'app-game-list',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule],
  templateUrl: './game-list.component.html',
  styleUrl: './game-list.component.scss'
})
export class GameListComponent implements OnInit {
  games: GameSummary[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  currentPage: number = 1;
  pageSize: number = 18; // Cambiado a 18 juegos por página
  totalGames: number = 0;
  hasNextPage: boolean = false;
  hasPreviousPage: boolean = false;
  
  // Añadir Math para poder usarlo en la plantilla
  Math = Math;
  
  constructor(
    private gameService: GameService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadGames();
  }

  loadGames(page: number = 1): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.currentPage = page;
    
    this.gameService.getGames(this.currentPage, this.pageSize)
      .pipe(
        catchError(error => {
          this.errorMessage = 'Error al cargar juegos. Por favor, inténtalo de nuevo.';
          console.error('Error cargando juegos:', error);
          this.isLoading = false;
          return of({
            count: 0,
            next: null,
            previous: null,
            results: []
          } as PaginatedGamesResponse);
        })
      )
      .subscribe(response => {
        this.games = response.results;
        this.totalGames = response.count;
        this.hasNextPage = !!response.next;
        this.hasPreviousPage = !!response.previous;
        this.isLoading = false;
      });
  }

  /**
   * Navega al detalle del juego
   * @param gameId ID del juego a ver
   * @param game Objeto del juego para determinar si es de Steam
   */
  navigateToGameDetail(gameId: number, game?: any): void {
    this.router.navigate(['/steam-game', gameId]);
  }

  nextPage(): void {
    if (this.hasNextPage) {
      this.loadGames(this.currentPage + 1);
    }
  }

  previousPage(): void {
    if (this.hasPreviousPage) {
      this.loadGames(this.currentPage - 1);
    }
  }
}
