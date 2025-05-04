import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
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
  private apiUrl = '/api/auth';
  private tokenKey = 'token'; // Changed to use 'token' consistently
  private userKey = 'user_data';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  
  public currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(private http: HttpClient, private router: Router) {
    console.debug('AuthService initialized');
    // Intenta cargar el usuario desde localStorage al iniciar el servicio
    const userData = this.getUserData();
    if (userData) {
      this.currentUserSubject.next(userData);
    }
  }
  
  /**
   * Inicia sesión con credenciales de usuario
   * @param loginData Datos de inicio de sesión (email y password)
   * @returns Observable con la respuesta del servidor
   */
  login(loginData: { email: string; password: string }): Observable<any> {
    console.debug('Attempting login for:', loginData.email);
    
    // Ensure we're using application/json content type
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    // Use the login-json endpoint which expects email/password as JSON
    return this.http.post<any>(`${this.apiUrl}/login-json`, loginData, { headers }).pipe(
      tap(response => {
        console.debug('Login successful, response:', response);
        
        // Store token and user data in localStorage using consistent keys
        if (response.token) {
          localStorage.setItem(this.tokenKey, response.token);
          console.debug('Token stored in localStorage under key:', this.tokenKey);
        } else {
          console.warn('No token received in login response');
        }
        
        if (response.user) {
          localStorage.setItem(this.userKey, JSON.stringify(response.user));
          console.debug('User data stored in localStorage');
        } else {
          console.warn('No user data received in login response');
        }
        
        // Actualiza el BehaviorSubject con los datos del usuario
        this.currentUserSubject.next(response.user);
      }),
      catchError((error: HttpErrorResponse) => {
        console.error('Login error:', error);
        let errorMsg = 'Error en el inicio de sesión';
        
        if (error.status === 401) {
          errorMsg = 'Credenciales incorrectas';
        } else if (error.status === 422) {
          errorMsg = 'Formato de datos incorrecto, comprueba tu email y contraseña';
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
    console.debug('Registering new user:', email);
    
    return this.http.post<AuthResponse>(`${this.apiUrl}/register`, {
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
        console.error('Registration error:', error);
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
    console.debug('Logging out user');
    // Elimina el token y datos del usuario de localStorage
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    
    // Actualiza el BehaviorSubject
    this.currentUserSubject.next(null);
    
    // Redirige al usuario a la página de inicio
    this.router.navigate(['/auth']);
  }
  
  /**
   * Checks if the user is logged in
   * @returns true if the user is logged in, false otherwise
   */
  isLoggedIn(): boolean {
    const token = this.getToken();
    // Also log the token (just first few characters for security) for debugging
    if (token) {
      console.debug('Token found, first 10 chars:', token.substring(0, 10) + '...');
    } else {
      console.debug('No authentication token found');
    }
    return !!token;
  }
  
  /**
   * Gets the current authentication token
   * @returns The JWT token or null if not authenticated
   */
  getToken(): string | null {
    const token = localStorage.getItem(this.tokenKey);
    if (token) {
      console.debug('Token retrieved from localStorage under key:', this.tokenKey);
    }
    return token;
  }
  
  getUserData(): User | null {
    const userData = localStorage.getItem(this.userKey);
    if (!userData) {
      return null;
    }
    
    try {
      return JSON.parse(userData);
    } catch (e) {
      console.error('Error parsing user data:', e);
      return null;
    }
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
    return this.http.post<{valid: boolean}>(`${this.apiUrl}/verify-token`, {})
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
    return this.http.post<any>(`${this.apiUrl}/change-password`, {
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
    return this.http.post<any>(`${this.apiUrl}/request-password-reset`, { email });
  }

  /**
   * Restablece la contraseña con token
   * @param token Token de restablecimiento
   * @param newPassword Nueva contraseña
   * @returns Observable con la respuesta del servidor
   */
  resetPassword(token: string, newPassword: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/reset-password`, {
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
    return this.http.post<any>(`${this.apiUrl}/logout`, {})
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
    return this.http.post<{token: string}>(`${this.apiUrl}/refresh-token`, {})
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
    return this.http.get<{exists: boolean}>(`${this.apiUrl}/check-email?email=${encodeURIComponent(email)}`);
  }
}
