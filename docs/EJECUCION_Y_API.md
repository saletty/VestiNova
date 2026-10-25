# Ejecución y conexión de las aplicaciones

Estado revisado el 25 de octubre de 2026. El backend y frontend nuevos permanecen en `vestinova-mvp`; no se movió código ni se modificó la base existente del MVP.

## Backend y web actuales

En una terminal PowerShell:

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8001
```

En otra terminal:

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp\frontend'
npm.cmd start
```

No iniciar otra instancia si esos puertos ya los atiende este proyecto. Acceso web: http://127.0.0.1:4201/admin/login; productos: http://127.0.0.1:4201/admin/productos; documentación API: http://127.0.0.1:8001/docs. La comprobación http://127.0.0.1:8001/api/health/db consulta la base `vestinova_mvp`.

En esta computadora ya se configuró el `.env` privado, se aplicaron migraciones y se creó el administrador. No volver a configurar el secreto ni recrear cuentas para publicar el código. PostgreSQL y sus datos no se suben a GitHub.

Para una instalación nueva, seguir el [README](../README.md): crear el entorno virtual, instalar `requirements.lock.txt`, ejecutar `configure_local`, `init_db` y `create_admin`; en frontend ejecutar `npm.cmd ci`. Cada integrante introduce sus propias credenciales localmente. No copiar ni compartir el `.env` del otro integrante.

## URL según el cliente

| Cliente | Base del backend nuevo | Condición |
| --- | --- | --- |
| Angular en la computadora | `/api` | `frontend/proxy.conf.json` envía a `http://127.0.0.1:8001`. |
| Navegador que llama directamente a la API | `http://127.0.0.1:8001/api` desde la computadora | Su origen debe estar en `CORS_ORIGINS`; por defecto se permiten `http://127.0.0.1:4201` y `http://localhost:4201`. |
| Android Emulator oficial | `http://10.0.2.2:8001/api` | Ese alias llega al loopback de la computadora; el backend puede seguir escuchando en `127.0.0.1`. |
| Android físico con USB y redirección ADB | `http://127.0.0.1:8001/api` | Primero configurar `adb reverse`; sin esa redirección, localhost es el teléfono. |
| App nativa en teléfono por Wi-Fi | `http://IP_LAN_DE_LA_PC:8001/api` | Misma red, backend escuchando en la interfaz de red y puerto accesible. |

Android documenta `10.0.2.2` como alias del loopback del anfitrión; no debe sustituirse por localhost dentro del emulador. [Referencia oficial](https://developer.android.com/studio/run/emulator-networking-address).

En el futuro móvil, acordar que la base **incluye `/api`** y que los servicios añaden `/catalogo/productos`, por ejemplo. No añadir `/api` dos veces. El móvil heredado construye otras rutas y no es compatible con esta convención sin adaptación.

## Pruebas por Wi-Fi

Solo cuando se decida probar un cliente móvil adaptado, iniciar manualmente el backend de desarrollo con:

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8001
```

Consultar la dirección IPv4 del adaptador Wi-Fi activo con `ipconfig` y utilizarla en el teléfono. `0.0.0.0` es una dirección de escucha, no la URL que se escribe en la app. Verificar que ambos dispositivos estén en la misma red y permitir el puerto de desarrollo en el firewall para esa red si fuera necesario. No se cambió automáticamente el firewall ni se abrió este servicio a la red durante la revisión.

La conexión a PostgreSQL debe seguir siendo local y apuntando a `vestinova_mvp`; no cambiar `DATABASE_URL` por la IP del teléfono. Exponer HTTP para una prueba de LAN no implica exponer PostgreSQL.

Para consultar Angular desde el navegador del teléfono, puede iniciarse su servidor con:

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp\frontend'
npm.cmd start -- --host 0.0.0.0 --port 4201
```

Abrir `http://IP_LAN_DE_LA_PC:4201`. Si se utiliza el proxy `/api`, Angular reenvía las llamadas desde la computadora al backend local; no hace falta publicar también el puerto 8001 para esa prueba web. Si un navegador o Flutter web llama directamente al backend, configurar su origen exacto mediante `CORS_ORIGINS`, sin sustituir los valores privados del resto del `.env`. Flutter nativo no utiliza las restricciones CORS del navegador.

## Android físico por USB

Con Android SDK Platform Tools instalado, depuración USB habilitada y un dispositivo autorizado:

```powershell
adb devices
$AndroidDeviceId = Read-Host 'Identificador del dispositivo mostrado por adb'
adb -s $AndroidDeviceId reverse tcp:8001 tcp:8001
```

Después la app adaptada puede usar `http://127.0.0.1:8001/api`. Esa excepción se debe a ADB, no a que localhost normalmente apunte a la PC. La configuración de red de Android y el permiso INTERNET deben permitir el tráfico de desarrollo. [ADB reverse](https://developer.android.com/tools/adb).

## Móvil encontrado: límites y comandos de referencia

La carpeta real es `fashionstore-mobile/fashionstore-mobile`, fuera del MVP. Es Flutter heredado, con archivos esenciales eliminados y SDK Dart instalado inferior al mínimo declarado. **No hay un comando que haga ejecutable el árbol actual sin resolver primero esos problemas.** No se restauraron archivos ni se actualizaron dependencias durante esta revisión.

Comandos que correspondería utilizar después de acordar procedencia, alcance y recuperación/adaptación:

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\fashionstore-mobile\fashionstore-mobile'
flutter --version
flutter doctor -v
flutter pub get
flutter analyze
flutter test
flutter devices
```

El historial de `ApiConfig` usaba `--dart-define=API_BASE_URL=...`; su archivo actual está eliminado. Para una implementación aprobada que conserve ese mecanismo, la ejecución en un emulador Android sería de la forma siguiente, **después de adaptar rutas y DTOs**:

```powershell
$AndroidEmulatorId = Read-Host 'Identificador del emulador mostrado por flutter devices'
flutter run -d $AndroidEmulatorId '--dart-define=API_BASE_URL=http://10.0.2.2:8001/api'
```

No ejecutar ese ejemplo como prueba de integración del móvil actual. iOS requiere macOS/Xcode para compilar y configurar correctamente red de desarrollo, permisos y firma; no se verificó una compilación iOS en esta computadora Windows. Android release tampoco se validó: el proyecto heredado todavía firma con debug y su manifest principal no declara INTERNET. Los detalles y las incompatibilidades están en [REVISION_MOVIL.md](REVISION_MOVIL.md).

## Alcance académico

No se encontró un enunciado o rúbrica del segundo parcial en el workspace. Los documentos del MVP y los números de casos en el código heredado no sustituyen esos requisitos. Falta confirmar qué funciones debe realizar la aplicación móvil; no se acredita la entrega móvil por tener una carpeta Flutter o por adaptar la web a pantallas pequeñas.
