export interface Product {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  precio: string;
  moneda: 'BOB';
  imagen_url: string | null;
  activo: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface ProductInput {
  nombre: string;
  descripcion: string;
  precio: string;
  slug?: string;
  imagen_url?: string | null;
  activo?: boolean;
}

export interface ProductList {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
}

export interface ProductQuery {
  q?: string;
  activo?: boolean;
  limit: number;
  offset: number;
}
