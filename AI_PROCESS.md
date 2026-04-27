# AI_PROCESS.md — Proceso de desarrollo con IA

## Herramientas de IA utilizadas y por qué

**Cursor IDE con Claude Sonnet 4.6 y Opus 4.7**
Elegí a Cursor como IDE debido a que ya habia tenido al oportunidad de manejarlo, utilice los modelos de Claude Sonnet y Opues porque considero que actualmente son los mejores modelos para trabajar los temas de programación.

Usé Cursor en modo **Agent** y **Plan**, lo que le permite leer archivos del proyecto, hacer búsquedas, escribir código, crear planes(paso a paso) y ejecutar comandos.

---

## Prompts enviados (cronológicos)

### Sesión principal

---

**Prompt 1:**
> Actúa como un arquitecto de software senior.
>
> Voy a darte el contexto de una prueba técnica. No quiero código todavía.
>
> Quiero que:
> 1. Expliques el problema en tus propias palabras
> 2. Identifiques objetivos funcionales y no funcionales
> 3. Identifiques riesgos técnicos
> 4. Identifiques qué debo aprender (especialmente EVM)
> 5. Propongas un plan de desarrollo por fases
> 6. Indiques en qué momento del flujo integrar Docker (no al final, sino estratégicamente)
>
> Contexto: @PruebaTecnica.txt

El asistente analizó el documento de la prueba técnica, identificó los objetivos funcionales (CRUD de proyectos y actividades, cálculo EVM, dashboard) y no funcionales (código limpio, tests, Gitflow, OpenAPI), identificó riesgos técnicos (implementar EVM correctamente, manejo de divisiones por cero, arquitectura desacoplada) y propuso un plan de desarrollo por fases con integración estratégica de Docker desde la fase 2.

---

**Prompt 2:**
> Explícame Earned Value Management (EVM) como si fuera un desarrollador que debe implementarlo.
>
> Necesito:
> 1. Explicación clara de cada indicador
> 2. Ejemplos numéricos paso a paso
> 3. Casos borde:
>    - AC = 0
>    - PV = 0
>    - sin actividades
> 4. Interpretación de CPI y SPI
> 5. Errores comunes de implementación
>
> No simplifiques demasiado, necesito precisión para implementar.

El asistente explicó las 8 fórmulas EVM con ejemplos numéricos concretos, describió el manejo de divisiones por cero retornando `None` en vez de `Infinity`, los umbrales de interpretación de CPI/SPI y los errores comunes como promediar índices individuales en vez de agregar valores absolutos.

---

**Prompt 3:**
> Voy a proponerte cálculos de EVM. Valida si son correctos.
>
> Datos:
> BAC = 1000
> % planificado = 50%
> % real = 40%
> AC = 600
>
> Calcula todos los indicadores.
>
> Luego:
> 1. Explica el estado del proyecto
> 2. Detecta errores
> 3. Valida que entiendo correctamente antes de codificar

El asistente validó los cálculos propuestos (PV=500, EV=400, CV=-200, SV=-100, CPI≈0.667, SPI=0.8, EAC=1500, VAC=-500), explicó el estado del proyecto (sobre presupuesto y atrasado) y confirmó la comprensión antes de pasar a codificar.

---

**Prompt 4:**
> Actúa como arquitecto de software.
>
> Diseña una solución fullstack incluyendo:
>
> 1. Backend (API REST)
> 2. Frontend (dashboard)
> 3. Base de datos
> 4. Flujo de datos
> 5. Servicio de cálculo EVM desacoplado
>
> Además:
> 6. Propón cómo dockerizar el sistema:
>    - Qué servicios van en contenedores
>    - Cómo se comunican
>    - Qué va en docker-compose
>    - Qué decisiones simplifican el despliegue
>
> Incluye:
> - Diagrama lógico en texto
> - Capas bien separadas
> - Justificación de decisiones
>
> Stack: [FastAPI + React]

El asistente diseñó la arquitectura completa con diagrama de capas, definió los tres contenedores (backend, frontend, database), explicó la comunicación por nombres de servicio en la red Docker y justificó las decisiones: cálculo EVM como función pura desacoplada, Nginx como proxy inverso, variables de entorno para la configuración.

---

**Prompt 5:**
> Diseña el modelo de base de datos.
>
> Incluye:
> 1. Tablas
> 2. Campos
> 3. Tipos de datos
> 4. Relaciones
> 5. Consideraciones para EVM
>
> Luego:
> - Script SQL PostgreSQL
>
> Además:
> - Qué considerar para que funcione correctamente en Docker (conexión, puertos, etc.)

