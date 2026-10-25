# Revisión del móvil encontrado

Revisión estática del 25 de octubre de 2026. No se movieron, copiaron, restauraron ni modificaron archivos del móvil; tampoco se ejecutaron sus operaciones ni se contactó un backend heredado.

## Carpeta y procedencia

Única candidata encontrada dentro de este espacio: `fashionstore-mobile/fashionstore-mobile`, hermana de `vestinova-mvp`. Tiene repositorio Git propio en `.git`, rama `main`, 16 commits alcanzables desde HEAD y 21 contando todas las referencias locales; HEAD `f1f7239` (22 de septiembre de 2026).

El remoto saneado es `https://github.com/dilom21/fashionstore-mobile.git`. El historial atribuye commits a los nombres `dilom21` y `harxld069`; el README histórico se titula «VANTER MEN — App móvil de CLIENTES», el paquete es `fashionstore_mobile` y los identificadores Android/iOS conservan Fashionstore. Son evidencias de que corresponde al proyecto heredado, no a la implementación nueva de VestiNova. Los metadatos Git no prueban por sí solos la autoría legal de todo el contenido. No se encontró un archivo de licencia del proyecto en el árbol actual ni en HEAD; la autorización de reutilización y atribución requiere aclaración antes de incorporarlo.

**No está incorporado al repositorio del MVP.** La propuesta `vestinova-mvp/mobile/` queda reservada para la decisión posterior. Copiar allí su `.git` crearía un repositorio anidado; añadirlo desde el Git padre puede registrar un gitlink en lugar de todos sus archivos. No se debe borrar `.git` para evitar esa advertencia ni importar el móvil automáticamente.

## Tecnología y estado real

- Flutter/Dart, aplicación cliente por funcionalidades en `lib/features`; servicios HTTP y modelos Dart, con navegación imperativa `Navigator`.
- Plataformas generadas: Android, iOS, web, Windows, macOS y Linux. Su presencia no acredita que todas compilen o funcionen.
- `pubspec.yaml`: Dart `^3.13.2`; `pubspec.lock`: Dart `>=3.13.2 <4.0.0`, Flutter `>=3.44.0`.
- Dependencias bloqueadas principales: `http 1.6.0`, `flutter_secure_storage 11.1.1`, `flutter_stripe 14.0.0`, `camera 0.12.1`, `pdf 3.13.1`, `printing 5.15.1`, `cupertino_icons 1.0.9`; pruebas Flutter y `flutter_lints 6.0.0`.
- Android declara Java/JVM 17, Android Gradle Plugin 9.1.0, Kotlin 2.4.0, MediaPipe Tasks Vision 1.0.0 y CameraX 1.6.2. Las versiones efectivas de compilación/minSdk se delegan a Flutter. Release todavía utiliza la firma de debug.
- Se localizó Flutter en `C:/Users/Personal/flutter/flutter/bin`. Su metadato local informa Flutter 3.47.1; ejecutar directamente `dart.exe --version` confirmó Dart **3.13.1**, inferior al mínimo declarado **3.13.2**. Debe resolverse esa compatibilidad antes de `pub get`; no se rebajó el requisito ni se actualizó el SDK.

La copia de trabajo tiene **55 archivos rastreados eliminados y 5 generados modificados**, ya presentes al iniciar la revisión. Entre los ausentes están:

- `lib/main.dart` y `README.md`.
- `lib/core/config/api_config.dart`, `lib/core/storage/auth_storage.dart`, `lib/core/theme/app_colors.dart`.
- Implementaciones Dart de asistencia inteligente y vestidor virtual.
- La carpeta `test`, con sus pruebas que sí aparecen en HEAD.

Hay 59 archivos Dart actuales. La comprobación de imports locales detectó seis destinos distintos ausentes, entre ellos configuración, almacenamiento y tema. El punto de entrada habitual no existe. **El móvil no es ejecutable tal como está**, independientemente del problema de versión del SDK. Los archivos en `.dart_tool` y `build` son artefactos anteriores, no evidencia de que el árbol actual sea reproducible.

## Pantallas y funcionalidades encontradas

Esto describe código presente, no una demostración funcional:

