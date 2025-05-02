import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-game-list',
  templateUrl: './game-list.component.html',
  styleUrls: ['./game-list.component.css']
})
export class GameListComponent implements OnInit {
  isFavoritesView = false;
  games = [
    { id: 1, title: 'Stardew Valley', image: 'https://via.placeholder.com/150', description: 'Un juego de simulación de agricultura y vida en el campo' },
    { id: 2, title: 'Hollow Knight', image: 'https://via.placeholder.com/150', description: 'Un juego de acción y aventura metroidvania' },
    { id: 3, title: 'Hades', image: 'https://via.placeholder.com/150', description: 'Un juego de acción roguelike de la mitología griega' }
  ];

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.isFavoritesView = this.route.snapshot.url.toString().includes('favorites');
  }
}
