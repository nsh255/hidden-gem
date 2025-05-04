import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

// Validador personalizado para verificar que las contraseñas coincidan
function passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password');
  const confirmPassword = control.get('confirmPassword');

  if (password && confirmPassword && password.value !== confirmPassword.value) {
    return { passwordMismatch: true };
  }

  return null;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent {
  registerForm: FormGroup;
  errorMessage: string | null = null;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Inicializar el formulario con validaciones
    this.registerForm = this.fb.group({
      nick: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      precio_max: [20.0] // Valor por defecto para el precio máximo
    }, { validators: passwordMatchValidator });
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;

      // Extraer datos del formulario
      const { nick, email, password } = this.registerForm.value;

      // Usar el método de registro
      this.authService.register(nick, email, password)
        .subscribe({
          next: (response) => {
            this.isLoading = false;
            console.log('Registro exitoso', response);
            // No necesitamos hacer navegación aquí, ya que el servicio lo manejará
          },
          error: (error) => {
            this.isLoading = false;
            if (error instanceof Error) {
              this.errorMessage = error.message;
            } else if (error.error?.detail) {
              this.errorMessage = error.error.detail;
            } else {
              this.errorMessage = 'Error en el registro. Por favor, inténtalo de nuevo.';
            }
            console.error('Error de registro', error);
          }
        });
    } else {
      // Marcar todos los campos como touched para mostrar errores de validación
      Object.keys(this.registerForm.controls).forEach(key => {
        const control = this.registerForm.get(key);
        control?.markAsTouched();
      });

      // Si hay error en las contraseñas, mostrar mensaje específico
      if (this.registerForm.hasError('passwordMismatch')) {
        this.errorMessage = 'Las contraseñas no coinciden';
      } else {
        this.errorMessage = 'Por favor, completa correctamente todos los campos requeridos';
      }
    }
  }
}
