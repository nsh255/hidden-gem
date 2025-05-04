import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LayoutNavbarComponent } from './layout-navbar.component';

@Component({
  selector: 'app-layout-shell',
  standalone: true,
  imports: [RouterOutlet, LayoutNavbarComponent],
  templateUrl: './layout-shell.component.html',
  styleUrl: './layout-shell.component.scss'
})
export class LayoutShellComponent {

}
