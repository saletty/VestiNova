import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'vn-catalog-layout',
  imports: [RouterLink, RouterOutlet],
  template: `
    <div class="catalog-shell">
      <a class="catalog-skip" href="#catalog-content">Saltar al contenido</a>
      <header class="catalog-header">
        <a class="catalog-brand" routerLink="/catalogo" aria-label="VestiNova · Catálogo">
          <span class="catalog-brand__seal" aria-hidden="true">VN</span>
          <span>VestiNova</span>
        </a>
        <nav aria-label="Navegación del catálogo">
          <a routerLink="/catalogo">Catálogo de prendas</a>
        </nav>
      </header>
      <main id="catalog-content" class="catalog-main" tabindex="-1"><router-outlet /></main>
      <footer class="catalog-footer"><span>VestiNova</span><span>Catálogo de prendas</span></footer>
    </div>
  `,
  styleUrl: './catalog.css',
})
export class CatalogLayout {}
