import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'preferred-theme';
  private isDarkMode = new BehaviorSubject<boolean>(false);
  
  // Observable for components to subscribe to
  public isDarkMode$ = this.isDarkMode.asObservable();
  
  constructor() { 
    this.loadThemeFromStorage();
  }
  
  /**
   * Toggle between light and dark theme
   */
  toggleTheme(): void {
    const newMode = !this.isDarkMode.value;
    this.setDarkMode(newMode);
  }
  
  /**
   * Set specific theme mode
   */
  setDarkMode(isDark: boolean): void {
    // Update state
    this.isDarkMode.next(isDark);
    
    // Update DOM and storage
    this.updateTheme(isDark);
    localStorage.setItem(this.THEME_KEY, isDark ? 'dark' : 'light');
  }
  
  /**
   * Get current theme mode
   */
  isDark(): boolean {
    return this.isDarkMode.value;
  }
  
  /**
   * Initialize theme from user's stored preference or system preference
   */
  private loadThemeFromStorage(): void {
    // Check localStorage
    const savedTheme = localStorage.getItem(this.THEME_KEY) as Theme | null;
    
    // If theme is saved in localStorage, use it
    if (savedTheme) {
      const isDark = savedTheme === 'dark';
      this.isDarkMode.next(isDark);
      this.updateTheme(isDark);
      return;
    }
    
    // Otherwise check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      this.isDarkMode.next(true);
      this.updateTheme(true);
    }
    
    // Add listener for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
      // Only apply system theme changes if user hasn't set a preference
      if (!localStorage.getItem(this.THEME_KEY)) {
        const isDark = event.matches;
        this.isDarkMode.next(isDark);
        this.updateTheme(isDark);
      }
    });
  }
  
  /**
   * Apply theme to DOM
   */
  private updateTheme(isDark: boolean): void {
    // Remove both theme classes first
    document.body.classList.remove('light-theme', 'dark-theme');
    
    // Add the appropriate theme class
    document.body.classList.add(isDark ? 'dark-theme' : 'light-theme');
  }
}