El asistente diseñó el modelo relacional con las tablas `projects` y `activities`, tipos `UUID`, `NUMERIC(15,2)`, `TIMESTAMPTZ`, triggers de `updated_at`, índices y la decisión clave de no persistir los indicadores derivados (PV, EV, CPI...) sino solo los 5 campos de entrada. Incluyó el script SQL completo y consideraciones Docker para la conexión.

---

**Prompt 6:**
> Define una API REST completa.
>
> Incluye:
> - CRUD proyectos
> - CRUD actividades
> - Endpoint de indicadores EVM
>
> Para cada endpoint:
> - Request
> - Response
> - Errores
>
> Formato compatible con OpenAPI.
>
> Además:
> - Consideraciones para ejecutarse dentro de Docker

El asistente definió los 9 endpoints en formato OpenAPI, especificando los contratos de request/response con tipos Pydantic, los códigos de error por dominio (`PROJECT_NOT_FOUND`, `ACTIVITY_NOT_IN_PROJECT`) y el sobre de respuesta unificado `{ "data": ... }` / `{ "error": ... }`.

---

**Prompt 7:**
> Genera la estructura del backend en FastAPI
>
> Reglas:
> - Separación por capas
> - Sin lógica en controllers
> - Código limpio
>
> Incluye:
> 1. Estructura de carpetas
> 2. Configuración de conexión a BD (usando variables de entorno)
> 3. Preparación para Docker (no localhost, usar nombre del servicio)
>
> No generes toda la lógica aún.

El asistente generó la estructura completa del backend: carpetas por capas (`api`, `services`, `domain`, `persistence`), `config.py` con Pydantic Settings que lee `DATABASE_URL` del entorno, `database.py` con el engine asíncrono SQLAlchemy, stubs de routers, servicios y repositorios con `raise NotImplementedError`, y los archivos de soporte (`.env.example`, `.dockerignore`, `.gitignore`).

---

**Prompt 8:**
> Implementa el servicio de cálculo EVM.
>
> Requisitos:
> - Funciones puras
> - Manejo de división por cero
> - Casos borde
>
> Incluye:
> - Tests unitarios
> - Explicación de decisiones
>
> Asegúrate que sea desacoplado y testeable.

El asistente implementó `evm_calculator.py` con funciones puras sin dependencias externas, `_safe_divide` que retorna `None` en divisiones por cero, las funciones `interpret_cpi`/`interpret_spi` con `math.isclose` para precisión flotante, y `calculate_project_indicators` que agrega valores absolutos. Incluyó el módulo de constantes para eliminar números mágicos.

---

**Prompt 9:**
> Genera pruebas unitarias para EVM.
>
> Incluye:
> - Casos normales
> - Casos borde
> - Validación matemática
>
> Explica por qué cada test existe.

El asistente generó 49 tests unitarios organizados en 10 clases: casos canónicos resueltos a mano, escenarios de desempeño (bajo/en/sobre presupuesto), casos borde (AC=0, PV=0, todo en cero), validación límite a límite de CPI/SPI, pruebas de agregación de proyecto, pureza de la función e invariantes algebraicas (EAC × CPI = BAC, EAC + VAC = BAC, linealidad de escala). Cobertura del dominio al 100%.

---

**Prompt 10:**
> Diseña un dashboard que incluya:
>
> - Tabla de actividades
> - Indicadores EVM
> - Estado visual CPI/SPI
> - Gráfica PV vs EV vs AC
>
> Luego genera código en React.
>
> Además:
> - Cómo consumir API desde entorno dockerizado

El asistente diseñó y generó el frontend completo en React 18 + TypeScript + Vite: tipos que mapean los contratos del backend, cliente Axios con rutas relativas (`/api/v1/...`), hook `useProject`, páginas `ProjectListPage` y `ProjectDetailPage`, componentes `StatusBadge`, `EVMSummaryCard`, `ActivityTable`, `ActivityForm`, `EVMBarChart` y estilos CSS modules. La estrategia de proxy Vite en desarrollo / Nginx en producción elimina CORS y hardcoding de hosts.

---

**Prompt 11:**
> Genera un Dockerfile para el backend.
>
> Requisitos:
> - Imagen ligera
> - Variables de entorno
> - Puerto expuesto
> - Preparado para producción simple
>
> Explica cada línea del Dockerfile.

