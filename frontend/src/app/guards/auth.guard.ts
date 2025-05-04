import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  // Redireccionar a la página de login con la URL a la que se intentaba acceder
  router.navigate(['/auth'], { 
    queryParams: { returnUrl: state.url }
  });
  
  return false;
};
