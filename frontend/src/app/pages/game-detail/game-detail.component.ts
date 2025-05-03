import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Location } from '@angular/common';

// Interfaz para el detalle del juego (se usará eventualmente con el servicio)
interface GameDetail {
  id: number;
  name: string;
  imageUrl: string;
  description: string;
  genres: string[];
  releaseDate: Date;
  price: number;
  rating: string;
  storeUrl?: string;
  screenshots?: string[];
}

// Interfaz para juegos similares
interface SimilarGame {
  id: number;
  name: string;
  imageUrl: string;
  genres: string[];
}

@Component({
  selector: 'app-game-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './game-detail.component.html',
  styleUrl: './game-detail.component.scss'
})
export class GameDetailComponent implements OnInit {
  gameId: number | null = null;
  game: GameDetail | null = null;
  similarGames: SimilarGame[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  isFavorite: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private location: Location
  ) { }

  ngOnInit(): void {
    // Obtener el ID del juego de la URL
    this.route.paramMap.subscribe(params => {
      const idParam = params.get('id');
      if (idParam) {
        this.gameId = parseInt(idParam, 10);
        this.loadGameDetails(this.gameId);
      } else {
        this.errorMessage = 'No se pudo encontrar el ID del juego.';
        this.isLoading = false;
      }
    });
  }

  /**
   * Carga los detalles del juego (simulado por ahora)
   * En el futuro, esto usará un servicio para obtener datos reales
   */
  loadGameDetails(gameId: number): void {
    // Simulación de carga
    setTimeout(() => {
      // Datos de ejemplo - En el futuro, estos vendrán del servicio
      this.game = {
        id: gameId,
        name: 'Hollow Knight',
        imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/367520/header.jpg',
        description: `
          <p>Hollow Knight es una aventura de acción clásica en 2D ambientada en un vasto mundo interconectado. 
          Explora cavernas sinuosas, ciudades antiguas y páramos mortales. Combate contra criaturas corrompidas, 
          hazte amigo de bichos extraños y resuelve los antiguos misterios que yacen en el corazón del reino.</p>
          
          <p>- Explora vastos mundos interconectados<br>
          - Conoce a extraños insectos y bestias misteriosas<br>
          - Evoluciona con poderosos hechizos y habilidades<br>
          - Personaliza tu experiencia con amuletos para aumentar las habilidades del Caballero<br>
          - Escapa de las abrumadoras presencias que habitan las profundidades</p>
        `,
        genres: ['Metroidvania', 'Souls-like', 'Plataformas', 'Indie', 'Aventura'],
        releaseDate: new Date('2017-02-24'),
        price: 14.99,
        rating: '9.5',
        storeUrl: 'https://store.steampowered.com/app/367520/Hollow_Knight/',
        screenshots: [
          'https://cdn.akamai.steamstatic.com/steam/apps/367520/ss_89b986b8b7474773aae38b5c5f37412212a7478f.jpg',
          'https://cdn.akamai.steamstatic.com/steam/apps/367520/ss_32af31e92a599a71937171de4588963f1be7b5bc.jpg',
          'https://cdn.akamai.steamstatic.com/steam/apps/367520/ss_b01aee735c14160ea0c20b9b28d31493e969ec73.jpg',
          'https://cdn.akamai.steamstatic.com/steam/apps/367520/ss_12ab4d4681375a0cd6c42e0962874ede93c9340c.jpg'
        ]
      };

      // Juegos similares de ejemplo
      this.similarGames = [
        {
          id: 1,
          name: 'Celeste',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/504230/header.jpg',
          genres: ['Plataformas', 'Indie', 'Difícil']
        },
        {
          id: 2,
          name: 'Dead Cells',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/588650/header.jpg',
          genres: ['Roguelike', 'Metroidvania', 'Acción']
        },
        {
          id: 3,
          name: 'Hades',
          imageUrl: 'https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg',
          genres: ['Roguelike', 'Acción', 'Indie']
        }
      ];

      this.isLoading = false;
    }, 1000); // Simulamos 1 segundo de carga
  }

  /**
   * Toggle para añadir/quitar de favoritos
   */
  toggleFavorite(): void {
    this.isFavorite = !this.isFavorite;
    // En el futuro, llamaremos a un servicio para guardar este estado
    console.log(`Juego ${this.isFavorite ? 'añadido a' : 'eliminado de'} favoritos`);
  }

  /**
   * Navegar a la página anterior
   */
  goBack(): void {
    this.location.back();
  }

  /**
   * Navegar a otro juego
   */
  navigateToGame(gameId: number): void {
    // Navegar a otro juego, recargando el componente
    this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
      this.router.navigate(['/game', gameId]);
    });
  }
}
