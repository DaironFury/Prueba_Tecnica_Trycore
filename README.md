# EVM Dashboard

Dashboard para gestión de proyectos con cálculo de indicadores de **Valor Ganado (EVM)** en tiempo real.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy (async) · PostgreSQL 16 |
| Frontend | React 18 · TypeScript 5 · Vite · React Router v6 · Recharts |
| Infra | Docker · Docker Compose · Nginx |

## Prerrequisitos

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.20 (incluido en Docker Desktop)
- [Node.js](https://nodejs.org/) ≥ 20 y npm ≥ 10 — **solo para el paso de preparación inicial**; no se necesitan en la máquina una vez que el stack corre en Docker.

## Preparación inicial (primera vez)

Antes del primer `docker compose up`, es necesario generar el `package-lock.json` del frontend. El Dockerfile usa `npm ci`, que falla si ese archivo no existe.

```bash
# Desde la raíz del repositorio
cd frontend
npm install --package-lock-only   # genera package-lock.json sin instalar nada localmente
cd ..
```

> **¿Por qué?** `npm ci` requiere un `package-lock.json` con `lockfileVersion >= 1` para garantizar instalaciones reproducibles dentro del contenedor. Sin él, el build de Docker falla con `EUSAGE`.

## Levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd Prueba_Tecnica_Trycore

# 2. Generar el lockfile del frontend (solo la primera vez)
cd frontend && npm install --package-lock-only && cd ..

# 3. Crear el archivo de variables de entorno
cp .env.example .env
# Edita .env si quieres cambiar contraseñas o puertos

# 4. Construir e iniciar los tres servicios
docker compose up --build
```

Una vez que los contenedores estén en pie:

| Servicio | URL |
|---|---|
| Aplicación web | http://localhost:3000 |
| API REST (Swagger UI) | http://localhost:8000/api/docs |
| Base de datos | `localhost:5432` |

## Estructura de carpetas

```
.
├── backend/                   # API FastAPI
│   ├── app/
│   │   ├── api/v1/            # Routers y schemas Pydantic
│   │   ├── domain/            # Lógica EVM pura (sin dependencias)
│   │   ├── persistence/       # ORM SQLAlchemy y repositorios
│   │   └── services/          # Casos de uso (orquestación)
│   └── tests/
│       ├── unit/              # Tests del calculador EVM puro
│       └── integration/       # Tests HTTP end-to-end
├── frontend/                  # SPA React + Vite
│   └── src/
│       ├── api/               # Clientes HTTP (Axios)
│       ├── components/        # Componentes reutilizables
│       ├── pages/             # Vistas (ProjectListPage, ProjectDetailPage)
│       ├── types/             # Tipos TypeScript
│       └── utils/             # Formateo de moneda y porcentajes
├── db/init/                   # Script SQL de inicialización
└── docker-compose.yml
```

## Ejecutar los tests

Los tests requieren que la base de datos esté corriendo:

```bash
# Solo la BD (si ya tienes el entorno Python instalado localmente)
docker compose up -d database

# Ejecutar tests con cobertura (desde la carpeta backend/)
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

Desde dentro del contenedor de la API:

```bash
docker compose exec api pytest --cov=app --cov-report=term-missing
```

La cobertura mínima configurada es **80 %** en las capas de negocio.

## Indicadores EVM calculados

| Indicador | Fórmula |
|---|---|
| PV | % planificado × BAC |
| EV | % real × BAC |
| CV | EV − AC |
| SV | EV − PV |
| CPI | EV / AC |
| SPI | EV / PV |
| EAC | BAC / CPI |
| VAC | BAC − EAC |

Los indicadores del proyecto se obtienen **sumando valores absolutos** de todas las actividades; nunca promediando índices individuales.

## Endpoints principales

```
GET    /api/v1/projects                          # Listar proyectos
POST   /api/v1/projects                          # Crear proyecto
GET    /api/v1/projects/{id}                     # Detalle + EVM
PUT    /api/v1/projects/{id}                     # Actualizar proyecto
DELETE /api/v1/projects/{id}                     # Eliminar proyecto
GET    /api/v1/projects/{id}/indicators          # Solo EVM consolidado
POST   /api/v1/projects/{id}/activities          # Crear actividad
PUT    /api/v1/projects/{id}/activities/{aid}    # Actualizar actividad
DELETE /api/v1/projects/{id}/activities/{aid}    # Eliminar actividad
GET    /health                                   # Liveness (sin BD)
GET    /health/ready                             # Readiness (con BD)
```

## Solución de problemas comunes

### `npm ci` falla con `EUSAGE` al construir el frontend

**Causa:** no existe `package-lock.json` en `frontend/`.

```bash
cd frontend
npm install --package-lock-only
cd ..
docker compose up --build
```

### Error de TypeScript en `vite.config.ts`: `Cannot find name 'process'` / `__dirname`

**Causa:** falta `@types/node` o no está declarado en `tsconfig.node.json`.

Verificar que `frontend/package.json` incluya `"@types/node"` en `devDependencies` y que `frontend/tsconfig.node.json` tenga `"types": ["node"]` dentro de `compilerOptions`. Ambos ya están configurados en este repositorio; si se eliminan por error, restáuralos.

### Error de TypeScript: `Cannot find module '*.module.css'`

**Causa:** falta el archivo `frontend/src/vite-env.d.ts`.

Crear el archivo con el siguiente contenido:

```ts
/// <reference types="vite/client" />
```

Este archivo habilita las declaraciones de tipo que Vite provee para imports de CSS Modules, imágenes y otras variables de entorno `import.meta.env`.
