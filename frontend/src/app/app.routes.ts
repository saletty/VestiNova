import { Routes } from '@angular/router';
import { adminGuard, guestGuard } from './auth/auth.guards';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'admin/productos' },
  {
    path: 'admin/login', canActivate: [guestGuard],
    loadComponent: () => import('./auth/login-page').then(m => m.LoginPage),
  },
  {
    path: 'admin', canActivate: [adminGuard], canActivateChild: [adminGuard],
    loadComponent: () => import('./layout/admin-layout').then(m => m.AdminLayout),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'productos' },
      { path: 'productos', loadComponent: () => import('./products/product-list').then(m => m.ProductListPage) },
      { path: 'productos/nuevo', loadComponent: () => import('./products/product-form').then(m => m.ProductFormPage) },
      { path: 'productos/:id/editar', loadComponent: () => import('./products/product-form').then(m => m.ProductFormPage) },
    ],
  },
  { path: '**', loadComponent: () => import('./layout/not-found-page').then(m => m.NotFoundPage) },
];
