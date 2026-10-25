# Preparación del repositorio público VestiNova

Revisión del 25 de octubre de 2026. Este procedimiento está escrito para que el usuario lo ejecute; **no se ejecutaron commits, creación de remoto, push ni invitaciones** durante la preparación.

## Qué se puede incluir

| Componente | Estado y decisión |
| --- | --- |
| `backend/` | Código nuevo, migraciones, scripts, pruebas, dependencias y ejemplo sin secretos; preparado para el primer commit. El `.env` privado y PostgreSQL permanecen locales. |
| `frontend/` | Angular nuevo, configuración, fuentes, pruebas y `package-lock.json`; preparado. `node_modules`, caché y compilados quedan ignorados. |
| `docs/` | Contrato del catálogo, ejecución, avances y auditorías; preparado. No representa una rúbrica académica. |
| `mobile/` | Solo README de reserva, sin app ejecutable. El Flutter heredado sigue fuera y requiere una decisión de procedencia y alcance antes de incorporarse. |

El repositorio Git local existente es `C:\Users\Personal\Downloads\VestiNova\vestinova-mvp`. Su carpeta puede conservar ese nombre aunque GitHub se llame **VestiNova**. No es necesario mover backend/frontend, cambiar URLs internas ni recrear la base.

```text
VestiNova (nombre remoto; raíz local vestinova-mvp)
├── backend/
├── frontend/
├── mobile/
│   └── README.md       # reserva; no se incorpora la app heredada
├── docs/
├── .gitignore
├── .gitattributes
└── README.md
```

No ejecutar `git init` ni `git add` desde la carpeta superior `C:\Users\Personal\Downloads\VestiNova`: contiene otros tres repositorios heredados independientes. No se eliminaron sus `.git`; no se pierde ni se importa su historial. Los conteos y el alcance de la revisión están en [AUDITORIA_GIT_Y_SECRETOS.md](AUDITORIA_GIT_Y_SECRETOS.md).

## Estado real previo a publicar

- El usuario confirmó que ya creó el repositorio GitHub público `saletty/VestiNova` desde la web. No repetir su creación.
- El Git del MVP está en la rama inicial `master`, sin commits, sin archivos rastreados y sin remoto configurado. No es necesario reinicializarlo.
- GitHub CLI (`gh`) no se encontró en PATH durante la revisión.
- Propietario confirmado: `saletty`; repositorio: `saletty/VestiNova`; compañero: `jerezsuarezmiguelangel011-max`.
- Ramas acordadas: `main`, `pruebas`, `salet` y `miguel`. Todavía no se crearon: este Git no tiene un primer commit al que puedan apuntar. Los comandos siguientes las crean después de ese commit.
- Backend, frontend, datos y credenciales del MVP se conservan. La publicación de código no sube PostgreSQL ni exporta datos.

Si este estado cambia antes de ejecutar los comandos, revisar `git status`, rama y remotos antes de continuar. No sustituir ni sobrescribir un remoto o historial distinto.

## Si Git muestra «detected dubious ownership»

Se comprobó este caso en la terminal del usuario: el `.git` inicializado durante la preparación pertenece a `CodexSandboxOffline`, mientras PowerShell se ejecuta como `Personal`. Git bloquea el repositorio por esa diferencia. `git add` no llega a preparar archivos; el error posterior de `git diff --cached` en modo `--no-index` es consecuencia del mismo bloqueo.

En la terminal de **Personal**, registrar únicamente esta carpeta conocida como confiable:

```powershell
git config --global --add safe.directory 'C:/Users/Personal/Downloads/VestiNova/vestinova-mvp'
Set-Location 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp'
git status
```