El asistente generó un Dockerfile multi-stage (`builder` + `runtime`) con imagen base `python:3.12.7-slim-bookworm`, virtualenv aislado en `/opt/venv`, usuario no-root `app:app`, `HEALTHCHECK` con `curl` y `CMD` en forma exec para recibir señales correctamente. Explicó cada línea con la justificación técnica y comparó el tamaño resultante (~180 MB vs ~480 MB single-stage).

---

**Prompt 12:**
> Genera un docker-compose.yml para:
>
> - Backend
> - PostgreSQL
>
> Incluye:
> - Variables de entorno
> - Volúmenes
> - Puertos
> - Dependencias entre servicios
>
> Explica:
> - Cómo se comunican los contenedores
> - Por qué usar nombres de servicio en vez de localhost

El asistente generó el `docker-compose.yml` con los servicios `database` (Postgres 16 Alpine) y `api`, red interna `evm-net`, volumen named `postgres_data`, healthcheck con `pg_isready` y `depends_on: condition: service_healthy`. Explicó el DNS interno de Docker y por qué `localhost` dentro de un contenedor apunta al propio contenedor, no al servicio de base de datos.

---

**Prompt 13:**
> Ayúdame a adaptar el backend para correr correctamente en Docker.
>
> Incluye:
> - Uso de DATABASE_URL
> - Manejo de variables de entorno
> - Evitar localhost
> - Configuración compatible con docker-compose
>
> Valida posibles errores comunes.

El asistente agregó el contexto `lifespan` en `main.py` con `SELECT 1` al arrancar (fail-fast si la DB es inalcanzable), el endpoint `/health/ready` que sondea la base de datos realmente, un validador en `config.py` que rechaza URLs sin el prefijo `postgresql+asyncpg://`, la función `_redact()` para logs sin passwords, y el script `db/init/01_schema.sql` para bootstrap automático. Incluyó una tabla de 18 errores comunes con su causa y solución.

---

**Prompt 14:**
> Modifica todas las descripciones y comentarios en idioma español

El asistente tradujo al español todos los docstrings, comentarios de módulo, docstrings de clase y función, resúmenes de endpoints OpenAPI (`summary=`), mensajes de log, mensajes de excepción de dominio, comentarios de infraestructura (Dockerfile, docker-compose, SQL, `.env.example`) y los nombres de variables de test. 22 archivos actualizados. Los 49 tests siguieron pasando sin regresiones.

---

**Prompt 15:**
> Quiero que crees la rama develop en el siguiente repositorio @PruebaTecnicaTrycore/Prueba_Tecnica_Trycore

El asistente verificó el repositorio local en `PruebaTecnicaTrycore/Prueba_Tecnica_Trycore`, comprobó que estaba en la rama `main` y que el remoto apuntaba a `https://github.com/DaironFury/Prueba_Tecnica_Trycore.git`. Creó la rama `develop` a partir de `main` con `git checkout -b develop` y la publicó en el repositorio remoto con `git push -u origin develop`, dejándola configurada para rastrear `origin/develop`.

---

**Prompt 16:**
> ahora realiza un commit para el .gitignore @PruebaTecnicaTrycore/Prueba_Tecnica_Trycore/.gitignore

El asistente detectó el archivo `.gitignore` como untracked en la rama `develop`, lo añadió al área de staging con `git add .gitignore`, realizó el commit con el mensaje `add .gitignore` (commit `49fb1e7`) y lo publicó en el remoto con `git push`.

---

**Prompt 17:**
> Crea un cursor rules

El asistente leyó la skill `create-rule`, exploró el proyecto para entender el stack y la arquitectura, y preguntó al usuario sobre el alcance de la regla. Con la respuesta (regla general, siempre aplicada), creó el directorio `.cursor/rules/` y el archivo `project-overview.mdc` con `alwaysApply: true`. El archivo documenta el stack tecnológico completo (backend Python/FastAPI/SQLAlchemy, frontend React/TypeScript/Vite, Docker), el flujo de capas del backend, las convenciones de estilo para backend y frontend, y las reglas transversales del proyecto.

---

