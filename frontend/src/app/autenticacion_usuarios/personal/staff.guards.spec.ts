import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree, provideRouter } from '@angular/router';
import { firstValueFrom, of, type Observable } from 'rxjs';
import { AuthService } from '../autenticacion/auth.service';
import { CompanyService } from '../../organizacion_empresarial/empresa/company.service';
import { staffPermissionGuard } from './staff.guards';

describe('Permisos efectivos y rol exclusivo de CU22', () => {
  async function check(role: string, granted: boolean): Promise<boolean | UrlTree> {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: { ensureSession: () => of({ id: 1 }) } },
        { provide: CompanyService, useValue: {
          ensureForUser: () => of(true),
          active: () => ({ id: 1, rol: role }),
          refreshAccess: () => of({}),
          hasPermission: (code: string) => code === 'analitica.consultar' && granted,
        } },
      ],
    });
    const route = { data: { permission: 'analitica.consultar', requiredRole: 'ADMINISTRADOR' } } as unknown as ActivatedRouteSnapshot;
    return firstValueFrom(TestBed.runInInjectionContext(() =>
      staffPermissionGuard(route, {} as RouterStateSnapshot)) as Observable<boolean | UrlTree>);
  }

  it('impide abrir CU22 por URL a un rol personalizado aunque posea el permiso', async () => {
    const result = await check('OPERADOR', true);
    expect(TestBed.inject(Router).serializeUrl(result as UrlTree)).toBe('/admin/acceso?motivo=permiso');
  });

  it('permite CU22 al administrador empresarial que tiene el permiso', async () => {
    expect(await check('ADMINISTRADOR', true)).toBe(true);
  });

  it('deniega CU22 al administrador empresarial con permiso revocado', async () => {
    const result = await check('ADMINISTRADOR', false);
    expect(TestBed.inject(Router).serializeUrl(result as UrlTree)).toBe('/admin/acceso?motivo=permiso');
  });
});
