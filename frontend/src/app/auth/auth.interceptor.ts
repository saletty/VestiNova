import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const privateApi = request.url.startsWith('/api/admin/') || ['/api/auth/me', '/api/auth/logout'].includes(request.url);
  const token = auth.token();
  const authorized = privateApi && token
    ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : request;
  return next(authorized).pipe(catchError((error: unknown) => {
    if (error instanceof HttpErrorResponse && error.status === 401 && privateApi && token !== null && token === auth.token()) {
      auth.invalidate();
      void router.navigate(['/admin/login'], { queryParams: { motivo: 'sesion' } });
    }
    return throwError(() => error);
  }));
};
