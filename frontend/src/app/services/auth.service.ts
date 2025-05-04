import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';
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
        }),
        catchError((error: HttpErrorResponse) => {
          let errorMsg = 'Error en el inicio de sesión';
          
          if (error.status === 401) {
            errorMsg = 'Credenciales incorrectas';
          } else if (error.error && error.error.detail) {
            errorMsg = typeof error.error.detail === 'string' 
              ? error.error.detail 
              : 'Error en el servidor';
          }
          
          return throwError(() => new Error(errorMsg));
        })
      );
  }
  
  /**
   * Registra un nuevo usuario y lo autentica automáticamente
   * @param nombre Nombre de usuario (nick)
   * @param email Email del usuario
   * @param password Contraseña del usuario
   * @param precio_max Precio máximo a pagar por un juego
   * @returns Observable con la respuesta de autenticación
   */
  register(nombre: string, email: string, password: string, precio_max: number = 20.0): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/register', {
      nick: nombre,
      email: email,
      password: password,
      precio_max: precio_max
    }).pipe(
      tap(response => {
        // Guardar el token JWT en localStorage
        localStorage.setItem(this.tokenKey, response.token);
        
        // Guardar la información del usuario en localStorage
        localStorage.setItem(this.userKey, JSON.stringify(response.user));
        
        // Actualizar el BehaviorSubject con los datos del usuario
        this.currentUserSubject.next(response.user);
        
        // Redirigir al usuario a la página de inicio después del registro exitoso
        this.router.navigate(['/home']);
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
    return !!localStorage.getItem('auth_token'); // Check if token exists
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

  /**
   * Verifica si el token actual es válido
   * @returns Observable que indica si el token es válido
   */
  verifyToken(): Observable<boolean> {
    return this.http.post<{valid: boolean}>('/api/auth/verify-token', {})
      .pipe(
        map(response => response.valid),
        catchError(() => {
          // Si hay error, el token no es válido
          this.logout();
          return of(false);
        })
      );
  }
  
  /**
   * Actualiza la información del usuario actual
   * @param userData Datos a actualizar
   * @returns Observable con la respuesta del servidor
   */
  updateUserData(userData: Partial<User>): Observable<User> {
    return this.http.patch<User>('/api/users/me', userData)
      .pipe(
        tap(updatedUser => {
          // Actualizar el usuario en localStorage
          const currentUser = this.getUserData();
          if (currentUser) {
            const newUserData = { ...currentUser, ...updatedUser };
            localStorage.setItem(this.userKey, JSON.stringify(newUserData));
            this.currentUserSubject.next(newUserData);
          }
        })
      );
  }

  /**
   * Cambia la contraseña del usuario actual
   * @param currentPassword Contraseña actual
   * @param newPassword Nueva contraseña
   * @returns Observable con la respuesta del servidor
   */
  changePassword(currentPassword: string, newPassword: string): Observable<any> {
    return this.http.post<any>('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  /**
   * Solicita restablecimiento de contraseña
   * @param email Email del usuario
   * @returns Observable con la respuesta del servidor
   */
  requestPasswordReset(email: string): Observable<any> {
    return this.http.post<any>('/api/auth/request-password-reset', { email });
  }

  /**
   * Restablece la contraseña con token
   * @param token Token de restablecimiento
   * @param newPassword Nueva contraseña
   * @returns Observable con la respuesta del servidor
   */
  resetPassword(token: string, newPassword: string): Observable<any> {
    return this.http.post<any>('/api/auth/reset-password', {
      token,
      new_password: newPassword
    });
  }

  /**
   * Realiza logout tanto en el cliente como en el servidor
   * invalidando el token actual
   * @returns Observable que indica el éxito del logout
   */
  serverLogout(): Observable<any> {
    // Obtener el token actual
    const token = this.getToken();
    
    // Si no hay token, hacer logout solo del lado del cliente
    if (!token) {
      this.logout();
      return of({ success: true });
    }
    
    // Realizar logout en el servidor
    return this.http.post<any>('/api/auth/logout', {})
      .pipe(
        tap(() => {
          // Al recibir respuesta exitosa, realizar logout local
          this.logout();
        }),
        catchError(error => {
          // Incluso si hay error, realizar logout local
          console.error('Error durante el logout en servidor:', error);
          this.logout();
          return of({ success: true, error: 'Logout parcial' });
        })
      );
  }

  /**
   * Refresca el token de autenticación
   * @returns Observable con la respuesta que contiene el nuevo token
   */
  refreshToken(): Observable<{token: string}> {
    return this.http.post<{token: string}>('/api/auth/refresh-token', {})
      .pipe(
        tap(response => {
          // Actualizar el token en localStorage
          localStorage.setItem(this.tokenKey, response.token);
        }),
        catchError(error => {
          // Si no se puede refrescar, forzar logout
          console.error('Error al refrescar token:', error);
          this.logout();
          return throwError(() => new Error('No se pudo refrescar la sesión'));
        })
      );
  }

  /**
   * Verifica si el email ya está registrado
   * @param email Email a verificar
   * @returns Observable con el resultado de la verificación
   */
  checkEmailExists(email: string): Observable<{exists: boolean}> {
    return this.http.get<{exists: boolean}>(`/api/auth/check-email?email=${encodeURIComponent(email)}`);
  }
}
