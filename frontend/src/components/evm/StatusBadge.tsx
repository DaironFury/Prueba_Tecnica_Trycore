import type { CSSProperties } from "react";

import type { EVMStatus } from "@/types/evm.types";
import { STATUS_VISUALS } from "@/utils/statusColors";

import styles from "./StatusBadge.module.css";

interface StatusBadgeProps {
  status: EVMStatus;
  label: string;
  compact?: boolean;
}

/**
 * Visual semáforo for CPI/SPI. Always renders the label alongside the
 * color so the indicator is intelligible to colorblind users.
 */
export function StatusBadge({ status, label, compact = false }: StatusBadgeProps) {
  const visual = STATUS_VISUALS[status];
  const style: CSSProperties = {
    color: visual.color,
    backgroundColor: visual.background,
  };

  return (
    <span
      className={`${styles.badge} ${compact ? styles.compact : ""}`}
      style={style}
      role="status"
      aria-label={label}
    >
      <span className={styles.dot} style={{ backgroundColor: visual.color }} />
      {label}
    </span>
  );
}