**Prompt 18:**
> Agrega las siguientes reglas al archivo:
>
> Consideraciones para los commits:
>
> No realizar los commits sin que yo te lo pida.
> Realiza todos los commits en español.
> Analiza cuidadosamente los cambios en cada archivo antes de hacer commit.
> Divide los cambios en varios commits lógicos (no agrupar todo en uno solo).
> Cada commit debe incluir una descripción:
> Clara y concisa.
> Breve, pero lo suficientemente descriptiva y detallada.
> Que explique qué cambios se realizaron y cuál es su objetivo.

El asistente añadió la sección **"Convenciones para commits"** al final de `.cursor/rules/project-overview.mdc`, incorporando las cinco reglas indicadas: no commitear sin solicitud explícita, mensajes siempre en español, análisis cuidadoso de cada archivo antes del commit, división en commits lógicos y cohesivos, y mensajes claros que expliquen qué se cambió y cuál es su objetivo.

---

**Prompt 19:**
> Quiero que generes un plan para lo siguiente:
>
> Estoy realizando una prueba tecnica como fullstack y necesito demostrar conocimientos en backend con FastAPI, Frontend con React, git flow y docker. ya se tiene realizado lo que esta en la siguiente ruta C:\Users\Usuario\Documents\TrycoreProjects\PruebaTecnicaTrycore\Prueba_Tecnica_Trycore

El asistente exploró el proyecto completo (backend, frontend, infraestructura, tests) y generó un plan detallado. Identificó el estado actual: dominio EVM implementado y con tests, arquitectura de capas completa, frontend cableado, pero todos los handlers de routers, servicios y repositorios con `raise NotImplementedError`. Propuso 10 pasos: ramas gitflow, repositorios, servicios, handlers, tests de integración, CRUD de proyectos en frontend, tabla EVM completa, servicio frontend en docker-compose, README.md y AI_PROCESS.md.

---

**Prompt 20:**
> para el gitflow ya se generaron las ramas main y develop, quiero crear un feature para el backend y para el Frontend, pero no se si agregar tambien la bd a backend o es mejor generar un feature diferente

El asistente recomendó **dos features** en lugar de tres: `feature/backend-api` (repositorios, servicios, routers, tests, README) y `feature/frontend-ui` (CRUD de proyectos, tabla EVM completa, servicio frontend en docker-compose). Argumentó que la BD no necesita feature propio porque `db/init/01_schema.sql` ya está escrito y no requiere cambios; simplemente viaja con el código al hacer `docker compose up`. Propuso un `feature/docs` separado para `AI_PROCESS.md`.

---

**Prompt 21:**
> Teniendo en cuenta la estructura actual que es más recomendable seguir trabajando con lo que se tiene o empezar de 0?

El asistente recomendó claramente **continuar con la estructura existente**. Argumentó que el dominio EVM, los tests unitarios, el ORM, los schemas Pydantic, los tipos TypeScript y el frontend están bien implementados y representan el 60-70% del trabajo. Los stubs (`NotImplementedError`) son la parte más mecánica: queries SQLAlchemy y handlers HTTP sin lógica compleja. Empezar de cero implicaría duplicar el esfuerzo y arriesgar perder decisiones arquitectónicas ya bien tomadas.

---

**Prompt 22:**
> quiero que para el plan antes de implementar los pasos se debe asegurar de probar cada uno de los pasos y validar que este funcionando correctamente tanto el backend como el Frontend

El asistente actualizó el plan incorporando un checkpoint de validación obligatorio después de cada paso de implementación. Estableció la regla: ningún paso avanza al siguiente sin que su validación sea exitosa. Los checkpoints incluyen: tests unitarios en verde tras los repositorios, Ruff sin errores tras los servicios, prueba de los 9 endpoints en Swagger UI tras los routers, cobertura ≥ 80% con `pytest --cov` tras los tests de integración, flujo completo en navegador tras el CRUD de proyectos, verificación manual de fórmulas EVM tras la tabla de actividades, y `docker compose up --build` con los tres servicios activos tras añadir el frontend al compose.

---

**Prompt 23:**
> genera el plan en un archivo .md en la carpeta raiz

El asistente creó el archivo `PLAN.md` en la raíz del repositorio con el plan completo: estado actual del proyecto, principio de validación continua, tabla de ramas gitflow, diagrama de flujo de datos, los 10 pasos con sus checklists de validación, las fórmulas EVM de referencia para verificación manual y el orden de ejecución recomendado.

---

**Prompt 24:**
> Vamos a realizar el siguiente plan @PLAN.md , teniendo en cuenta las reglas del archivo @.cursor/rules/project-overview.mdc

