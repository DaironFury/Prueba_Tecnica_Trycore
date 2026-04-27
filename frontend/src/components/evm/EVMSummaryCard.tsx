import type { EVMIndicators } from "@/types/evm.types";
import { formatCurrency, formatRatio } from "@/utils/format";

import { StatusBadge } from "./StatusBadge";
import styles from "./EVMSummaryCard.module.css";

interface EVMSummaryCardProps {
  indicators: EVMIndicators;
}

interface MetricProps {
  label: string;
  value: string;
  hint?: string;
}

function Metric({ label, value, hint }: MetricProps) {
  return (
    <div className={styles.metric}>
      <div className={styles.metricLabel}>{label}</div>
      <div className={styles.metricValue}>{value}</div>
      {hint && <div className={styles.metricHint}>{hint}</div>}
    </div>
  );
}

export function EVMSummaryCard({ indicators }: EVMSummaryCardProps) {
  return (
    <div className={styles.container}>
      <div className={styles.absoluteRow}>
        <Metric label="BAC" value={formatCurrency(indicators.bac)} />
        <Metric label="PV" value={formatCurrency(indicators.pv)} />
        <Metric label="EV" value={formatCurrency(indicators.ev)} />
        <Metric label="AC" value={formatCurrency(indicators.ac)} />
      </div>

      <div className={styles.indicesRow}>
        <div className={styles.indexCard}>
          <div className={styles.indexHeader}>
            <span className={styles.indexCode}>CPI</span>
            <StatusBadge
              status={indicators.cpi_status}
              label={indicators.cpi_label}
            />
          </div>
          <div className={styles.indexValue}>{formatRatio(indicators.cpi)}</div>
        </div>

        <div className={styles.indexCard}>
          <div className={styles.indexHeader}>
            <span className={styles.indexCode}>SPI</span>
            <StatusBadge
              status={indicators.spi_status}
              label={indicators.spi_label}
            />
          </div>
          <div className={styles.indexValue}>{formatRatio(indicators.spi)}</div>
        </div>
      </div>

      <div className={styles.projectionRow}>
        <Metric
          label="EAC"
          value={formatCurrency(indicators.eac)}
          hint="Costo proyectado al final"
        />
        <Metric
          label="VAC"
          value={formatCurrency(indicators.vac)}
          hint="Variación al final"
        />
        <Metric
          label="CV"
          value={formatCurrency(indicators.cv)}
          hint="Cost Variance"
        />
        <Metric
          label="SV"
          value={formatCurrency(indicators.sv)}
          hint="Schedule Variance"
        />
      </div>
    </div>
  );
}
