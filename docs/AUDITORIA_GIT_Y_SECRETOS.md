# Resumen de auditoría para publicación

25 de octubre de 2026. Este resumen puede acompañar al código nuevo. El informe local con los detalles de posibles secretos históricos se conserva en `docs/_local/AUDITORIA_GIT_Y_SECRETOS.md`, ignorado por Git, para no difundir localizaciones precisas de credenciales ajenas al MVP. Ningún informe muestra valores de credenciales.

## Repositorios

No se encontró Git en la carpeta superior `C:\Users\Personal\Downloads\VestiNova` ni en sus antecesores. Hay cuatro repositorios independientes:

| Carpeta | Rama revisada | Commits desde HEAD / todas las referencias | Remoto |
| --- | --- | --- | --- |
| `vestinova-mvp` | `master` inicial | 0 / 0 | Sin remoto. |
| `fashionstore-api/fashionstore-api` | `main` | 26 / 27 | GitHub del proyecto heredado. |
| `fashionstore-web/fashionstore-web` | `main` | 31 / 31 | GitHub del proyecto heredado. |
| `fashionstore-mobile/fashionstore-mobile` | `main` | 16 / 21 | GitHub del proyecto heredado. |

No se borraron ni trasladaron carpetas `.git`, no se reescribió historial y no se ejecutaron staging, commits o push. No se encontraron gitlinks/submódulos en los índices inspeccionados. Los tres repositorios heredados permanecen fuera de la raíz propuesta para publicar. La procedencia del móvil se documenta en [REVISION_MOVIL.md](REVISION_MOVIL.md).

## Resultado del MVP

El MVP no tiene archivos rastreados ni historial previo. Se revisaron 75 archivos de texto del árbol de trabajo en el escaneo inicial; las coincidencias fueron fixtures de pruebas y una conexión local de ejemplo, sin credenciales operativas identificadas. `backend/.env` se comprobó como ignorado sin abrir su contenido. El ejemplo público utiliza marcadores explícitos y el `.env` privado no se modificó.

Se amplió y comprobó el `.gitignore` para excluir `.env` y copias habituales, entornos virtuales, dependencias, compilados y firmas móviles; se mantienen fuentes, migraciones, ejemplos sin secretos y archivos de dependencias/bloqueo. Se verificó también que no se depende de exclusiones globales de la computadora. Las instrucciones de publicación revisan el índice antes del commit y rechazan gitlinks o rutas sensibles inesperadas.

## Historial heredado excluido

La revisión encontró posibles secretos en una fuente heredada y una copia local de configuración que no está ignorada en su propio repositorio. Sus valores no se imprimieron, no se verificó su vigencia y no se contactaron servicios remotos. El detalle permanece únicamente en el informe local excluido. Si las credenciales fueron reales, debe acordarse su revocación/rotación con su propietario antes de cualquier reutilización. No se importará ese historial al repositorio nuevo.

## Alcance y límites

Se revisaron nombres de archivos y blobs alcanzables desde referencias y reflogs: 296 del backend heredado, 705 de la web y 354 del móvil. Los patrones cubrieron claves privadas, tokens conocidos, JWT literales, conexiones con contraseña y asignaciones sensibles habituales. Se distinguieron datos sintéticos de pruebas. No se analizaron como texto binarios o archivos mayores de 2 MB ni objetos huérfanos fuera de referencias/reflogs.

La detección por patrones tiene límites y no acredita ausencia absoluta de secretos ni la autoría de un archivo. Los archivos añadidos después requieren revisión antes de publicarse. El informe no certifica que la app móvil funcione o cumpla los requisitos académicos.