El asistente leyó el `PLAN.md` y exploró el estado actual del código (ORM, schemas, calculador EVM y sus 49 tests unitarios, stubs con `NotImplementedError` en repositorios, servicios y routers, frontend con tipos y componentes ya cableados). Ejecutó los 10 pasos del plan en orden:

1. Creó las ramas `feature/backend-api`, `feature/frontend-ui` y `feature/docs` desde `develop`.
2. Implementó `ProjectRepository` (`list_all`, `get_by_id`, `get_by_id_with_activities`, `create`, `update`, `delete`) y `ActivityRepository` (`list_by_project`, `get_by_id`, `create`, `update`, `delete`) con SQLAlchemy async y `selectinload` explícito.
3. Implementó `ProjectService` (orquestación EVM, traducción `ActivityORM → ActivityInput → EVMIndicators`, lanza `ProjectNotFoundError`) y `ActivityService` (valida pertenencia de la actividad al proyecto antes de modificar, lanza `ActivityNotInProjectError`).
4. Implementó los 9 handlers de routers con inyección de dependencias mediante `_get_service` factory; corrigió el `nginx.conf` donde el proxy apuntaba a `http://backend:8000` en lugar del nombre correcto del servicio `http://api:8000`.
5. Actualizó `conftest.py` con fixtures `_create_tables` (session-scoped), `db_session` (TRUNCATE + CASCADE para aislamiento) y `async_client` (override de `get_db_session`). Creó `test_projects.py` (15 tests) y `test_activities.py` (11 tests) cubriendo todos los endpoints, validaciones de pertenencia cross-project y verificación EVM end-to-end contra el caso canónico.
6. Refactorizó `ProjectListPage.tsx`: añadió botón "Nuevo proyecto", botones editar/eliminar por tarjeta, modal reutilizable con formulario (nombre, descripción, fecha de corte), manejo de errores del servidor visibles al usuario.
7. Amplió `ActivityTable.tsx` con columnas PV, EV, CV, SV, EAC, VAC; aplicó colores verde/rojo a varianzas y usó `cpi_label`/`spi_label` del backend como tooltip de los badges de estado.
8. Agregó el servicio `frontend` al `docker-compose.yml` (build `./frontend`, puerto 3000, `depends_on: api`); añadió `FRONTEND_PORT` al `.env.example`.
9. Creó `README.md` con descripción, prerrequisitos, instrucciones de arranque, URLs, estructura de carpetas, tabla de fórmulas EVM y lista de endpoints.
10. Creó este archivo `AI_PROCESS.md` con todas las secciones requeridas por la prueba técnica.

---

**Prompt 25:**
> ayudame a levantar el @docker-compose.yml

El asistente verificó que Docker estaba corriendo y que el `.env` ya existía. Al ejecutar `docker compose up -d --build` se detectaron tres problemas encadenados que impedían el build del servicio frontend:

1. **`npm ci` fallaba con `EUSAGE`** porque no existía `package-lock.json` en `frontend/`. Se resolvió ejecutando `npm install --package-lock-only` en la carpeta `frontend/` para generarlo sin instalar nada localmente.
2. **TypeScript no reconocía `process`, `__dirname` ni `node:path` en `vite.config.ts`** porque faltaba `@types/node`. Se añadió como `devDependency` en `package.json` y se declaró `"types": ["node"]` en `tsconfig.node.json`.
3. **TypeScript no reconocía los imports `*.module.css`** porque faltaba el archivo de referencia de Vite. Se creó `frontend/src/vite-env.d.ts` con `/// <reference types="vite/client" />`, que habilita los tipos de CSS Modules, imágenes y variables `import.meta.env`.

Tras regenerar el `package-lock.json` con la nueva dependencia, el build completó sin errores y los tres contenedores quedaron activos (`evm-database` healthy, `evm-api` healthy, `evm-frontend` up) en sus puertos configurados (5432, 8000, 3000).

---

**Prompt 26:**
> Agrega estas modificaciones que se realizaron en el README para tener en cuenta y evitar futuras fallas al momento de levantar el docker

El asistente actualizó `README.md` documentando los hallazgos del levantamiento:

