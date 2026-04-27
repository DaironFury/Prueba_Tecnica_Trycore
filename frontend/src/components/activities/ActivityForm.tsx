import { type FormEvent, useState } from "react";

import type { Activity, ActivityCreatePayload } from "@/types/activity.types";

import styles from "./ActivityForm.module.css";

interface ActivityFormProps {
  initialActivity?: Activity;
  onSubmit: (payload: ActivityCreatePayload) => Promise<void> | void;
  onCancel: () => void;
}

interface FormValues {
  name: string;
  bac: string;
  planned_percent: string;
  actual_percent: string;
  actual_cost: string;
}

function toFormValues(activity?: Activity): FormValues {
  return {
    name: activity?.name ?? "",
    bac: activity?.bac.toString() ?? "",
    planned_percent: activity?.planned_percent.toString() ?? "",
    actual_percent: activity?.actual_percent.toString() ?? "",
    actual_cost: activity?.actual_cost.toString() ?? "",
  };
}

function toPayload(values: FormValues): ActivityCreatePayload {
  return {
    name: values.name.trim(),
    bac: Number(values.bac),
    planned_percent: Number(values.planned_percent),
    actual_percent: Number(values.actual_percent),
    actual_cost: Number(values.actual_cost),
  };
}

export function ActivityForm({
  initialActivity,
  onSubmit,
  onCancel,
}: ActivityFormProps) {
  const [values, setValues] = useState<FormValues>(toFormValues(initialActivity));
  const [submitting, setSubmitting] = useState(false);
  const isEditing = Boolean(initialActivity);

  function handleChange<K extends keyof FormValues>(field: K, value: string) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(toPayload(values));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <h2 className={styles.title}>
        {isEditing ? "Editar actividad" : "Nueva actividad"}
      </h2>

      <label className={styles.field}>
        <span>Nombre</span>
        <input
          type="text"
          required
          maxLength={255}
          value={values.name}
          onChange={(e) => handleChange("name", e.target.value)}
        />
      </label>

      <div className={styles.row}>
        <label className={styles.field}>
          <span>BAC (presupuesto total)</span>
          <input
            type="number"
            min={0}
            step={0.01}
            required
            value={values.bac}
            onChange={(e) => handleChange("bac", e.target.value)}
          />
        </label>

        <label className={styles.field}>
          <span>AC (costo real)</span>
          <input
            type="number"
            min={0}
            step={0.01}
            required
            value={values.actual_cost}
            onChange={(e) => handleChange("actual_cost", e.target.value)}
          />
        </label>
      </div>

      <div className={styles.row}>
        <label className={styles.field}>
          <span>% planificado</span>
          <input
            type="number"
            min={0}
            max={100}
            step={0.01}
            required
            value={values.planned_percent}
            onChange={(e) => handleChange("planned_percent", e.target.value)}
          />
        </label>

        <label className={styles.field}>
          <span>% real</span>
          <input
            type="number"
            min={0}
            max={100}
            step={0.01}
            required
            value={values.actual_percent}
            onChange={(e) => handleChange("actual_percent", e.target.value)}
          />
        </label>
      </div>

      <div className={styles.actions}>
        <button
          type="button"
          className="btn"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={submitting}
        >
          {submitting ? "Guardando..." : isEditing ? "Actualizar" : "Crear"}
        </button>
      </div>
    </form>
  );
}
