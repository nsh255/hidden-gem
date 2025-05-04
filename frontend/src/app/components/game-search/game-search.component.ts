import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { debounceTime, distinctUntilChanged, Subject, switchMap, catchError, of } from 'rxjs';
import { GameService, GameSummary } from '../../services/game.service';

@Component({
  selector: 'app-game-search',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './game-search.component.html',
  styleUrls: ['./game-search.component.scss']
})
export class GameSearchComponent implements OnInit {
  searchTerm: string = '';
  searchResults: GameSummary[] = [];
  isSearching: boolean = false;
  showResults: boolean = false;
  private searchTerms = new Subject<string>();

  constructor(
    private gameService: GameService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.searchTerms.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(term => {
        this.isSearching = true;
        if (!term.trim()) {
          this.showResults = false;
          this.isSearching = false;
          return of([]);
        }
        return this.gameService.searchGames(term).pipe(
          catchError(() => {
            this.isSearching = false;
            return of([]);
          })
        );
      })
    ).subscribe(results => {
      this.searchResults = results;
      this.isSearching = false;
      this.showResults = this.searchTerm.trim().length > 0;
    });
  }

  search(term: string): void {
    this.searchTerm = term;
    this.searchTerms.next(term);
  }

  navigateToGame(gameId: number): void {
    this.router.navigate(['/game', gameId]);
    this.clearSearch();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.showResults = false;
    this.searchResults = [];
  }

  onClickOutside(): void {
    this.showResults = false;
  }
}
