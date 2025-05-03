import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
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

interface RegisterResponse {
  id: number;
  nick: string;
  email: string;
  precio_max: number;
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
  
  /**
   * Registra un nuevo usuario y lo autentica automáticamente
   * @param nombre Nombre de usuario (nick)
   * @param email Email del usuario
   * @param password Contraseña del usuario
   * @returns Observable con la respuesta de autenticación
   */
  register(nombre: string, email: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/register', {
      nick: nombre,
      email: email,
      password: password
    }).pipe(
      tap(response => {
        // Guardar el token JWT en localStorage
        localStorage.setItem(this.tokenKey, response.token);
        
        // Guardar la información del usuario en localStorage
        localStorage.setItem(this.userKey, JSON.stringify(response.user));
        
        // Actualizar el BehaviorSubject con los datos del usuario
        this.currentUserSubject.next(response.user);
      }),
      catchError((error: HttpErrorResponse) => {
        let errorMsg = 'Error en el registro';
        
        // Manejar errores de validación
        if (error.status === 400) {
          if (error.error && error.error.detail) {
            if (typeof error.error.detail === 'string') {
              errorMsg = error.error.detail;
            } else if (Array.isArray(error.error.detail)) {
              // Para errores de validación Pydantic que vienen como array
              errorMsg = error.error.detail.map((err: any) => err.msg).join(', ');
            }
          }
        }
        
        return throwError(() => new Error(errorMsg));
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