- En **Prerrequisitos** se agregó Node.js ≥ 20 / npm ≥ 10 como requisito previo (solo para el paso de preparación, no para el runtime en Docker).
- Se añadió la sección **"Preparación inicial (primera vez)"** explicando que hay que generar el `package-lock.json` con `npm install --package-lock-only` antes del primer `docker compose up`, junto con la justificación técnica (`npm ci` requiere lockfile con `lockfileVersion >= 1`).
- Los pasos de **"Levantar el proyecto"** se renumeraron incorporando la generación del lockfile como paso 2 explícito.
- Se agregó la sección **"Solución de problemas comunes"** con tres entradas: error `EUSAGE` de `npm ci` (lockfile faltante), error TypeScript `Cannot find name 'process'` / `__dirname` (`@types/node` y `tsconfig.node.json`), y error `Cannot find module '*.module.css'` (`vite-env.d.ts` faltante), cada una con causa y solución concreta.

---

**Prompt 27:**
> Genera los feature con base a @PLAN.md y ten en cuen la reglas @.cursor/rules/project-overview.mdc

El asistente leyó en profundidad el `PLAN.md` y todas las reglas del proyecto. A continuación exploró sistemáticamente cada archivo del repositorio — repositorios, servicios, routers, tests de integración, conftest, páginas y componentes React, docker-compose, README y AI_PROCESS — para determinar el estado real de la implementación.

El diagnóstico fue que **todos los features del plan ya estaban completamente implementados** en el directorio de trabajo como archivos no rastreados (`??` en git). Las tres ramas de gitflow (`feature/backend-api`, `feature/frontend-ui`, `feature/docs`) también existían pero no tenían ningún commit propio. El asistente documentó el estado de cada uno de los 10 pasos del PLAN con su nivel de completitud y concluyó que lo único pendiente era organizar los commits en las ramas correspondientes según el gitflow.

---

**Prompt 28:**
> Si quiero que continues con los commits

El asistente organizó **15 commits cohesivos** distribuidos en las tres ramas de feature siguiendo estrictamente el gitflow descrito en el PLAN:

En **`feature/backend-api`** (8 commits):
1. Config base, ORM (ProjectORM, ActivityORM) y calculador EVM puro con modelos de dominio
2. Repositorios de proyectos y actividades con SQLAlchemy async
3. Servicios (ProjectService, ActivityService) más excepciones de dominio y error handlers
4. 9 endpoints HTTP, schemas Pydantic v2 y main.py con lifespan y CORS
5. Tests unitarios e integración con cobertura mínima del 80%
6. Dockerfile del backend, requirements y archivos de entorno
7. Schema SQL de PostgreSQL, .env.example raíz y reglas Cursor
8. README.md completo con instrucciones de despliegue

En **`feature/frontend-ui`** (6 commits):
1. Tipos TypeScript, cliente HTTP Axios y utilidades de formato
2. Componentes EVM reutilizables (ActivityTable, EVMSummaryCard, EVMBarChart, StatusBadge, Modal, ActivityForm)
3. Páginas ProjectListPage (CRUD completo) y ProjectDetailPage con hook useProject
4. Configuración de Vite, TypeScript, ESLint y package.json
5. Dockerfile multi-stage y configuración Nginx con proxy inverso
6. Servicio frontend incorporado al docker-compose

En **`feature/docs`** (1 commit):
1. AI_PROCESS.md y PLAN.md

---

## Cómo aprendiste EVM

**Aprendizaje EVM**

Como se puede evidenciar con el Prompt 2 y 3, fue con lo que aprendi EVM y valide el entendimiento de las formulas, eso tambien me aseguro que la IA entendiera el requerimiento y posteriormente implementara de manera correcta las formulas.

---

## Decisiones donde no segui la IA

**Problemas con la IA**

Al momento de ir generando el proyecto estaba manejando un solo chat, lo cual genero que la IA perdiera contexto de lo que se habia trabajado antes, lo cual genero que al momento de realizar la inserción a git, realizo todo el proceso de manera incorrecta donde inclusive todo archivo y carpetas que no deberia tomar.

---

## Decisión de arquitectura propia

**Docker**

Aun sin saber manejar Docker y no haber manejado, se que a la interna de Trycore se esta implementando la implementación de Docker por ende decidí agregarlo a la prueba.

---

## Decisión honesta

**Diferente si repitiera el ejercicio**

Para mi fue un reto total debido a que mi perfil esta orientado totalmente al RPA con Automation Anywhere, por lo cual no tenia los suficientes conocimientos para dicha prueba, en este momento que aprendí a manejar mejor el IDE de cursor y nuevos conocimientos por lo cual el mayor diferencial seria cuestionar un poco más a la IA y no dejarla ir tan sola para el proceso.