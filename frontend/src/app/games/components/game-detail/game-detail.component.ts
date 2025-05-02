import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-game-detail',
  templateUrl: './game-detail.component.html',
  styleUrls: ['./game-detail.component.css']
})
export class GameDetailComponent implements OnInit {
  gameId: number;
  game = {
    id: 1,
    title: 'Stardew Valley',
    image: 'https://via.placeholder.com/600x400',
    description: 'Un juego de simulación de agricultura y vida en el campo',
    developer: 'ConcernedApe',
    releaseDate: '2016-02-26',
    genres: ['Simulación', 'RPG', 'Indie'],
    price: 14.99,
    rating: 4.8
  };

  constructor(private route: ActivatedRoute) {
    this.gameId = 0;
  }

  ngOnInit(): void {
    this.gameId = +this.route.snapshot.paramMap.get('id')!;
    // Aquí se cargarían los datos del juego desde un servicio
  }
}
