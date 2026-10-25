import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Subject, catchError, of, switchMap, tap } from 'rxjs';
import { productError } from './product-errors';
import { ProductList, ProductQuery } from './product.model';
import { ProductService } from './product.service';

@Component({
  selector: 'app-product-list',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './product-list.html',
  styleUrl: './products.css',
})
export class ProductListPage {
  private readonly products = inject(ProductService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly requests = new Subject<ProductQuery>();
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly notice = this.products.notice;
  readonly result = signal<ProductList>({ items: [], total: 0, limit: 20, offset: 0 });
  readonly filters = new FormGroup({
    q: new FormControl('', { nonNullable: true, validators: [Validators.maxLength(120)] }),
    activo: new FormControl('', { nonNullable: true }),
  });
  private currentQuery: ProductQuery = { limit: 20, offset: 0 };

  constructor() {
    this.requests.pipe(
      tap(() => { this.loading.set(true); this.error.set(null); }),
      switchMap(query => this.products.list(query).pipe(
        catchError(error => { this.error.set(productError(error)); return of(null); }),
      )),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(response => {
      this.loading.set(false);
      if (response) this.result.set(response);
    });
  }

  ngOnInit(): void { this.reload(); }

  search(): void {
    if (this.filters.invalid) { this.filters.markAllAsTouched(); return; }
    const filters = this.filters.getRawValue();
    this.currentQuery = {
      q: filters.q.trim() || undefined,
      activo: filters.activo === '' ? undefined : filters.activo === 'true',
      limit: 20, offset: 0,
    };
    this.reload();
  }

  clear(): void { this.filters.reset(); this.search(); }
  reload(): void { this.requests.next({ ...this.currentQuery }); }

  page(direction: -1 | 1): void {
    if (this.loading()) return;
    const next = this.currentQuery.offset + direction * this.currentQuery.limit;
    if (next < 0 || next >= this.result().total) return;
    this.currentQuery = { ...this.currentQuery, offset: next };
    this.reload();
  }

  first(): number { return this.result().total === 0 ? 0 : this.result().offset + 1; }
  last(): number { return Math.min(this.result().offset + this.result().items.length, this.result().total); }
  hasFilters(): boolean { return Boolean(this.currentQuery.q || this.currentQuery.activo !== undefined); }
}
