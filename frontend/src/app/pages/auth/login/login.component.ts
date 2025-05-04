import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';  // Fixed import path

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  isLoading: boolean = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {}

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;
      
      // Get form values
      const email = this.loginForm.value.email;
      const password = this.loginForm.value.password;
      
      console.debug('Attempting login with email:', email);
      
      // Use the correct parameter format for login
      this.authService.login({ email, password })
        .subscribe({
          next: (response) => {
            console.debug('Login successful, navigating to home');
            this.isLoading = false;
            this.router.navigate(['/']);
          },
          error: (error) => {
            this.isLoading = false;
            console.error('Login error:', error);
            
            if (error.status === 401) {
              this.errorMessage = 'Email o contraseña incorrectos. Por favor, intenta de nuevo.';
            } else if (error.message) {
              this.errorMessage = error.message;
            } else {
              this.errorMessage = 'Error al iniciar sesión. Por favor, intenta nuevamente.';
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