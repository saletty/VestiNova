# Contrato compartido de productos — VestiNova MVP

Acuerdo inicial de integración, 25 de octubre de 2026. Este documento propone el contrato para que ambos integrantes trabajen sobre una API común; no implica una aceptación externa del compañero.

## Responsabilidades

- Integrante 1: autenticación de administrador, API y formularios administrativos para registrar, editar y listar productos; migraciones y persistencia.
- Integrante 2, rama `miguel`: pantallas públicas de catálogo y detalle, consumiendo los endpoints siguientes. El primer incremento de CU09 implementa `/catalogo` y `/catalogo/{slug}`, con búsqueda por nombre, paginación y estados de carga, vacío, error y producto no disponible.
- Ambas partes: conservar nombres, tipos y semántica del contrato. Proponer cambios aquí y actualizar las pruebas antes de modificar respuestas.

## Endpoints públicos

Base relativa desde Angular: `/api`. El proxy local apunta a `http://127.0.0.1:8001`.

| Método y ruta | Resultado |
| --- | --- |
| `GET /api/catalogo/productos` | Lista paginada exclusivamente de productos activos. |
| `GET /api/catalogo/productos/{slug}` | Detalle activo; `404` si no existe o está inactivo. |

Listado: parámetros `q` opcional (búsqueda), `limit` (20 por defecto, máximo 100) y `offset` (0 por defecto). Respuesta:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

Cada elemento y el detalle comparten esta forma ilustrativa; los ejemplos no se insertan en la base:

```json
{
  "id": 1,
  "slug": "camisa-lino",
  "nombre": "Camisa de lino",
  "descripcion": "Descripción escrita por el administrador.",
  "precio": "180.00",
  "moneda": "BOB",
  "imagen_url": null,
  "activo": true,
  "creado_en": "2026-10-25T12:00:00Z",
  "actualizado_en": "2026-10-25T12:00:00Z"
}
```

`precio` viaja como cadena decimal exacta con dos decimales; mostrarlo como bolivianos sin recalcularlo para guardarlo. `imagen_url` puede ser nulo: usar un estado visual sin imagen, sin inventar una fotografía de producto. Las fechas son ISO 8601 con zona horaria. El slug identifica la URL pública; el ID identifica las operaciones administrativas.

Los campos de esta versión se limitan a identidad, descripción, precio, imagen externa opcional y visibilidad. No hay stock, tallas, colores, compras, ventas, reservas, empresas o suscripciones.

Validaciones: nombre entre 3 y 120 caracteres; descripción de hasta 3000; slug entre 3 y 140, con letras ASCII minúsculas, números y guiones simples; precio mayor que cero y máximo `99999999.99`, con dos decimales como máximo; URL de imagen HTTP/HTTPS, sin credenciales y de hasta 2048 caracteres. `q` admite hasta 120 caracteres y busca por nombre, con orden de ID descendente. El servidor genera el slug al registrar si se omite; editar el nombre conserva el slug salvo cambio explícito. Un slug duplicado devuelve `409`; no se cambia de forma silenciosa.

## Endpoints administrativos

Requieren `Authorization: Bearer TOKEN`, sesión vigente y administrador activo, comprobados por el servidor.

| Método y ruta | Operación |
| --- | --- |
| `GET /api/admin/productos` | Lista; admite `q`, `activo`, `limit`, `offset`. |
| `GET /api/admin/productos/{id}` | Obtener los datos para editar. |
| `POST /api/admin/productos` | Crear; `201` y producto persistido. |
| `PATCH /api/admin/productos/{id}` | Actualizar solo campos enviados; devuelve producto persistido. |

Alta: `nombre`, `descripcion`, `precio`; opcionales `slug`, `imagen_url`, `activo`. Si no se envía slug, el servidor lo genera. Moneda fija `BOB`. El formulario administrativo recibe y muestra las validaciones del servidor. No existe borrado físico ni carga de archivos en este alcance.

## Autenticación y errores

- `POST /api/auth/login`: `{ "correo": "...", "password": "..." }` → `access_token`, `token_type: "bearer"`, `expires_at` y `administrador: {id,nombre,correo,rol:"ADMINISTRADOR",activo:true}`.
- `GET /api/auth/me`: identidad del administrador vigente. No devuelve contraseña ni hash.
- `POST /api/auth/logout`: revoca la sesión; respuesta `204`.
- `401`: sesión ausente, vencida, revocada o cuenta inactiva. `403`: actor o permiso insuficiente. `404`: recurso no disponible. `409`: slug ya utilizado. `422`: validación.
- Errores de dominio: `{ "detail": "Mensaje" }`; errores de entrada FastAPI: `detail` es una lista con `loc` y `msg`. No mostrar mensajes SQL ni trazas al usuario.

El catálogo no necesita token. No debe consumir `/api/admin/*` ni guardar credenciales del administrador. Desactivar un producto lo retira de las consultas públicas.

## Pantallas del primer incremento de CU09

El frontend utiliza exclusivamente los dos GET públicos anteriores. Conserva `precio` como cadena decimal y presenta el importe en bolivianos; utiliza la imagen recibida o una alternativa sin fotografía si falta o no se puede cargar. El estado `activo` representa publicación, no existencias.

Este incremento no incorpora filtros adicionales, variantes, empresas, promociones, disponibilidad por sucursal, compras ni almacenamiento offline. No modifica el esquema de PostgreSQL, la autenticación, las pantallas administrativas ni los diagramas ICONIX. El caso académico completo sigue pendiente de las integraciones con CU05, CU06, CU08 y CU14.
