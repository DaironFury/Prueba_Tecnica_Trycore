import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  createActivity,
  deleteActivity,
  updateActivity,
} from "@/api/activities.api";
import { ActivityForm } from "@/components/activities/ActivityForm";
import { ActivityTable } from "@/components/activities/ActivityTable";
import { Modal } from "@/components/Modal";
import { EVMBarChart } from "@/components/evm/EVMBarChart";
import { EVMSummaryCard } from "@/components/evm/EVMSummaryCard";
import { useProject } from "@/hooks/useProject";
import type {
  Activity,
  ActivityCreatePayload,
} from "@/types/activity.types";

import styles from "./ProjectDetailPage.module.css";

type ModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; activity: Activity };

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { project, loading, error, refetch } = useProject(projectId);
  const [modal, setModal] = useState<ModalState>({ mode: "closed" });

  if (loading) {
    return (
      <main className="app-shell">
        <div className="empty-state">Cargando proyecto...</div>
      </main>
    );
  }

  if (error || !project) {
    return (
      <main className="app-shell">
        <div className={styles.error}>
          {error?.message ?? "Proyecto no encontrado"}
        </div>
        <Link to="/projects" className="btn">
          Volver a proyectos
        </Link>
      </main>
    );
  }

  async function handleCreate(payload: ActivityCreatePayload) {
    await createActivity(project!.id, payload);
    setModal({ mode: "closed" });
    await refetch();
  }

  async function handleUpdate(
    activityId: string,
    payload: ActivityCreatePayload,
  ) {
    await updateActivity(project!.id, activityId, payload);
    setModal({ mode: "closed" });
    await refetch();
  }

  async function handleDelete(activity: Activity) {
    const confirmed = window.confirm(
      `¿Eliminar la actividad "${activity.name}"?`,
    );
    if (!confirmed) return;
    await deleteActivity(project!.id, activity.id);
    await refetch();
  }

  return (
    <main className="app-shell">
      <header className={styles.header}>
        <Link to="/projects" className={styles.backLink}>
          ← Volver
        </Link>
        <h1 className={styles.title}>{project.name}</h1>
        <p className={styles.subtitle}>
          Fecha de corte: {project.status_date} · {project.activities.length}{" "}
          {project.activities.length === 1 ? "actividad" : "actividades"}
        </p>
        {project.description && (
          <p className={styles.description}>{project.description}</p>
        )}
      </header>

      <h2 className="section-title">Resumen del proyecto</h2>
      <EVMSummaryCard indicators={project.indicators} />

      <h2 className="section-title">PV vs EV vs AC por actividad</h2>
      <EVMBarChart activities={project.activities} />

      <div className={styles.activitiesHeader}>
        <h2 className="section-title" style={{ margin: 0 }}>
          Actividades
        </h2>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setModal({ mode: "create" })}
        >
          + Nueva actividad
        </button>
      </div>

      <ActivityTable
        activities={project.activities}
        onEdit={(activity) => setModal({ mode: "edit", activity })}
        onDelete={(activity) => void handleDelete(activity)}
      />

      <Modal
        open={modal.mode !== "closed"}
        onClose={() => setModal({ mode: "closed" })}
      >
        {modal.mode === "create" && (
          <ActivityForm
            onSubmit={handleCreate}
            onCancel={() => setModal({ mode: "closed" })}
          />
        )}
        {modal.mode === "edit" && (
          <ActivityForm
            initialActivity={modal.activity}
            onSubmit={(payload) => handleUpdate(modal.activity.id, payload)}
            onCancel={() => setModal({ mode: "closed" })}
          />
        )}
      </Modal>
    </main>
  );
}
