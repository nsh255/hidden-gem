import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-layout-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './layout-navbar.component.html',
  styleUrls: ['./layout-navbar.component.scss']
})
export class LayoutNavbarComponent {
  constructor(
    public authService: AuthService,
    public themeService: ThemeService
  ) {}

  logout() {
    this.authService.logout();
  }

  toggleTheme() {
    this.themeService.toggleTheme();
  }
}