| Área | Evidencia local | Limitación |
| --- | --- | --- |
| Acceso de clientes y registro | `lib/features/autenticacion_seguridad/pages/`, modelos y `services/auth_service.dart`. | Depende de configuración/almacenamiento eliminados; no es acceso administrativo del MVP. |
| Inicio y navegación | `inicio/pages/main_navigation_page.dart`: Inicio, Catálogo, Vestidor, Carrito y Perfil; accesos a reservas e historial. | Importa vestidor/asistencia ausentes. El `main.dart` que restauraba la sesión solo puede verse en HEAD. |
| Catálogo y detalle | `catalogo/pages/catalogo_page.dart`, `producto_detalle_page.dart`, filtros y disponibilidad por sucursal. | El detalle también invoca carrito y vestidor; no se adapta cambiando solamente la URL. |
| Carritos y reservas | `carrito/` y `reservas/`: listado, detalle, cantidades, creación/cancelación. | Endpoints y modelos fuera del alcance actual del MVP. |
| Compra, pago e historial | `ventas/pages/`: checkout digital, Stripe, historial, detalle de compra y comprobante PDF/impresión. | No hay backend equivalente en el MVP; no se probaron pagos ni servicios externos. |
| Vestidor/asistencia | Imports, configuración nativa Android, dependencias y archivos en el historial. | Sus implementaciones Dart y pruebas están eliminadas de la copia actual. No se consideran disponibles. |

## Backend y configuración de API

En el árbol actual falta la clase `ApiConfig`; por eso no existe una URL efectiva que pueda comprobarse ejecutando esta copia. Se inspeccionó **HEAD, solo como evidencia histórica**:

- `lib/core/config/api_config.dart:17`: `String.fromEnvironment('API_BASE_URL')`, sin valor predeterminado. El destino debía pasarse con `--dart-define` al compilar/ejecutar.
- La documentación histórica daba ejemplos locales en el puerto 8000, con base de origen sin `/api`. No se comprobó qué URL se usó para generar los artefactos existentes ni se contactó ese destino.
- `AuthStorage` histórico utilizaba `FlutterSecureStorage` y la clave local `vanter_access_token`. El archivo está eliminado actualmente.
- `AuthService` actual solo admite `contexto == 'cliente'`. Su logout elimina el token local y no llama al servidor.

Los paths históricos y comentarios de los servicios coinciden con el contrato de clientes/comercio del backend Fashionstore, no con los endpoints nuevos de VestiNova MVP.

## Comparación con el contrato nuevo

Referencia vigente: [CONTRATO_CATALOGO.md](CONTRATO_CATALOGO.md) y `backend/app/{auth,products,schemas,security}.py` del MVP.

| Tema | Móvil heredado | VestiNova MVP | Adaptación o decisión necesaria |
| --- | --- | --- | --- |
| Login | `POST /auth/clientes/login`; espera `access_token`, `usuario`, `contexto: cliente`, `cliente_id`, nombre/apellido. | `POST /api/auth/login`; devuelve `administrador`, rol ADMINISTRADOR y expiración. No hay clientes. | Son actores distintos. No cambiar el móvil cliente para utilizar credenciales de administrador como sustituto. Definir primero el alcance móvil. |
| Registro | `POST /auth/clientes/registro`, con CI, sexo, teléfono y fecha de nacimiento. | No existe registro público ni API de clientes. | No está cubierto por el MVP. No agregarlo por inferencia de lo que trae el código heredado. |
| Restauración/logout | `/auth/me` y exigencia de contexto cliente; logout solo local. | `/api/auth/me`; `/api/auth/logout` revoca la sesión persistida. | Cambiar paths y contrato de identidad si se autorizara móvil administrativo; preservar revocación. El catálogo público del MVP no necesita sesión. |
| Listado | `GET /productos`; exige que la raíz JSON sea una lista. | `GET /api/catalogo/productos`; objeto `{items,total,limit,offset}`. | Cambiar ruta, decodificación y paginación. Con solo otra base URL el parser actual falla. |
| Búsqueda/filtros | `buscar`, categoría, talla, color, temporada, colección, sucursal y stock. | `q`, `limit`, `offset`; catálogo solo activo. | Implementar los parámetros del contrato nuevo y retirar filtros sin soporte; no inventar categorías/stock. |
| Detalle e imágenes | `GET /productos/{id}`; `imagen_principal_url`, `recursos`, `variantes`, inventarios. | `GET /api/catalogo/productos/{slug}`; `imagen_url` opcional, sin variantes ni stock. | Adoptar slug y mapa de campos; desacoplar disponibilidad, carrito y vestidor. |
| Producto/precio | `estado`, categoría e imagen principal; convierte `precio` a `double`. | `activo`, `slug`, `imagen_url`, `moneda: BOB`, fechas; `precio` cadena decimal exacta. | El parser tolera precio como cadena, pero convierte a flotante. Adoptar el DTO nuevo; no interpretar valores cero/vacíos de fallback como equivalencia de contratos. |
| Comercio adicional | `/carritos`, `/reservas`, `/ventas/digital`, `/pagos/stripe/*`, historial/comprobante, asistencia y vestidor. | No existen esas APIs en este MVP. | Quedan fuera de integración hasta que haya requisitos confirmados; no habilitarlas ni declarar entrega completa. |

