import { Injectable } from '@angular/core';
import { 
  HttpInterceptor, 
  HttpRequest, 
  HttpHandler, 
  HttpEvent 
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  
  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Obtener el token JWT usando el servicio AuthService
    const token = this.authService.getToken();
    
    // Si tenemos un token, clonamos la petición y añadimos la cabecera de autorización
    if (token) {
      // Clonamos la petición porque las peticiones HTTP son inmutables
      const authRequest = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Pasamos la petición clonada al siguiente manejador
      return next.handle(authRequest);
    }
    
    // Si no hay token, simplemente pasamos la petición original sin modificar
    return next.handle(request);
  }
}