Esta excepción se limita a la raíz del MVP; no autoriza todas las carpetas ni cambia permisos/propietarios de Windows. No hace falta borrar o reinicializar `.git`. Después de que `git status` funcione, repetir el bloque de preparación de archivos del paso 3 y continuar con el primer commit. Esta configuración la ejecuta el usuario localmente; no se modificó su configuración global desde el agente. [Referencia de safe.directory](https://git-scm.com/docs/git-config#Documentation/git-config.txt-safedirectory).

## Secretos y exclusiones

El `.gitignore` contempla `.env` y copias habituales, claves privadas, firmas Android/iOS, entornos virtuales, dependencias, cachés y compilados Python/Angular/Flutter. Conserva `.env.example`, migraciones, `requirements*.txt`, `package-lock.json`, `pubspec.lock` y fuentes. Los patrones se comprobaron con `git check-ignore` sin crear archivos sensibles de prueba.

El informe detallado sobre posibles secretos históricos queda en `docs/_local/`, ignorado por Git. Se publica únicamente el resumen saneado de auditoría.

La revisión del MVP no identificó secretos reales en los archivos previstos para incluirse; las coincidencias de código fueron fixtures de pruebas y ejemplos. Su historial está vacío. El informe explica los límites de la detección por patrones; no constituye garantía sobre archivos que se añadan después.

Se encontraron **posibles secretos en el historial del backend heredado**, que no se incorpora. No se mostraron sus valores ni se probó su vigencia. Ese hallazgo no se resuelve copiando o publicando el historial antiguo; si fueran credenciales reales, debe revisarse su revocación/rotación en su origen. La auditoría no modificó cuentas externas.

## 1. Instalar GitHub CLI e iniciar sesión

Git ya está instalado. Como no se encontró `gh`, instalarlo si continúa ausente:

```powershell
winget install --id GitHub.cli --exact --source winget
```

Cerrar y abrir una terminal PowerShell para actualizar PATH. Si WinGet no está disponible, usar el instalador Windows de [GitHub CLI](https://cli.github.com/).

```powershell
gh --version
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh api user --jq .login
```

Confirmar que el usuario mostrado es el propietario deseado. La autenticación ocurre en GitHub; no pegar tokens, contraseñas ni el `.env` en el chat ni en los comandos del repositorio. [Autenticación de GitHub CLI](https://cli.github.com/manual/gh_auth_login).

## 2. Revisar la raíz y preparar los datos del remoto existente

Estos comandos están destinados a un repositorio de una cuenta personal. Si el propietario será una organización, confirmar antes permisos y política de colaboradores de esa organización.

```powershell
$VestiNovaRoot = 'C:\Users\Personal\Downloads\VestiNova\vestinova-mvp'
Set-Location -LiteralPath $VestiNovaRoot
git rev-parse --show-toplevel
git status --short
git branch --show-current
git remote -v

$GitHubOwner = 'saletty'
$AuthenticatedUser = gh api user --jq .login
if ($LASTEXITCODE -ne 0) { throw 'No se pudo comprobar la sesión de GitHub.' }
$AuthenticatedUser = $AuthenticatedUser.Trim()
if ($AuthenticatedUser -ne $GitHubOwner) { throw 'La sesión de GitHub no coincide con el propietario elegido.' }
$VestiNovaRepo = "$GitHubOwner/VestiNova"
$VestiNovaRemote = "https://github.com/$VestiNovaRepo.git"

```

El repositorio ya se creó desde la web y debe permanecer vacío hasta subir el commit local; el README y `.gitignore` ya están en este proyecto. No volver a ejecutar la creación ni clonar otro proyecto en esta computadora. La consulta `git ls-remote` del paso 4 comprueba que no se hayan creado commits remotos por accidente.

Para el primer push no es obligatorio instalar `gh`: Git puede autenticar mediante su gestor de credenciales. Si se omiten los pasos de GitHub CLI, antes del paso 4 definir `$VestiNovaRemote = 'https://github.com/saletty/VestiNova.git'` y `$VestiNovaRepo = 'saletty/VestiNova'`. Los comandos `gh` para fijar la rama predeterminada, abrir el repositorio e invitar al compañero pueden hacerse posteriormente o desde la interfaz web de GitHub.

## 3. Preparar y revisar el primer commit

Ejecutar desde la misma terminal y raíz. Se incluyen juntos todos los archivos necesarios del MVP actual; no omitir módulos referenciados por rutas/imports para dividirlo artificialmente.

```powershell
git check-ignore backend/.env backend/.venv/pyvenv.cfg frontend/node_modules/.package-lock.json
git status --short --ignored

git add -- .gitattributes .gitignore README.md backend frontend mobile docs
if ($LASTEXITCODE -ne 0) { throw 'No se prepararon los archivos; revisa la salida de Git.' }
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
if ($LASTEXITCODE -ne 0) { throw 'Revisa los errores de formato antes del commit.' }

$NestedGitLinks = @(git ls-files --stage | Select-String '^160000 ')
if ($NestedGitLinks.Count -gt 0) { throw 'Hay un gitlink/repositorio anidado; detenerse y revisar su origen.' }

$SensitivePaths = @(git ls-files | Where-Object {
    ((($_ -match '(^|/)\.env') -or ($_ -match '\.env($|[._~ -])')) -and ($_ -notmatch '(^|/)\.env\.example$')) -or
    ($_ -match '(^|/)(node_modules|\.venv|\.dart_tool|build|dist|\.runtime)/') -or
    ($_ -match '^docs/_local/') -or
    ($_ -match '(?i)\.(jks|keystore|p12|pfx|p8|pem|key|mobileprovision|provisionprofile)$') -or
    ($_ -match '(^|/)key\.properties$')
})
if ($SensitivePaths.Count -gt 0) {
    $SensitivePaths
    throw 'Hay rutas sensibles o generadas en el índice. Revisarlas antes de confirmar; no se mostraron contenidos.'
}
```

Revisar especialmente que `mobile` solo contiene su README y que los archivos nuevos propios no llevan credenciales incrustadas. `.gitignore` no protege archivos que ya estén rastreados; por eso se comprueba el índice. No continuar si hay hallazgos nuevos pendientes de aclarar.

Si falta identidad de autor para Git, establecerla solo en este repositorio. El correo del commit será visible en un repositorio público; puede utilizarse el correo noreply que GitHub muestre en la configuración de la cuenta.

```powershell
if (-not (git config --get user.name)) { git config user.name (Read-Host 'Nombre para tus commits') }
if (-not (git config --get user.email)) { git config user.email (Read-Host 'Correo de autor para Git, o tu noreply de GitHub') }

git commit -m 'feat(mvp): iniciar acceso administrativo y gestión de productos'
if ($LASTEXITCODE -ne 0) { throw 'El commit no se completó; no continuar al push.' }
git branch -m main
if ($LASTEXITCODE -ne 0) { throw 'No se cambió el nombre de rama; revisar las ramas existentes.' }
git branch pruebas main
if ($LASTEXITCODE -ne 0) { throw 'No se creó pruebas; revisar si ya existe.' }
git branch salet main
if ($LASTEXITCODE -ne 0) { throw 'No se creó salet; revisar si ya existe.' }
git branch miguel main
if ($LASTEXITCODE -ne 0) { throw 'No se creó miguel; revisar si ya existe.' }
git branch --list
git log -1 --oneline
```

El cambio `master` → `main` corresponde a esta rama inicial y no utiliza una variante de renombrado forzado. Las cuatro ramas apuntarán inicialmente al mismo commit, con todos los archivos necesarios para ejecutar el MVP. No se crea una copia de carpetas por rama. Los avances siguientes deben incluir código, migraciones, dependencias, pruebas y documentación necesarias para funcionar juntos.

## 4. Conectar el remoto y publicar las cuatro ramas

Se comprobó que no hay remoto en el MVP. Si apareciera uno antes de ejecutar esto, detenerse y revisarlo; no sustituirlo automáticamente.

```powershell
$ExistingRemotes = @(git remote)
if ($ExistingRemotes.Count -gt 0) { throw 'Ya existe un remoto; revisarlo antes de añadir origin.' }
git remote add origin $VestiNovaRemote
if ($LASTEXITCODE -ne 0) { throw 'No se agregó origin.' }
git remote -v

$RemoteRefs = @(git ls-remote origin)
if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar el remoto; comprueba autenticación y URL.' }
if ($RemoteRefs.Count -gt 0) { throw 'El remoto no está vacío; revisar sus commits antes de integrar.' }

git push -u origin main pruebas salet miguel
if ($LASTEXITCODE -ne 0) { throw 'El push no se completó; revisa el error sin sobrescribir historial.' }
gh repo edit $VestiNovaRepo --default-branch main
if ($LASTEXITCODE -ne 0) { throw 'Revisa la rama predeterminada en GitHub; las ramas ya pueden haberse publicado.' }
git ls-remote --heads origin
gh repo view $VestiNovaRepo --web
```

La consulta de ramas remotas debe mostrar `refs/heads/main`, `refs/heads/pruebas`, `refs/heads/salet` y `refs/heads/miguel`. `main` queda como predeterminada mediante el [comando de configuración del repositorio](https://cli.github.com/manual/gh_repo_edit). Si el remoto tiene contenido o rechaza el push, revisar e integrar el historial conscientemente; no borrarlo ni sobrescribirlo. El usuario realiza esta publicación manualmente. [Guía de GitHub para código local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## 5. Invitar al compañero

Invitar al usuario confirmado, en la misma sesión PowerShell:

```powershell
$GitHubCollaborator = 'jerezsuarezmiguelangel011-max'
gh api --method PUT "repos/$VestiNovaRepo/collaborators/$GitHubCollaborator" -H 'Accept: application/vnd.github+json' -H 'X-GitHub-Api-Version: 2026-03-10'
if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear la invitación; revisar permisos o usuario.' }
```

En un repositorio personal, la invitación añade acceso de colaborador; el compañero debe aceptarla. En una organización, el endpoint también permite especificar `permission=push` para acceso de escritura según sus políticas. No se concede administración como requisito de este trabajo. Alternativa gráfica: repositorio → Settings → Collaborators → Add people. [Referencia oficial del endpoint](https://docs.github.com/en/rest/collaborators/collaborators#add-a-repository-collaborator).

Después podrá clonar el único repositorio y configurar sus entornos locales con el README. La aplicación móvil no debe añadirse automáticamente al aceptar la invitación: su procedencia, estado, compatibilidad y requisitos siguen pendientes de decisión.

El uso de las cuatro ramas y los comandos de trabajo de cada integrante están en [RAMAS_Y_COLABORACION.md](RAMAS_Y_COLABORACION.md). Los PR propuestos van de `salet` o `miguel` hacia `pruebas`, y de `pruebas` hacia `main` después de validar.
