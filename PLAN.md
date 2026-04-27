# Plan de Implementación — EVM Dashboard

## Estado actual

Lo que ya existe y funciona:

- Dominio puro (`evm_calculator.py`) con todas las fórmulas EVM y sus tests unitarios
- Esqueleto completo de rutas, schemas Pydantic, ORM y modelos de dominio
- Frontend con todas las páginas, componentes, tipos y cliente HTTP cableados
- Esquema PostgreSQL (`db/init/01_schema.sql`) y Dockerfile del backend
- **Bloqueante:** todos los handlers de routers, servicios y repositorios lanzan `NotImplementedError`

---

## Principio de validación continua

> **Regla:** Ningún paso avanza al siguiente sin que la validación correspondiente sea exitosa. Si algo falla, se corrige antes de continuar.

---

## Gitflow

| Rama | Contenido | PR destino |
|---|---|---|
| `main` | Producción | — |
| `develop` | Integración | — |
| `feature/backend-api` | Repositorios, servicios, routers, tests de integración, README.md | develop |
| `feature/frontend-ui` | CRUD proyectos, tabla EVM completa, servicio frontend en docker-compose | develop |
| `feature/docs` | AI_PROCESS.md | develop |
| `release/1.0.0` | Merge final develop → main | main |

La BD **no tiene feature propio**: `db/init/01_schema.sql` ya está escrito y no requiere cambios.

---

## Flujo de datos

```
Frontend (React)
    └── src/api/         →  HTTP /api/v1
                                └── FastAPI Router
                                        └── Service
                                                ├── Repository → AsyncSession → PostgreSQL
                                                └── EVMCalculator (dominio puro)
```

---

## Paso 1 — Gitflow: crear ramas

```bash
git checkout develop
git checkout -b feature/backend-api
# (al terminar backend)
git checkout develop
git checkout -b feature/frontend-ui
git checkout develop
git checkout -b feature/docs
```

---

## Paso 2 — Backend: Repositorios

**Rama:** `feature/backend-api`

### `backend/app/persistence/repositories/project_repository.py`

- `get_all()` → lista de `ProjectORM`
- `get_by_id(project_id)` → `ProjectORM | None`
- `create(data: ProjectCreate)` → `ProjectORM`
- `update(project_id, data: ProjectUpdate)` → `ProjectORM | None`
- `delete(project_id)` → `bool`

### `backend/app/persistence/repositories/activity_repository.py`

- `create(project_id, data: ActivityCreate)` → `ActivityORM`
- `update(activity_id, data: ActivityUpdate)` → `ActivityORM | None`
- `delete(activity_id)` → `bool`

### Validación

- [ ] `docker compose up -d database` — BD levanta sin errores
- [ ] `pytest tests/unit/` — todos los tests del calculador en verde
- [ ] Smoke test manual: ejercitar cada método del repositorio contra la BD real

---

## Paso 3 — Backend: Servicios

**Rama:** `feature/backend-api`

### `backend/app/services/project_service.py`

Orquesta repositorios + dominio EVM:

- `list_projects()` → lista de proyectos
- `get_project_detail(project_id)` → proyecto + actividades + `EVMIndicators` calculados
- `create_project(data)` → proyecto creado
- `update_project(project_id, data)` → proyecto actualizado
- `delete_project(project_id)` → confirmación
- `get_project_indicators(project_id)` → solo `EVMIndicators` consolidados

Flujo de cálculo: `ActivityORM` → `ActivityInput` → `evm_calculator` por actividad → `calculate_project_indicators` para consolidar.

### `backend/app/services/activity_service.py`

- `create_activity(project_id, data)` → actividad creada
- `update_activity(project_id, activity_id, data)` → actividad actualizada
- `delete_activity(project_id, activity_id)` → confirmación

### Validación

- [ ] `pytest tests/unit/` — sigue en verde
- [ ] `ruff check backend/` — sin errores de linting

---

## Paso 4 — Backend: Handlers de routers

**Rama:** `feature/backend-api`

Implementar los 9 endpoints en `projects.py` y `activities.py`:

- Inyectar servicio vía `Depends`
- Devolver `DataResponse` o `MessageResponse`
- Lanzar `HTTPException(404)` si el recurso no existe

### Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/api/v1/projects` | 200 lista |
| POST | `/api/v1/projects` | 201 objeto |
| GET | `/api/v1/projects/{id}` | 200 detalle + EVM |
| PUT | `/api/v1/projects/{id}` | 200 actualizado |
| DELETE | `/api/v1/projects/{id}` | 204 |
| GET | `/api/v1/projects/{id}/indicators` | 200 EVM consolidado |
| POST | `/api/v1/projects/{id}/activities` | 201 actividad |
| PUT | `/api/v1/projects/{id}/activities/{aid}` | 200 actividad |
| DELETE | `/api/v1/projects/{id}/activities/{aid}` | 204 |

