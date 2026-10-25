import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { authInterceptor } from './auth.interceptor';
import { AuthService, SESSION_KEY } from './auth.service';

describe('Autorización HTTP del MVP', () => {
  let http: HttpTestingController;
  let client: HttpClient;
  beforeEach(() => {
    sessionStorage.setItem(SESSION_KEY, 'token-de-prueba');
    TestBed.configureTestingModule({ providers: [provideHttpClient(withInterceptors([authInterceptor])), provideHttpClientTesting(), provideRouter([])] });
    http = TestBed.inject(HttpTestingController);
    client = TestBed.inject(HttpClient);
  });
  afterEach(() => { http.verify(); sessionStorage.clear(); vi.restoreAllMocks(); });
  it('añade Bearer únicamente a la API propia y no al login ni URLs externas', () => {
    client.get('/api/admin/productos').subscribe();
    const own = http.expectOne('/api/admin/productos');
    expect(own.request.headers.get('Authorization')).toBe('Bearer token-de-prueba');
    own.flush([]);
    client.get('https://externo.test/imagen').subscribe();
    const external = http.expectOne('https://externo.test/imagen');
    expect(external.request.headers.has('Authorization')).toBe(false);
    external.flush({});
    client.get('/api/catalogo/productos').subscribe();
    const catalog = http.expectOne('/api/catalogo/productos');
    expect(catalog.request.headers.has('Authorization')).toBe(false);
    catalog.flush({ items: [] });
    TestBed.inject(AuthService).login({ correo: 'admin@vestinova.test', password: 'prueba' }).subscribe({ error: () => undefined });
    const login = http.expectOne('/api/auth/login');
    expect(login.request.headers.has('Authorization')).toBe(false);
    login.flush({}, { status: 401, statusText: 'Unauthorized' });
  });
  it('un 401 privado invalida la sesión y redirige al acceso', () => {
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
    client.get('/api/admin/productos').subscribe({ error: () => undefined });
    http.expectOne('/api/admin/productos').flush({}, { status: 401, statusText: 'Unauthorized' });
    expect(TestBed.inject(AuthService).token()).toBeNull();
    expect(navigate).toHaveBeenCalledWith(['/admin/login'], { queryParams: { motivo: 'sesion' } });
  });
  it('un 403 no borra una sesión válida', () => {
    client.get('/api/admin/productos').subscribe({ error: () => undefined });
    http.expectOne('/api/admin/productos').flush({}, { status: 403, statusText: 'Forbidden' });
    expect(TestBed.inject(AuthService).token()).toBe('token-de-prueba');
  });
});
