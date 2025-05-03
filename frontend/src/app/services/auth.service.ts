import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';

interface User {
  id: number;
  nick: string;
  email: string;
}

interface AuthResponse {
  token: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenKey = 'auth_token';
  private userKey = 'user_data';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  
  public currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(private http: HttpClient, private router: Router) {
    // Intenta cargar el usuario desde localStorage al iniciar el servicio
    const userData = this.getUserData();
    if (userData) {
      this.currentUserSubject.next(userData);
    }
  }
  
  login(email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login-json', { email, password })
      .pipe(
        tap(response => {
          // Guarda el token en localStorage
          localStorage.setItem(this.tokenKey, response.token);
          
          // Guarda los datos del usuario en localStorage
          localStorage.setItem(this.userKey, JSON.stringify(response.user));
          
          // Actualiza el BehaviorSubject con los datos del usuario
          this.currentUserSubject.next(response.user);
        })
      );
  }
  
  logout(): void {
    // Elimina el token y datos del usuario de localStorage
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    
    // Actualiza el BehaviorSubject
    this.currentUserSubject.next(null);
    
    // Redirige al usuario a la página de inicio
    this.router.navigate(['/']);
  }
  
  isLoggedIn(): boolean {
    return !!this.getToken() && !!this.getUserData();
  }
  
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
  
  getUserData(): User | null {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }
  
  getCurrentUserId(): number | null {
    const user = this.getUserData();
    return user ? user.id : null;
  }
}
