# AI_PROCESS.md — Proceso de desarrollo con IA

## Herramientas de IA utilizadas y por qué

**Cursor IDE con Claude Sonnet (Anthropic)**
Cursor es un editor de código que integra modelos de lenguaje directamente en el flujo de trabajo de programación. Elegí Claude Sonnet porque tiene razonamiento contextual fuerte para mantener consistencia arquitectónica a lo largo de una base de código grande, lo que en este proyecto fue clave: necesitaba que el asistente entendiera la separación en capas (Router → Service → Repository → Domain) y la respetara en cada archivo que generaba.

Usé Cursor en modo **Agent** (no solo chat), lo que le permite leer archivos del proyecto, hacer búsquedas, escribir código y ejecutar comandos. Esto permite iterar mucho más rápido que copiar-pegar entre un chat externo y el editor.

---

## Prompts enviados (cronológicos)

### Sesión principal

**Prompt 1:**
> "Vamos a realizar el siguiente plan @PLAN.md , teniendo en cuenta las reglas del archivo @.cursor/rules/project-overview.mdc"

Este fue el prompt inicial que disparó toda la implementación. No hubo prompts anteriores en esta sesión porque el esqueleto del proyecto ya estaba creado previamente con los stubs `raise NotImplementedError`.

El agente leyó el `PLAN.md`, exploró los archivos existentes (ORM, schemas, dominio puro, calculador EVM, tests unitarios) y ejecutó los 10 pasos del plan en orden:

1. Crear ramas Gitflow (`feature/backend-api`, `feature/frontend-ui`, `feature/docs`)
2. Implementar `ProjectRepository` y `ActivityRepository` con SQLAlchemy async
3. Implementar `ProjectService` y `ActivityService` con orquestación EVM
4. Implementar los 9 handlers de routers con inyección de dependencias
5. Escribir tests de integración con fixtures de BD real (PostgreSQL + TRUNCATE)
6. Refactorizar `ProjectListPage` con CRUD completo (modal de crear/editar/eliminar)
7. Ampliar `ActivityTable` con columnas PV, EV, CV, SV, EAC, VAC
8. Agregar el servicio `frontend` a `docker-compose.yml`
9. Escribir `README.md`
10. Escribir este documento `AI_PROCESS.md`

---

## Cómo aprendí EVM

Antes de este proyecto mi conocimiento sobre Earned Value Management era superficial. El aprendizaje ocurrió en tres capas:

**Capa conceptual:** Leí la descripción del problema técnico (`PruebaTecnica.txt`). La frase clave fue: *"Un proyecto puede haber gastado el 60% del presupuesto habiendo completado solo el 40% del trabajo — y eso es una señal de alerta"*. Eso me dio el modelo mental: EVM relaciona lo que debería haberse gastado con lo que realmente se avanzó.

**Capa matemática:** Las ocho fórmulas de la tabla (PV, EV, CV, SV, CPI, SPI, EAC, VAC) son algebraicamente simples. El insight más importante es que los índices CPI y SPI **no son independientes de escala**: un proyecto grande en problemas no puede quedar enmascarado por uno pequeño eficiente. Por eso los indicadores del proyecto se calculan sumando valores absolutos (total\_ev / total\_ac), no promediando los CPI individuales.

**Capa de casos borde:** El calculador puro (`evm_calculator.py`) y sus tests me mostraron los casos no triviales: AC = 0 deja CPI indefinido (no Infinity), planned\_percent = 0 deja SPI indefinido, CPI = 0 hace EAC indefinido. El uso de `None` en vez de `Infinity` o `NaN` es una decisión deliberada para que el JSON sea siempre parseable.

---

## Cómo validué las fórmulas

La validación ocurrió en dos niveles:

**Nivel unitario (ya existía):** El archivo `tests/unit/test_evm_calculator.py` contiene 460 líneas con 25+ casos de prueba. Incluye:
- Casos canónicos con valores resueltos a mano (BAC=10.000, planned=60%, actual=40%, AC=5.500 → PV=6.000, EV=4.000, CV=-1.500...)
- Casos borde (AC=0, planned\_percent=0, todo en cero)
- Propiedades algebraicas (EAC × CPI = BAC, EAC + VAC = BAC, escalado lineal)

**Nivel de integración:** En `tests/integration/test_projects.py`, el test `TestEVMCalculationIntegration.test_evm_after_activity_creation` crea un proyecto + actividad vía HTTP y verifica los indicadores contra los mismos valores del caso canónico, cerrando el ciclo end-to-end.

---

## Dos decisiones donde no seguí a la IA

