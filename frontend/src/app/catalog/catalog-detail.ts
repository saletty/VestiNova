import { HttpErrorResponse } from '@angular/common/http';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Observable, Subject, catchError, distinctUntilChanged, map, of, startWith, switchMap } from 'rxjs';
import { CatalogApiService } from './catalog-api.service';
import { CatalogImage } from './catalog-image';
import { CatalogProduct } from './catalog.models';

@Component({
  selector: 'vn-catalog-detail',
  imports: [RouterLink, CatalogImage],
  templateUrl: './catalog-detail.html',
  styleUrl: './catalog.css',
})
export class CatalogDetailPage {
  private readonly api = inject(CatalogApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly retries = new Subject<void>();
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly notFound = signal(false);
  readonly product = signal<CatalogProduct | null>(null);

  constructor() {
    this.route.paramMap.pipe(
      map(params => params.get('slug')),
      distinctUntilChanged(),
      switchMap(slug => this.retries.pipe(
        startWith(undefined),
        switchMap(() => this.load(slug)),
      )),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(product => {
      this.product.set(product);
      this.loading.set(false);
    });
  }

  retry(): void {
    if (!this.loading() && this.error()) this.retries.next();
  }

  private load(slug: string | null): Observable<CatalogProduct | null> {
    this.loading.set(true);
    this.error.set(null);
    this.notFound.set(false);
    this.product.set(null);
    if (!slug) {
      this.notFound.set(true);
      return of(null);
    }
    return this.api.get(slug).pipe(catchError((error: unknown) => {
      const status = error instanceof HttpErrorResponse ? error.status : undefined;
      if (status === 404) {
        this.notFound.set(true);
      } else {
        this.error.set(status === 0
          ? 'No pudimos conectar con el catálogo. Comprueba tu conexión e inténtalo nuevamente.'
          : status === 403
            ? 'No tienes permiso para consultar este producto.'
            : 'No pudimos cargar el producto. Inténtalo nuevamente.');
      }
      return of(null);
    }));
  }
}
