import { Routes } from '@angular/router';
import { adminGuard, guestGuard } from './auth/auth.guards';
import { companyAdminGuard, companyGuard } from './company/company.guards';
import { productFormLeaveGuard } from './products/product-form.guard';
import { variantLeaveGuard } from './products/variant-page.guard';

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
      { path: 'empresa', loadComponent: () => import('./company/company-page').then(m => m.CompanyPage) },
      { path: 'productos', canActivate: [companyGuard], loadComponent: () => import('./products/product-list').then(m => m.ProductListPage) },
      { path: 'productos/nuevo', canActivate: [companyAdminGuard], canDeactivate: [productFormLeaveGuard], loadComponent: () => import('./products/product-form').then(m => m.ProductFormPage) },
      { path: 'productos/:id/variantes', canActivate: [companyGuard], canDeactivate: [variantLeaveGuard], loadComponent: () => import('./products/variant-page').then(m => m.VariantPage) },
      { path: 'productos/:id/editar', canActivate: [companyAdminGuard], canDeactivate: [productFormLeaveGuard], loadComponent: () => import('./products/product-form').then(m => m.ProductFormPage) },
    ],
  },
  { path: '**', loadComponent: () => import('./layout/not-found-page').then(m => m.NotFoundPage) },
];
