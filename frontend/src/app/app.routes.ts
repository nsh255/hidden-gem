import { Routes } from '@angular/router';
import { AuthComponent } from './pages/auth/auth.component';
import { RegisterComponent } from './pages/register/register.component';
import { HomeComponent } from './pages/home/home.component';
import { GameListComponent } from './pages/game-list/game-list.component';
import { GameDetailComponent } from './pages/game-detail/game-detail.component';
import { RecommendationsComponent } from './pages/recommendations/recommendations.component';
import { FavoritesComponent } from './pages/favorites/favorites.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'auth', component: AuthComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'games', component: GameListComponent },
  { path: 'game/:id', component: GameDetailComponent },
  { 
    path: 'favorites', 
    component: FavoritesComponent,
    canActivate: [authGuard]  // Protege la ruta para usuarios autenticados
  },
  { 
    path: 'recommendations', 
    component: RecommendationsComponent,
    canActivate: [authGuard]  // Protege la ruta para usuarios autenticados
  },
  { path: '**', redirectTo: '' }  // Redireccionar a home para rutas no encontradas
];
