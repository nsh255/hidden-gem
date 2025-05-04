import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private router: Router) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Don't add token for auth requests to avoid interference with login/register
    if (request.url.includes('/api/auth/')) {
      return next.handle(request);
    }
    
    // Get the auth token from localStorage
    const token = localStorage.getItem('token');
    
    if (token) {
      // Clone the request and add the Authorization header
      const authReq = request.clone({
        headers: request.headers.set('Authorization', `Bearer ${token}`)
      });
      
      // Handle the authenticated request and catch 401/403 errors
      return next.handle(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
          // If we get a 401 Unauthorized or 403 Forbidden response,
          // redirect to the login page
          if (error.status === 401 || error.status === 403) {
            console.error('Authentication error:', error.status);
            localStorage.removeItem('token');
            localStorage.removeItem('user_data');
            this.router.navigate(['/auth']);
          }
          return throwError(() => error);
        })
      );
    }
    
    // If no token, proceed with the original request
    return next.handle(request);
  }
}
