import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule, RouterModule],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss'
})
export class AuthComponent implements OnInit {
  loginForm: FormGroup;
  errorMessage: string | null = null;
  isLoading = false;
  registrationSuccess = false;

  constructor(
    private fb: FormBuilder, 
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // Verificar si viene de un registro exitoso o tiene URL de retorno
    this.route.queryParams.subscribe(params => {
      if (params['registered'] === 'true') {
        this.registrationSuccess = true;
        
        // Si se proporciona un email, rellenarlo automáticamente
        if (params['email']) {
          this.loginForm.patchValue({
            email: params['email']
          });
        }
      }
      
      // Guardar la URL de retorno si existe
      if (params['returnUrl']) {
        localStorage.setItem('returnUrl', params['returnUrl']);
      }
    });
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;
      
      // Get values safely using the get method
      const email = this.loginForm.get('email')?.value || '';
      const password = this.loginForm.get('password')?.value || '';
      
      console.debug('Auth component submitting login for:', email);
      
      // Add clear debugging to track the login flow
      console.debug('Login data being sent:', { email, password: '********' });
      
      this.authService.login({ email, password })
        .subscribe({
          next: (response) => {
            console.debug('Login successful in auth component, response:', response);
            this.isLoading = false;
            
            // Redirigir a la URL de retorno o a la página principal
            const returnUrl = localStorage.getItem('returnUrl') || '/';
            localStorage.removeItem('returnUrl');
            this.router.navigateByUrl(returnUrl);
          },
          error: (error: any) => {
            this.isLoading = false;
            console.error('Login error in auth component:', error);
            
            if (error.status === 401) {
              this.errorMessage = 'Credenciales incorrectas. Por favor, verifica tu email y contraseña.';
            } else if (error.status === 422) {
              this.errorMessage = 'Formato de datos incorrecto. Por favor, verifica tu email y contraseña.';
            } else if (error.error && error.error.detail) {
              this.errorMessage = error.error.detail;
            } else if (error instanceof Error) {
              this.errorMessage = error.message;
            } else {
              this.errorMessage = 'Error al iniciar sesión. Por favor, inténtalo de nuevo.';
            }
          }
        });
    } else {
      // Mark all fields as touched to show validation errors
      Object.keys(this.loginForm.controls).forEach(key => {
        const control = this.loginForm.get(key);
        control?.markAsTouched();
      });
    }
  }
}