### Validación

- [ ] `docker compose up -d database api`
- [ ] Probar **todos** los endpoints desde Swagger UI → `http://localhost:8000/api/docs`
- [ ] `POST /api/v1/projects` → 201 con id
- [ ] `GET /api/v1/projects/{id}` → 200 con EVM calculado
- [ ] `GET /api/v1/projects/{id}` tras delete → 404
- [ ] Verificar manualmente que los indicadores EVM son correctos para un caso simple

---

## Paso 5 — Backend: Tests de integración

**Rama:** `feature/backend-api`

### `backend/tests/conftest.py` — añadir fixtures

- Fixture `app` con BD de test
- Fixture `async_client` con `httpx.AsyncClient` + `ASGITransport`

### `backend/tests/integration/test_projects.py`

Al menos un test por endpoint: 201 create, 200 list, 200 detail con EVM, 200 update, 204 delete, 404 not found.

### `backend/tests/integration/test_activities.py`

Al menos un test por endpoint de actividades.

### Validación

- [ ] `pytest --cov=app --cov-report=term-missing` → cobertura ≥ 80% en capa de negocio
- [ ] `pytest -v` → todos los tests en verde
- [ ] Servicios y repositorios aparecen con cobertura real en el reporte (no excluidos)

---

## Paso 6 — Frontend: CRUD de proyectos

**Rama:** `feature/frontend-ui`

### `frontend/src/pages/ProjectListPage.tsx`

- Botón "Nuevo proyecto" → modal con formulario (nombre, descripción, fecha de corte)
- Botón editar en cada tarjeta de proyecto → modal con datos pre-cargados
- Botón eliminar con confirmación
- Usar `createProject`, `updateProject`, `deleteProject` de `projects.api.ts` (ya implementados)

### Validación

- [ ] Con backend corriendo, abrir `http://localhost:5173`
- [ ] Crear proyecto → aparece en lista
- [ ] Editar nombre → verificar cambio
- [ ] Eliminar → desaparece de lista
- [ ] Verificar que los errores del servidor se muestran al usuario

---

## Paso 7 — Frontend: Tabla de actividades completa

**Rama:** `feature/frontend-ui`

### `frontend/src/components/activities/ActivityTable.tsx`

Añadir columnas: PV, EV, CV, SV, EAC, VAC (los datos ya llegan desde el backend).

### Validación

- [ ] Crear un proyecto, añadir 3 actividades con valores distintos
- [ ] Verificar que los indicadores en la tabla coinciden con el `EVMSummaryCard`
- [ ] Verificar cálculo manual contra las fórmulas:
  - PV = % planificado × BAC
  - EV = % real × BAC
  - CV = EV − AC
  - SV = EV − PV
  - CPI = EV / AC
  - SPI = EV / PV
  - EAC = BAC / CPI
  - VAC = BAC − EAC
- [ ] El `EVMBarChart` sigue mostrando correctamente PV/EV/AC

---

## Paso 8 — Docker Compose: servicio frontend

**Rama:** `feature/frontend-ui`

Añadir a `docker-compose.yml`:

```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:80"
  depends_on:
    - api
```

### Validación

- [ ] `docker compose down -v && docker compose up --build`
- [ ] Los **tres servicios** levantan: `database` (5432), `api` (8000), `frontend` (3000)
- [ ] Flujo completo desde `http://localhost:3000` (Nginx, sin Vite)
- [ ] El proxy de Nginx redirige `/api/` correctamente al servicio `api`

---

## Paso 9 — README.md

**Rama:** `feature/backend-api`

Actualizar `README.md` con:

- Descripción del proyecto y stack tecnológico
- Prerrequisitos: Docker + Docker Compose
- Instrucciones: `docker compose up --build`
- URLs: app en `http://localhost:3000`, Swagger en `http://localhost:8000/api/docs`
- Cómo correr los tests: `pytest --cov=app`
- Estructura de carpetas

---

## Paso 10 — AI_PROCESS.md

**Rama:** `feature/docs`

Crear `AI_PROCESS.md` con las secciones requeridas por la prueba:

- Herramientas de IA utilizadas y por qué
- Todos los prompts enviados (textuales, en orden cronológico)
- Cómo aprendiste EVM
- Cómo validaste las fórmulas
- Dos decisiones donde no seguiste a la IA
- Cómo verificaste los cálculos
- Una decisión de arquitectura independiente
- Reflexión final

---

## Orden de ejecución

1. Crear `feature/backend-api` → Pasos 2, 3, 4, 5, 9 → PR → develop
2. Crear `feature/frontend-ui` → Pasos 6, 7, 8 → PR → develop
3. Crear `feature/docs` → Paso 10 → PR → develop
4. Crear `release/1.0.0` desde develop → PR → main (entrega final)
