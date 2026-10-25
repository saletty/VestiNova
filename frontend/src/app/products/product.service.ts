import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { Observable } from 'rxjs';
import { Product, ProductInput, ProductList, ProductQuery } from './product.model';

@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/admin/productos';
  readonly notice = signal<string | null>(null);

  list(query: ProductQuery): Observable<ProductList> {
    let params = new HttpParams().set('limit', query.limit).set('offset', query.offset);
    if (query.q) params = params.set('q', query.q);
    if (query.activo !== undefined) params = params.set('activo', query.activo);
    return this.http.get<ProductList>(this.endpoint, { params });
  }

  get(id: number): Observable<Product> {
    return this.http.get<Product>(`${this.endpoint}/${id}`);
  }

  create(product: ProductInput): Observable<Product> {
    return this.http.post<Product>(this.endpoint, product);
  }

  update(id: number, changes: Partial<ProductInput>): Observable<Product> {
    return this.http.patch<Product>(`${this.endpoint}/${id}`, changes);
  }
}