### Decisión 1: No usar aiosqlite para los tests de integración

El patrón más común en tutoriales de FastAPI testing es usar SQLite en memoria con `aiosqlite` para los tests de integración, porque evita la dependencia de PostgreSQL en CI. El asistente consideró este approach.

Decidí no hacerlo por una razón técnica concreta: el ORM usa `PG_UUID(as_uuid=True)` (tipo UUID nativo de PostgreSQL) y columnas `Numeric(15, 2)`. SQLite maneja estas columnas de manera diferente, lo que podría producir tests que pasan en SQLite pero fallan en PostgreSQL real (precisión decimal, casting de UUID). Preferí tests que fallan honestamente cuando la BD no está disponible a tests que pasan artificialmente.

El tradeoff: los tests de integración requieren `docker compose up -d database` para correr. Acepté ese costo a cambio de mayor fidelidad.

### Decisión 2: Usar `TRUNCATE` entre tests en lugar de savepoints/rollback

La técnica "clásica" para aislamiento en tests async con SQLAlchemy es usar `begin_nested()` (savepoints) o transacciones que se revierten al final de cada test. Con `asyncpg`, implementar esto correctamente es complejo porque el driver no soporta exactamente el mismo protocolo de savepoints que `psycopg2`.

Decidí usar `TRUNCATE activities, projects CASCADE` antes de cada test. Es ligeramente más lento (DDL + datos) pero:
- Es explícito y comprensible para cualquier desarrollador que lea el conftest
- No tiene bugs ocultos de commit/rollback inesperado
- Funciona de forma idéntica en cualquier versión del driver

---

## Cómo verifiqué los cálculos

1. **Verificación algebraica manual:** Para el caso canónico (BAC=10.000, planned=60%, actual=40%, AC=5.500) calculé a mano cada indicador y los usé como assertions en los tests unitarios y de integración.

2. **Propiedades algebraicas como invariantes:** En lugar de solo testear números específicos, los tests verifican propiedades que deben cumplirse para *cualquier* entrada válida:
   - `EAC × CPI = BAC` (si CPI ≠ None)
   - `EAC + VAC = BAC`
   - Escalar BAC y AC por k deja CPI y SPI sin cambio (linealidad)
   - CV > 0 ↔ CPI > 1 (coherencia de signos)

3. **Verificación de que la agregación es correcta:** El test `test_indices_son_ponderados_no_promediados` verifica explícitamente que una actividad pequeña con buen CPI no enmascara a una grande con problemas — esto es el error conceptual más común en implementaciones EVM.

---

## Una decisión de arquitectura independiente

**Separación de los indicadores EVM fuera del ORM (no se persisten)**

La decisión más importante fue no guardar PV, EV, CPI, SPI, EAC, VAC en la base de datos. Los cinco campos de entrada (BAC, planned\_percent, actual\_percent, AC, nombre) son la **única fuente de verdad**. Los indicadores se recalculan en cada lectura.

Motivaciones:
- **Consistencia garantizada:** Nunca puede haber un estado donde los indicadores almacenados no corresponden a los campos de entrada (el clásico bug de "cache stale").
- **Cero migración:** Si las fórmulas EVM cambian (hipotético), no hay que migrar columnas calculadas.
- **Dominio puro testeable:** El calculador `evm_calculator.py` no tiene ninguna dependencia de persistencia. Sus tests corren en microsegundos sin BD.

El único costo es recalcular en cada GET. Para el volumen esperado (decenas de actividades por proyecto), este costo es insignificante.

---

## Reflexión final

El mayor aprendizaje no fue sobre EVM ni sobre el stack tecnológico — fue sobre **el rol del asistente de IA en el proceso de ingeniería**.

El asistente es muy efectivo para tareas donde la forma correcta está bien definida: implementar un repositorio SQLAlchemy, escribir fixtures de pytest, estructurar un modal React. En esas tareas, el asistente ahorra horas de tipeo y búsqueda de documentación.

El asistente es menos confiable cuando la decisión requiere contexto de negocio o tradeoffs no evidentes en el código. Las dos decisiones documentadas arriba (tests contra PostgreSQL real, TRUNCATE vs savepoints) surgieron de pensar en las consecuencias a mediano plazo, no de lo que el asistente sugería por defecto.

La habilidad que realmente importa no es escribir prompts perfectos, sino saber **cuándo confiar en la sugerencia y cuándo cuestionarla**. Eso requiere entender el problema lo suficientemente bien como para evaluar la respuesta — y eso no lo reemplaza ningún modelo de lenguaje.
