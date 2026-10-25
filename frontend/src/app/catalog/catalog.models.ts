import type { Product, ProductList } from '../products/product.model';

// El contrato público comparte la respuesta de producto, sin operaciones administrativas.
export type CatalogProduct = Product;
export type CatalogList = ProductList;

export interface CatalogQuery {
  q?: string;
  limit: number;
  offset: number;
}
