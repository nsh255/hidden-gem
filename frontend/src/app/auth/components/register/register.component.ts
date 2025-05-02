import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService, RegisterData } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  errorMessage: string = '';
  successMessage: string = '';
  loading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      nickname: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      max_price: [29.99, [Validators.required, Validators.min(0)]]
    }, { validators: this.passwordMatchValidator });
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');

    if (password && confirmPassword && password.value !== confirmPassword.value) {
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit(): void {
    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    const registerData: RegisterData = {
      email: this.registerForm.value.email,
      password: this.registerForm.value.password,
      nickname: this.registerForm.value.nickname,
      max_price: this.registerForm.value.max_price
    };

    this.authService.register(registerData).subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = 'Registro exitoso. Redirigiendo al login...';
        setTimeout(() => {
          this.router.navigate(['/auth/login']);
        }, 2000);
      },
      error: (error) => {
        this.loading = false;
        if (error.status === 400) {
          this.errorMessage = error.error.detail || 'Error en el registro';
        } else {
          this.errorMessage = 'Error en el servidor. Intente más tarde.';
        }
      }
    });
  }

  // Getters para acceso fácil en la plantilla
  get email() { return this.registerForm.get('email'); }
  get nickname() { return this.registerForm.get('nickname'); }
  get password() { return this.registerForm.get('password'); }
  get confirmPassword() { return this.registerForm.get('confirmPassword'); }
  get max_price() { return this.registerForm.get('max_price'); }
  get passwordsMatch() {
    return this.registerForm.hasError('passwordMismatch') && 
           this.password?.dirty && 
           this.confirmPassword?.dirty;
  }
}
