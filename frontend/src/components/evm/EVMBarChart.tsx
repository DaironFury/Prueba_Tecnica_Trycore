import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Activity } from "@/types/activity.types";

import styles from "./EVMBarChart.module.css";

interface EVMBarChartProps {
  activities: Activity[];
}

interface ChartDatum {
  name: string;
  PV: number;
  EV: number;
  AC: number;
}

const COLORS = {
  PV: "#1d4ed8",
  EV: "#15803d",
  AC: "#b91c1c",
};

const CHART_HEIGHT_PX = 320;

function buildChartData(activities: Activity[]): ChartDatum[] {
  return activities.map((activity) => ({
    name: activity.name,
    PV: activity.indicators.pv,
    EV: activity.indicators.ev,
    AC: activity.indicators.ac,
  }));
}

export function EVMBarChart({ activities }: EVMBarChartProps) {
  if (activities.length === 0) {
    return (
      <div className={styles.empty}>
        Agrega actividades para ver la comparación PV / EV / AC.
      </div>
    );
  }

  const data = buildChartData(activities);

  return (
    <div className={styles.container}>
      <ResponsiveContainer width="100%" height={CHART_HEIGHT_PX}>
        <BarChart data={data} margin={{ top: 16, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number) =>
              new Intl.NumberFormat("es-CO").format(value)
            }
          />
          <Legend />
          <Bar dataKey="PV" fill={COLORS.PV} radius={[4, 4, 0, 0]} />
          <Bar dataKey="EV" fill={COLORS.EV} radius={[4, 4, 0, 0]} />
          <Bar dataKey="AC" fill={COLORS.AC} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
