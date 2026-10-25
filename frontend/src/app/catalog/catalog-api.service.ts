import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CatalogList, CatalogProduct, CatalogQuery } from './catalog.models';

@Injectable({ providedIn: 'root' })
export class CatalogApiService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = '/api/catalogo/productos';

  list(query: CatalogQuery): Observable<CatalogList> {
    let params = new HttpParams().set('limit', query.limit).set('offset', query.offset);
    const name = query.q?.trim();
    if (name) params = params.set('q', name);
    return this.http.get<CatalogList>(this.endpoint, { params });
  }

  get(slug: string): Observable<CatalogProduct> {
    return this.http.get<CatalogProduct>(`${this.endpoint}/${encodeURIComponent(slug)}`);
  }
}
