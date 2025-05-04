import { HttpRequest, HttpHandlerFn, HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const router = inject(Router);
  
  // Print the current URL being intercepted for debugging
  console.debug('Intercepting request to:', req.url);
  
  // Skip token for auth-related endpoints
  if (req.url.includes('/api/auth/login') || req.url.includes('/api/auth/login-json') || req.url.includes('/api/auth/register')) {
    console.debug('Skipping auth header for auth endpoint');
    return next(req);
  }
  
  // Get token
  const token = localStorage.getItem('token');
  
  if (token) {
    console.debug('Adding auth token to request');
    // Clone the request and add the Authorization header
    const authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    
    // Handle the authenticated request and catch 401/403 errors
    return next(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // If we get a 401 Unauthorized or 403 Forbidden response,
        // redirect to the login page
        if (error.status === 401 || error.status === 403) {
          console.error('Authentication error:', error.status);
          localStorage.removeItem('token');
          localStorage.removeItem('user_data');
          router.navigate(['/auth']);
        }
        return throwError(() => error);
      })
    );
  }
  
  console.debug('No token found, proceeding without auth header');
  // If no token, proceed with the original request
  return next(req);
};
