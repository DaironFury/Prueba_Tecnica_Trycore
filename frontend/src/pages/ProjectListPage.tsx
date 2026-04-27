import { type FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError } from "@/api/client";
import {
  createProject,
  deleteProject,
  fetchProjects,
  updateProject,
} from "@/api/projects.api";
import { Modal } from "@/components/Modal";
import type { ProjectCreatePayload, ProjectSummary } from "@/types/project.types";

import styles from "./ProjectListPage.module.css";

interface ProjectFormValues {
  name: string;
  description: string;
  status_date: string;
}

const EMPTY_FORM: ProjectFormValues = { name: "", description: "", status_date: "" };

function toFormValues(project: ProjectSummary): ProjectFormValues {
  return {
    name: project.name,
    description: project.description ?? "",
    status_date: project.status_date,
  };
}

function toPayload(values: ProjectFormValues): ProjectCreatePayload {
  return {
    name: values.name.trim(),
    description: values.description.trim() || undefined,
    status_date: values.status_date,
  };
}

export function ProjectListPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal de crear/editar
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<ProjectSummary | null>(null);
  const [formValues, setFormValues] = useState<ProjectFormValues>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al cargar proyectos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  function openCreateModal() {
    setEditingProject(null);
    setFormValues(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  }

  function openEditModal(project: ProjectSummary, event: React.MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    setEditingProject(project);
    setFormValues(toFormValues(project));
    setFormError(null);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingProject(null);
    setFormValues(EMPTY_FORM);
    setFormError(null);
  }

  async function handleFormSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      const payload = toPayload(formValues);
      if (editingProject) {
        await updateProject(editingProject.id, payload);
      } else {
        await createProject(payload);
      }
      closeModal();
      await loadProjects();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Error al guardar el proyecto");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(project: ProjectSummary, event: React.MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    if (!confirm(`¿Eliminar el proyecto "${project.name}"? Esta acción no se puede deshacer.`)) {
      return;
    }
    try {
      await deleteProject(project.id);
      await loadProjects();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al eliminar el proyecto");
    }
  }

  function handleFieldChange(field: keyof ProjectFormValues, value: string) {
    setFormValues((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <main className="app-shell">
      <header className={styles.header}>
        <h1 className={styles.title}>Proyectos</h1>
        <button className="btn btn-primary" onClick={openCreateModal}>
          + Nuevo proyecto
        </button>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      {loading && <div className="empty-state">Cargando proyectos...</div>}

      {!loading && !error && projects.length === 0 && (
        <div className="empty-state">
          No hay proyectos. Crea uno para empezar.
        </div>
      )}

      <div className={styles.grid}>
        {projects.map((project) => (
          <div key={project.id} className={`card ${styles.projectCard}`}>
            <Link to={`/projects/${project.id}`} className={styles.cardLink}>
              <h3 className={styles.projectName}>{project.name}</h3>
              <p className={styles.projectMeta}>
                {project.activity_count} actividades · Corte {project.status_date}
              </p>
              {project.description && (
                <p className={styles.projectDescription}>{project.description}</p>
              )}
            </Link>
            <div className={styles.cardActions}>
              <button
                className="btn"
                onClick={(e) => openEditModal(project, e)}
                title="Editar proyecto"
              >
                Editar
              </button>
              <button
                className="btn btn-danger"
                onClick={(e) => void handleDelete(project, e)}
                title="Eliminar proyecto"
              >
                Eliminar
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal open={modalOpen} onClose={closeModal}>
        <form className={styles.form} onSubmit={(e) => void handleFormSubmit(e)}>
          <h2 className={styles.formTitle}>
            {editingProject ? "Editar proyecto" : "Nuevo proyecto"}
          </h2>

          {formError && <div className={styles.formError}>{formError}</div>}

          <label className={styles.field}>
            <span>Nombre *</span>
            <input
              type="text"
              required
              maxLength={255}
              value={formValues.name}
              onChange={(e) => handleFieldChange("name", e.target.value)}
              autoFocus
            />
          </label>

          <label className={styles.field}>
            <span>Descripción</span>
            <textarea
              rows={3}
              value={formValues.description}
              onChange={(e) => handleFieldChange("description", e.target.value)}
              placeholder="Descripción opcional del proyecto"
            />
          </label>

          <label className={styles.field}>
            <span>Fecha de corte *</span>
            <input
              type="date"
              required
              value={formValues.status_date}
              onChange={(e) => handleFieldChange("status_date", e.target.value)}
            />
          </label>

          <div className={styles.formActions}>
            <button type="button" className="btn" onClick={closeModal} disabled={submitting}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Guardando..." : editingProject ? "Actualizar" : "Crear"}
            </button>
          </div>
        </form>
      </Modal>
    </main>
  );
}
