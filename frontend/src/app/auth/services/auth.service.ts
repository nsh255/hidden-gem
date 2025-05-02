import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  nickname: string;
  max_price: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  nickname: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private http: HttpClient) {}

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login', credentials)
      .pipe(
        tap(response => {
          // Guardar token y datos de usuario en localStorage
          localStorage.setItem('authToken', response.access_token);
          localStorage.setItem('userId', response.user_id.toString());
          localStorage.setItem('email', response.email);
          localStorage.setItem('nickname', response.nickname);
        })
      );
  }

  register(userData: RegisterData): Observable<any> {
    return this.http.post('/api/auth/register', userData);
  }

  logout(): void {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('email');
    localStorage.removeItem('nickname');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('authToken');
  }

  getAuthToken(): string | null {
    return localStorage.getItem('authToken');
  }
}
