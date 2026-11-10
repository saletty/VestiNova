import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of, switchMap } from 'rxjs';
import { AuthService } from '../../autenticacion_usuarios/autenticacion/auth.service';
import { CompanyService } from './company.service';

export const companyGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => companies.active() ? true : router.createUrlTree(['/admin/empresa']))) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};

/** Entrada administrativa según el rol efectivo de la empresa seleccionada.
 * Evita enviar a Cajeros y Encargados a pantallas de edición de productos.
 */
export const adminHomeGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => {
      if (!user) return of(router.createUrlTree(['/admin/login']));
      if (user.es_superadministrador) return of(router.createUrlTree(['/admin/plataforma']));
      return companies.ensureForUser(user.id).pipe(map(() => {
        const current = companies.active();
        if (!current) return router.createUrlTree(['/admin/empresa']);
        if (current.rol === 'CAJERO') return router.createUrlTree(['/admin/caja']);
        if (current.rol === 'ENCARGADO_SUCURSAL') {
          return router.createUrlTree(['/admin/atencion-reservas']);
        }
        if (companies.canViewProducts()) return router.createUrlTree(['/admin/productos']);
        if (companies.hasPermission('catalogo.consultar')) {
          return router.createUrlTree(['/admin/catalogo-consulta']);
        }
        return router.createUrlTree(['/admin/acceso']);
      }));
    }),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};

export const companyAdminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => {
      if (!companies.active()) return router.createUrlTree(['/admin/empresa']);
      return companies.canManage() ? true : router.createUrlTree([companies.hasPermission('catalogo.consultar') ? '/admin/catalogo-consulta' : '/admin/acceso'], { queryParams: { motivo: 'permiso' } });
    })) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};

export const productsGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => {
      if (!companies.active()) return router.createUrlTree(['/admin/empresa']);
      return companies.canViewProducts() ? true : router.createUrlTree(['/admin/acceso']);
    })) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};

export const cashierGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => {
      const company = companies.active();
      if (!company) return router.createUrlTree(['/admin/empresa']);
      return ['CAJERO', 'ENCARGADO_SUCURSAL'].includes(company.rol)
        ? true : router.createUrlTree(['/admin/acceso'], { queryParams: { motivo: 'permiso' } });
    })) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};


/** CU13: solo Encargados pueden registrar conciliaciones comerciales. */
export const managerGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => {
      const current = companies.active();
      if (!current) return router.createUrlTree(['/admin/empresa']);
      return current.rol === 'ENCARGADO_SUCURSAL'
        ? true : router.createUrlTree(['/admin/acceso'], { queryParams: { motivo: 'permiso' } });
    })) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};

/** Reservas y entrega de compras: aún no tienen códigos de permiso propios en CU01.
 * Mantener acceso restringido a los tres perfiles operativos reconocidos por el backend.
 */
export const operationalStaffGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const companies = inject(CompanyService);
  const router = inject(Router);
  return auth.ensureSession().pipe(
    switchMap(user => user ? companies.ensureForUser(user.id).pipe(map(() => {
      const company = companies.active();
      if (!company) return router.createUrlTree(['/admin/empresa']);
      return ['ADMINISTRADOR', 'ENCARGADO_SUCURSAL', 'CAJERO'].includes(company.rol)
        ? true : router.createUrlTree(['/admin/acceso'], { queryParams: { motivo: 'permiso' } });
    })) : of(router.createUrlTree(['/admin/login']))),
    catchError(() => of(router.createUrlTree(['/admin/empresa']))),
  );
};
