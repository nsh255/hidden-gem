import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { GameSearchComponent } from '../game-search/game-search.component';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule, GameSearchComponent, ClickOutsideDirective],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  isMenuOpen: boolean = false;

  constructor(public authService: AuthService) { }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  closeMenu(): void {
    this.isMenuOpen = false;
  }

  logout(): void {
    this.authService.logout();
    this.closeMenu();
  }
}
