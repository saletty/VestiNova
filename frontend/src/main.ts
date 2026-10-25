import { bootstrapApplication } from '@angular/platform-browser';
import { App } from './app/app';
import { appConfig } from './app/app.config';

bootstrapApplication(App, appConfig).catch(() => {
  document.body.textContent = 'No se pudo iniciar VestiNova. Recarga la página e inténtalo otra vez.';
});
