-- =====================================================================
-- EVM Dashboard — esquema inicial
-- ---------------------------------------------------------------------
-- Aplicado automáticamente por la imagen oficial de postgres en el PRIMER
-- arranque del contenedor (cuando /var/lib/postgresql/data está vacío).
-- NO se vuelve a ejecutar en reinicios posteriores, preservando los datos.
--
-- Las sentencias usan IF NOT EXISTS / OR REPLACE para ser idempotentes
-- si alguna vez se ejecutan manualmente.
-- =====================================================================

-- pgcrypto provee gen_random_uuid(); estándar en imágenes Postgres 13+.
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ---------------------------------------------------------------------
-- projects (proyectos)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(255) NOT NULL,
    description   TEXT,
    status_date   DATE         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


-- ---------------------------------------------------------------------
-- activities (actividades)
-- ---------------------------------------------------------------------
-- Solo se persisten los cinco campos de entrada del EVM (BAC, %planificado,
-- %real, AC, project_id). Todos los indicadores derivados (PV, EV, CV, SV,
-- CPI, SPI, EAC, VAC) se calculan en cada lectura para que la base de datos
-- nunca diverja de las fórmulas implementadas en app/domain/evm_calculator.py.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activities (
    id               UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       UUID           NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name             VARCHAR(255)   NOT NULL,
    bac              NUMERIC(15, 2) NOT NULL,
    planned_percent  NUMERIC(5, 2)  NOT NULL,
    actual_percent   NUMERIC(5, 2)  NOT NULL,
    actual_cost      NUMERIC(15, 2) NOT NULL,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_bac_non_negative          CHECK (bac >= 0),
    CONSTRAINT chk_actual_cost_non_negative  CHECK (actual_cost >= 0),
    CONSTRAINT chk_planned_percent_range     CHECK (planned_percent BETWEEN 0 AND 100),
    CONSTRAINT chk_actual_percent_range      CHECK (actual_percent  BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_activities_project_id
    ON activities(project_id);


-- ---------------------------------------------------------------------
-- Trigger de updated_at
-- ---------------------------------------------------------------------
-- SQLAlchemy actualiza updated_at mediante `onupdate=func.now()`, pero
-- también se aplica a nivel de BD para que cualquier UPDATE manual
-- (p.ej. via psql) mantenga la columna actualizada correctamente.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_projects_updated_at ON projects;
CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_activities_updated_at ON activities;
CREATE TRIGGER trg_activities_updated_at
    BEFORE UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
