import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.scss'
})
export class UserProfileComponent implements OnInit {
  profileForm!: FormGroup;
  user: any = null;
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isLoading = false;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private userService: UserService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    // Get user data
    this.user = this.authService.getUserData();
    
    // Check if user is logged in
    if (!this.authService.isLoggedIn()) {
      console.error('User is not logged in, redirecting to login page');
      this.errorMessage = 'Sesión no válida. Por favor, inicia sesión nuevamente.';
      setTimeout(() => {
        this.router.navigate(['/auth']);
      }, 3000);
      return;
    }
    
    if (!this.user) {
      console.error('No user data found, redirecting to auth page');
      this.router.navigate(['/auth']);
      return;
    }
    
    console.debug('User data loaded:', this.user);
    
    // Initialize form with current values
    this.profileForm = this.fb.group({
      nick: [this.user.nick, [Validators.required, Validators.minLength(3)]],
      precio_max: [this.user.precio_max || 20, [Validators.required, Validators.min(0), Validators.max(100)]]
    });
  }
  
  onSubmit(): void {
    if (this.profileForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;
      this.successMessage = null;
      
      const { nick, precio_max } = this.profileForm.value;
      console.debug('Submitting form with values:', { nick, precio_max });
      
      // Check if token exists
      if (!this.authService.getToken()) {
        this.errorMessage = 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.';
        this.isLoading = false;
        return;
      }
      
      this.userService.updateUserProfile({ nick, precio_max })
        .subscribe({
          next: (response) => {
            this.isLoading = false;
            this.successMessage = 'Perfil actualizado correctamente';
            
            // Update the stored user data
            this.user = { ...this.user, nick, precio_max };
            
            // Auto-hide success message after 3 seconds
            setTimeout(() => {
              this.successMessage = null;
            }, 3000);
          },
          error: (error) => {
            this.isLoading = false;
            this.errorMessage = error.message || 'Error al actualizar el perfil';
            console.error('Error updating profile:', error);
            
            // If it's an authentication error, redirect to login
            if (error.message.includes('sesión') || error.message.includes('autenti')) {
              setTimeout(() => {
                this.router.navigate(['/auth']);
              }, 3000);
            }
          }
        });
    } else {
      // Mark all fields as touched to show validation errors
      Object.keys(this.profileForm.controls).forEach(key => {
        const control = this.profileForm.get(key);
        control?.markAsTouched();
      });
    }
  }
}
