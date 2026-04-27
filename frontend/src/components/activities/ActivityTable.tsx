import type { Activity } from "@/types/activity.types";
import { formatCurrency, formatPercent, formatRatio } from "@/utils/format";

import { StatusBadge } from "../evm/StatusBadge";
import styles from "./ActivityTable.module.css";

interface ActivityTableProps {
  activities: Activity[];
  onEdit: (activity: Activity) => void;
  onDelete: (activity: Activity) => void;
}

export function ActivityTable({ activities, onEdit, onDelete }: ActivityTableProps) {
  if (activities.length === 0) {
    return (
      <div className={styles.empty}>
        Este proyecto aún no tiene actividades registradas.
      </div>
    );
  }

  return (
    <div className={styles.tableWrapper}>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th className={styles.numeric}>BAC</th>
            <th className={styles.numeric}>% Plan</th>
            <th className={styles.numeric}>% Real</th>
            <th className={styles.numeric}>AC</th>
            <th className={styles.numeric}>PV</th>
            <th className={styles.numeric}>EV</th>
            <th className={styles.numeric}>CV</th>
            <th className={styles.numeric}>SV</th>
            <th className={styles.numeric}>EAC</th>
            <th className={styles.numeric}>VAC</th>
            <th className={styles.numeric}>CPI</th>
            <th className={styles.numeric}>SPI</th>
            <th className={styles.actions}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {activities.map((activity) => {
            const { indicators } = activity;
            return (
              <tr key={activity.id}>
                <td>
                  <div className={styles.nameCell}>{activity.name}</div>
                </td>
                <td className={styles.numeric}>{formatCurrency(activity.bac)}</td>
                <td className={styles.numeric}>{formatPercent(activity.planned_percent)}</td>
                <td className={styles.numeric}>{formatPercent(activity.actual_percent)}</td>
                <td className={styles.numeric}>{formatCurrency(activity.actual_cost)}</td>
                <td className={styles.numeric}>{formatCurrency(indicators.pv)}</td>
                <td className={styles.numeric}>{formatCurrency(indicators.ev)}</td>
                <td className={`${styles.numeric} ${indicators.cv < 0 ? styles.negative : styles.positive}`}>
                  {formatCurrency(indicators.cv)}
                </td>
                <td className={`${styles.numeric} ${indicators.sv < 0 ? styles.negative : styles.positive}`}>
                  {formatCurrency(indicators.sv)}
                </td>
                <td className={styles.numeric}>{formatCurrency(indicators.eac)}</td>
                <td className={`${styles.numeric} ${indicators.vac !== null && indicators.vac < 0 ? styles.negative : styles.positive}`}>
                  {formatCurrency(indicators.vac)}
                </td>
                <td className={styles.numeric}>
                  <div className={styles.indexCell}>
                    <span>{formatRatio(indicators.cpi)}</span>
                    <StatusBadge
                      status={indicators.cpi_status}
                      label={indicators.cpi_label}
                      compact
                    />
                  </div>
                </td>
                <td className={styles.numeric}>
                  <div className={styles.indexCell}>
                    <span>{formatRatio(indicators.spi)}</span>
                    <StatusBadge
                      status={indicators.spi_status}
                      label={indicators.spi_label}
                      compact
                    />
                  </div>
                </td>
                <td className={styles.actions}>
                  <button
                    className="btn"
                    type="button"
                    onClick={() => onEdit(activity)}
                    aria-label={`Editar ${activity.name}`}
                  >
                    Editar
                  </button>
                  <button
                    className="btn btn-danger"
                    type="button"
                    onClick={() => onDelete(activity)}
                    aria-label={`Eliminar ${activity.name}`}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
