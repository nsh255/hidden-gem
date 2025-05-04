import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-layout-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './layout-navbar.component.html',
  styleUrl: './layout-navbar.component.scss'
})
export class LayoutNavbarComponent {
  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  logout(): void {
    // First navigate to home
    this.router.navigate(['/'])
      .then(() => {
        // Then logout
        this.authService.logout();
        // Then reload the page to refresh all components
        window.location.reload();
      });
  }
}