Evidencias principales: `auth_service.dart:25–29, 93–107, 280–300`; `auth_models.dart:85–135`; `catalogo_service.dart:28–35, 50–100`; `producto_model.dart:31–45, 235–255`; `producto_detalle_page.dart:5, 54–66, 228–289`.

## Red local y comandos

Los siguientes son comandos de referencia Flutter, **no un procedimiento actualmente verificado para ejecutar esta copia**. Requiere primero decidir procedencia/reutilización, resolver los archivos ausentes y disponer de un SDK compatible. No se deben restaurar archivos ni cambiar APIs sin esa decisión.

```powershell
Set-Location 'C:\Users\Personal\Downloads\VestiNova\fashionstore-mobile\fashionstore-mobile'
flutter --version
dart --version
flutter doctor -v
flutter pub get
flutter analyze
flutter test
flutter devices
```

Cuando exista un móvil aprobado y adaptado al contrato, deberá configurarse una base distinta según el dispositivo:

| Entorno | Dirección de la API nueva | Condición |
| --- | --- | --- |
| Navegador en la computadora | `http://127.0.0.1:8001/api` | Angular ya utiliza proxy `/api`; Flutter web necesitaría su URL y origen CORS permitidos. |
| Emulador Android oficial | `http://10.0.2.2:8001/api` | `10.0.2.2` apunta a la computadora anfitriona. |
| Android físico por USB | `http://127.0.0.1:8001/api` | Ejecutar `adb reverse tcp:8001 tcp:8001` en la computadora, con el dispositivo autorizado. |
| Teléfono por Wi-Fi | `http://IP_LAN_DE_LA_PC:8001/api` | Misma red; API escuchando en `0.0.0.0`, puerto accesible y HTTP de desarrollo permitido. La conexión PostgreSQL sigue siendo local en el servidor. |

`localhost` en un teléfono sin redirección apunta al propio teléfono. `--dart-define=API_BASE_URL=...` es el mecanismo del código histórico, no una integración implementada: su constructor de rutas también tendría que cambiar. El directorio `mobile` futuro deberá fijar si la base incluye `/api` y mantener esa convención en todos sus servicios.

Android actual permite HTTP e INTERNET en `src/debug`; esa excepción cleartext es global dentro del build debug, no una lista limitada a hosts. El manifest principal carece de INTERNET, por lo que no acredita acceso de red en release, y release aún firma con debug. En iOS no se encontraron excepciones ATS para HTTP local ni claves de descripción de uso de cámara. Antes de pruebas físicas o publicación deben revisarse explícitamente esas configuraciones. Windows no permite compilar iOS; se requiere el entorno Apple correspondiente.

## Segundo parcial y decisión pendiente

No se encontró en la carpeta móvil una especificación o rúbrica vigente del segundo parcial. Los números CU09/CU19/CU22/CU26 que aparecen en comentarios y commits son referencias heredadas, no requisitos confirmados de VestiNova. El informe principal debe contrastar cualquier documento académico que el usuario proporcione; no se certifica la entrega móvil.

Decisión previa a incorporar: reutilizar código heredado con autorización, atribución, alcance y adaptación definidos, o crear una implementación móvil propia reducida. La publicación del backend/frontend nuevos puede prepararse de forma independiente. Esta auditoría no tomó esa decisión ni alteró historial alguno.
