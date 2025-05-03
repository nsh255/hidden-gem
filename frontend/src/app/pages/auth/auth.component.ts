import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss'
})
export class AuthComponent {
  loginForm: FormGroup;
  errorMessage: string | null = null;
  isLoading = false;

  constructor(
    private fb: FormBuilder, 
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;
      
      const { email, password } = this.loginForm.value;
      
      this.authService.login(email, password)
        .subscribe({
          next: (response) => {
            this.isLoading = false;
            console.log('Login exitoso', response);
            // Redirige a la página principal después del login
            this.router.navigate(['/']);
          },
          error: (error: HttpErrorResponse) => {
            this.isLoading = false;
            if (error.status === 401) {
              this.errorMessage = 'Credenciales incorrectas. Por favor, verifica tu email y contraseña.';
            } else if (error.error && error.error.detail) {
              this.errorMessage = error.error.detail;
            } else {
              this.errorMessage = 'Error al iniciar sesión. Por favor, inténtalo de nuevo.';
            }
            console.error('Error de login', error);
          }
        });
    } else {
      // Marcar todos los campos como touched para mostrar errores de validación
      Object.keys(this.loginForm.controls).forEach(key => {
        const control = this.loginForm.get(key);
        control?.markAsTouched();
      });
    }
  }
}
