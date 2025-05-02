import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  featuredGames = [
    { id: 1, title: 'Stardew Valley', image: 'https://via.placeholder.com/300x200', description: 'Un juego de simulación de agricultura y vida en el campo' },
    { id: 2, title: 'Hollow Knight', image: 'https://via.placeholder.com/300x200', description: 'Un juego de acción y aventura metroidvania' },
    { id: 3, title: 'Hades', image: 'https://via.placeholder.com/300x200', description: 'Un juego de acción roguelike de la mitología griega' }
  ];
}
